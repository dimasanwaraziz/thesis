"""
Simulation of Katandawa & Barmawi (2020),
"Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding",
Journal of Information Hiding and Multimedia Signal Processing 11(1), 14-43.

"Eq. N", "Algorithm N", "Theorem N" and "Section N" refer to the paper.

Pipeline (Fig. 3):
    secret image -> bits -> RM(1,4) encode -> Key Trace (if E_T > 3/4 HW)
                 -> Em bits into LSB of BBS-random cover pixels (modulus function, n=1)
                 -> Key Trace into agreed image (modulus function, n = ceil/floor(nn))
    key text (seed, Nc, H0, W0) -> (2,2) VCS -> Share 1 (secure channel)
                                            -> Share 2, RM-encoded, into the stego tail
"""
import math
from dataclasses import dataclass

import numpy as np


# --------------------------------------------------------------------------
# Reed-Muller RM(1, m)  (Section 2)
# --------------------------------------------------------------------------
class RM1:
    """First-order Reed-Muller code with majority-logic decoding."""

    def __init__(self, m=4):
        self.m = m
        self.k = m + 1                    # Eq. 1 with r = 1
        self.N = 2 ** m                   # Eq. 2
        self.dmin = 2 ** (m - 1)          # Eq. 3
        self.t = (self.dmin - 1) // 2     # Eq. 4
        # Same row layout as G_{1,4} printed in the paper:
        # row i = bit (m-1-i) of the column index, last row = all ones.
        cols = np.arange(self.N)
        rows = [(cols >> (m - 1 - i)) & 1 for i in range(m)]
        rows.append(np.ones(self.N, dtype=np.int64))
        self.G = np.array(rows, dtype=np.uint8)

    def encode(self, msg_blocks):
        """(n, k) message bits -> (n, N) codewords, c = u * G (Eq. 7)."""
        return ((msg_blocks.astype(np.int64) @ self.G) % 2).astype(np.uint8)

    def decode(self, codewords):
        """(n, N) received words -> (n, k) message bits (Section 2.3)."""
        c = codewords.astype(np.uint8)
        msg = np.zeros((c.shape[0], self.k), dtype=np.uint8)
        cols = np.arange(self.N)
        # Every u_i has N/2 independent check sums c_j + c_{j xor 2^b};
        # the majority wins, so up to t errors are corrected.
        for i in range(self.m):
            b = self.m - 1 - i
            lo = cols[((cols >> b) & 1) == 0]
            hi = lo | (1 << b)
            votes = (c[:, lo] ^ c[:, hi]).sum(axis=1)
            msg[:, i] = votes > self.N // 4
        # Remove the decoded part (Eq. 14); the remainder votes for u_0.
        partial = (msg[:, :self.m].astype(np.int64) @ self.G[:self.m]) % 2
        residual = c ^ partial.astype(np.uint8)
        msg[:, self.m] = residual.sum(axis=1) > self.N // 2
        return msg


def to_blocks(bits, k):
    """Split bits into k-bit blocks, zero-padding the last one (Definition 4.2).

    The number of padding bits is n*k - Y, as in the worked example of the
    paper (Eq. 29 prints Y mod k, which does not match that example).
    """
    n = math.ceil(len(bits) / k)
    padded = np.zeros(n * k, dtype=np.uint8)
    padded[:len(bits)] = bits
    return padded.reshape(n, k)


def rm_encode_bits(bits, rm):
    return rm.encode(to_blocks(bits, rm.k)).ravel()


def rm_decode_bits(bits, rm, n_out):
    return rm.decode(bits.reshape(-1, rm.N)).ravel()[:n_out]


def image_to_bits(img):
    """Section 4.1.1 step 1: every pixel becomes 8 bits (MSB first)."""
    return np.unpackbits(img.astype(np.uint8).ravel())


def bits_to_image(bits, h, w):
    """Section 4.2.7: every 8 bits become one pixel."""
    return np.packbits(bits[:8 * h * w]).reshape(h, w)


# --------------------------------------------------------------------------
# Modulus function (Thien & Lin 2003, Section 3.1)
# --------------------------------------------------------------------------
def modulus_embed(pixels, values, n):
    """Hide `values` in the n low-order bits of `pixels` (Eq. 16-18).

    `n` may be a scalar or a per-pixel array (the agreed image mixes
    ceil(nn) and floor(nn) bits per pixel).
    """
    x = pixels.astype(np.int64)
    z = values.astype(np.int64)
    n = np.broadcast_to(np.asarray(n, dtype=np.int64), x.shape)
    mod = np.left_shift(1, n)
    dd = z - x % mod                                          # Eq. 16
    lo = (mod - 1) // 2                                       # floor((2^n - 1) / 2)
    hi = mod // 2                                             # ceil((2^n - 1) / 2)
    dd = np.where(dd < -lo, dd + mod, np.where(dd > hi, dd - mod, dd))   # Eq. 17
    xp = x + dd
    xp = np.where(xp < 0, xp + mod, np.where(xp > 255, xp - mod, xp))    # Eq. 18
    return xp.astype(np.uint8)


def modulus_extract(pixels, n):
    """z = x' mod 2^n (Eq. 19)."""
    n = np.asarray(n, dtype=np.int64)
    return pixels.astype(np.int64) % np.left_shift(1, n)


# --------------------------------------------------------------------------
# Blum Blum Shub random pixel positions (Section 4.1.3)
# --------------------------------------------------------------------------
BBS_P = 1000003   # prime, = 3 (mod 4)
BBS_Q = 1000039   # prime, = 3 (mod 4)

_position_cache = {}


class BlumBlumShub:
    """x_{i+1} = x_i^2 mod M, M = p*q; outputs the LSB of every state."""

    def __init__(self, seed, p=BBS_P, q=BBS_Q):
        self.M = p * q
        if seed <= 1 or math.gcd(seed, self.M) != 1:
            raise ValueError("BBS seed must be > 1 and coprime with p*q")
        self.x = seed * seed % self.M

    def next_int(self, nbits):
        value = 0
        x, M = self.x, self.M
        for _ in range(nbits):
            x = x * x % M
            value = (value << 1) | (x & 1)
        self.x = x
        return value


def random_positions(seed, count, pool):
    """`count` distinct pixel indices in [0, pool) drawn from BBS.

    The paper groups BBS bits into 18-bit integers (2^18 = 512*512). Here the
    group width is ceil(log2(pool)); out-of-range and repeated values are
    skipped so that no pixel is embedded twice.
    """
    key = (seed, count, pool)
    if key in _position_cache:
        return _position_cache[key]
    if count > pool:
        raise ValueError("not enough pixels for the requested positions")
    nbits = max(1, (pool - 1).bit_length())
    gen = BlumBlumShub(seed)
    used = bytearray(pool)
    out = np.empty(count, dtype=np.int64)
    i = 0
    while i < count:
        v = gen.next_int(nbits)
        if v < pool and not used[v]:
            used[v] = 1
            out[i] = v
            i += 1
    _position_cache[key] = out
    return out


# --------------------------------------------------------------------------
# Key Trace: the "multiple embedding" (Section 4.1.2, Algorithms 1 and 2)
# --------------------------------------------------------------------------
@dataclass
class CycleLayout:
    ET: int        # encoded bits
    P: int         # usable cover pixels = 3/4 * H1 * W1
    Nc: float      # Eq. 31
    ceil_nc: int
    floor_nc: int
    h: int         # pixels holding ceil(Nc) bits (Eq. 32)
    h_prime: int   # pixels holding floor(Nc) bits (Eq. 33)

    @property
    def kt_len(self):
        # Each block of s bits leaves s - 1 bits of Key Trace.
        return self.h * (self.ceil_nc - 1) + self.h_prime * (self.floor_nc - 1)


def cycle_layout(ET, P):
    floor_nc = ET // P
    h = ET - floor_nc * P                 # = P * (Nc - floor(Nc))
    ceil_nc = floor_nc + (1 if h else 0)
    return CycleLayout(ET, P, ET / P, ceil_nc, floor_nc, h, P - h)


def _groups(bits, layout):
    """Blocks db (size ceil(Nc)) followed by blocks db' (size floor(Nc))."""
    split = layout.h * layout.ceil_nc
    groups = []
    if layout.h:
        groups.append(bits[:split].reshape(layout.h, layout.ceil_nc))
    if layout.h_prime:
        groups.append(bits[split:].reshape(layout.h_prime, layout.floor_nc))
    return groups


def generate_key_trace(eb, layout, R):
    """Algorithm 1 for every block.

        CK_{s-1} = db_s xor R,  CK_{t-1} = db_t xor CK_t,  E = db_1 xor CK_1

    which unrolls to a suffix XOR: CK_j = R xor db_{j+1} xor ... xor db_s and
    E = R xor db_1 xor ... xor db_s (the parity of the block). Returns
    (Em, KT): one bit per cover pixel and the Key Trace for the agreed image.
    """
    em_parts, kt_parts = [], []
    for D in _groups(eb, layout):
        suffix = np.bitwise_xor.accumulate(D[:, ::-1], axis=1)[:, ::-1] ^ np.uint8(R)
        em_parts.append(suffix[:, 0])
        kt_parts.append(suffix[:, 1:].ravel())
    return np.concatenate(em_parts), np.concatenate(kt_parts)


def recover_from_key_trace(em, kt, layout, R):
    """Algorithm 2: kb = (E, CK_1, ..., CK_{s-1}, R), db_j = kb_j xor kb_{j+1}."""
    out = []
    em_pos = kt_pos = 0
    for rows, size in ((layout.h, layout.ceil_nc), (layout.h_prime, layout.floor_nc)):
        if not rows:
            continue
        ck = kt[kt_pos:kt_pos + rows * (size - 1)].reshape(rows, size - 1)
        kb = np.hstack([em[em_pos:em_pos + rows, None], ck,
                        np.full((rows, 1), R, dtype=np.uint8)])
        out.append((kb[:, :-1] ^ kb[:, 1:]).ravel())
        em_pos += rows
        kt_pos += rows * (size - 1)
    return np.concatenate(out)


# --------------------------------------------------------------------------
# Key Trace <-> agreed image (Section 4.1.5, 4.2.4)
# --------------------------------------------------------------------------
def agreed_bits_per_pixel(kt_len, n_pixels):
    """nn = |KT| / (H2*W2) (Eq. 37): first pixels get ceil(nn), the rest floor(nn)."""
    floor_nn = kt_len // n_pixels
    extra = kt_len - floor_nn * n_pixels
    if floor_nn + (1 if extra else 0) > 8:
        raise ValueError(f"agreed image too small: needs {kt_len / n_pixels:.2f} bits/pixel")
    per_pixel = np.full(n_pixels, floor_nn, dtype=np.int64)
    per_pixel[:extra] += 1
    return per_pixel


def _pack_variable(bits, per_pixel):
    values = np.zeros(len(per_pixel), dtype=np.int64)
    pos = 0
    for width in np.unique(per_pixel):
        idx = np.flatnonzero(per_pixel == width)
        if width == 0:
            continue
        chunk = bits[pos:pos + len(idx) * width].reshape(len(idx), width)
        values[idx] = chunk.astype(np.int64) @ (1 << np.arange(width - 1, -1, -1))
        pos += len(idx) * width
    return values


def _unpack_variable(values, per_pixel):
    out = []
    for width in np.unique(per_pixel):
        idx = np.flatnonzero(per_pixel == width)
        if width == 0:
            continue
        shifts = np.arange(width - 1, -1, -1)
        out.append(((values[idx, None] >> shifts) & 1).astype(np.uint8).ravel())
    return np.concatenate(out)


def embed_key_trace(agreed, kt):
    per_pixel = agreed_bits_per_pixel(len(kt), agreed.size)
    # np.unique sorts widths ascending, and ceil(nn) pixels come first, so
    # the packing order is: floor(nn) pixels, then ceil(nn) pixels.
    values = _pack_variable(kt, per_pixel)
    flat = modulus_embed(agreed.ravel(), values, per_pixel)
    return flat.reshape(agreed.shape)


def extract_key_trace(agreed_stego, kt_len):
    per_pixel = agreed_bits_per_pixel(kt_len, agreed_stego.size)
    values = modulus_extract(agreed_stego.ravel(), per_pixel)
    return _unpack_variable(values, per_pixel)


# --------------------------------------------------------------------------
# Secret key and (2,2) visual cryptography (Section 4.1.6, 4.2.1)
# --------------------------------------------------------------------------
KEY_FORMAT = "{seed:010d} {nc:012.6f} {h0:05d} {w0:05d}"
KEY_CHARS = 35                                   # fixed width, so |S2| is known


class KeyRecoveryError(Exception):
    pass


def key_to_matrix(seed, nc, h0, w0):
    """Secret Key T' as a binary matrix, one 8-bit row per character.

    The paper renders every character as a 16x14 glyph to be read by eye;
    here each character is its ASCII byte so the receiver can parse it.
    """
    text = KEY_FORMAT.format(seed=seed, nc=nc, h0=h0, w0=w0)
    assert len(text) == KEY_CHARS, text
    return np.unpackbits(np.frombuffer(text.encode("ascii"), dtype=np.uint8)).reshape(KEY_CHARS, 8)


def matrix_to_key(mat):
    text = np.packbits(mat.ravel()).tobytes().decode("ascii", errors="replace")
    try:
        seed, nc, h0, w0 = text.split()
        return {"seed": int(seed), "nc": float(nc), "h0": int(h0), "w0": int(w0), "text": text}
    except ValueError as exc:
        raise KeyRecoveryError(f"key image unreadable: {text!r}") from exc


_VCS_PATTERNS = np.array([[1, 0], [0, 1]], dtype=np.uint8)


def vcs_split(secret, rng):
    """(2,2) VCS, pixel expansion 2: white -> equal subpixels, black -> complementary."""
    choice = rng.integers(0, 2, size=secret.shape)
    s1 = _VCS_PATTERNS[choice]
    s2 = np.where(secret[..., None] == 1, _VCS_PATTERNS[1 - choice], s1)
    h, w = secret.shape
    return s1.reshape(h, 2 * w), s2.reshape(h, 2 * w)


def vcs_stack(s1, s2):
    return s1 | s2


def vcs_decode(stacked):
    h, w2 = stacked.shape
    return (stacked.reshape(h, w2 // 2, 2).sum(axis=2) == 2).astype(np.uint8)


def share2_region(n_pixels, rm):
    """S2 is RM-encoded and stored in the last pixels of the stego (marker q)."""
    s2_bits = KEY_CHARS * 8 * 2
    length = math.ceil(s2_bits / rm.k) * rm.N
    return n_pixels - length, s2_bits


# --------------------------------------------------------------------------
# Embedding / extraction
# --------------------------------------------------------------------------
def encoded_length(h0, w0, rm):
    """E_T = 8 * H0 * W0 * N / k, rounded up to whole codewords."""
    return math.ceil(8 * h0 * w0 / rm.k) * rm.N


def embed(cover, secret, agreed, seed, R=0, rm_m=4, rng=None):
    """Sender side (Section 4.1). Returns (stego I'', agreed stego A', share 1, info)."""
    rng = rng or np.random.default_rng()
    rm = RM1(rm_m)
    h0, w0 = secret.shape
    HW = cover.size
    P = 3 * HW // 4
    q, _ = share2_region(HW, rm)
    if P > q:
        raise ValueError("cover too small for 3/4 HW plus the Share 2 region")

    # 4.1.1 Encoding
    sb = image_to_bits(secret)
    eb = rm_encode_bits(sb, rm)
    ET = len(eb)

    # 4.1.2 Key Trace (only when the encoded bits exceed 3/4 of the cover)
    layout = None
    kt = np.zeros(0, dtype=np.uint8)
    if ET > P:
        layout = cycle_layout(ET, P)
        EB, kt = generate_key_trace(eb, layout, R)
    else:
        EB = eb                                                  # Eq. 36
    nc = ET / P

    # 4.1.3 + 4.1.4 random positions, LSB embedding with n = 1
    positions = random_positions(seed, len(EB), q)               # L from Eq. 35
    stego = cover.ravel().copy()
    stego[positions] = modulus_embed(stego[positions], EB, 1)

    # 4.1.5 Key Trace into the agreed image
    agreed_stego = embed_key_trace(agreed, kt) if len(kt) else agreed.copy()

    # 4.1.6 + 4.1.7 key -> shares; S2 (RM encoded) into the stego tail
    key = key_to_matrix(seed, nc, h0, w0)
    share1, share2 = vcs_split(key, rng)
    ct = rm_encode_bits(share2.ravel(), rm)
    stego[q:] = modulus_embed(stego[q:], ct, 1)

    info = {
        "secret_bits": len(sb), "ET": ET, "P": P, "Nc": nc,
        "kt_len": len(kt), "cover_bits": len(EB),
        "nn": len(kt) / agreed.size if len(kt) else 0.0,
        "h": layout.h if layout else 0, "h_prime": layout.h_prime if layout else 0,
        "share2_pixels": HW - q,
        "EC_paper": ET / HW,                                     # Eq. 26 / 38
        "payload_bpp": len(sb) / HW,
        "EC_both_carriers": ET / (HW + (agreed.size if len(kt) else 0)),
    }
    return stego.reshape(cover.shape), agreed_stego, share1, info


def recover_key(stego, share1, rm_m=4):
    """Section 4.2.1: extract S2, decode it, stack with S1."""
    rm = RM1(rm_m)
    q, s2_bits = share2_region(stego.size, rm)
    ct = modulus_extract(stego.ravel()[q:], 1).astype(np.uint8)
    share2 = rm_decode_bits(ct, rm, s2_bits).reshape(share1.shape)
    return matrix_to_key(vcs_decode(vcs_stack(share1, share2)))


def extract(stego, agreed_stego, share1, R=0, rm_m=4, key=None):
    """Receiver side (Section 4.2). Pass `key` to skip share recovery."""
    rm = RM1(rm_m)
    key = key or recover_key(stego, share1, rm_m)
    h0, w0 = key["h0"], key["w0"]
    HW = stego.size
    P = 3 * HW // 4
    q, _ = share2_region(HW, rm)
    ET = encoded_length(h0, w0, rm)

    layout = cycle_layout(ET, P) if ET > P else None
    positions = random_positions(key["seed"], P if layout else ET, q)
    em = modulus_extract(stego.ravel()[positions], 1).astype(np.uint8)   # 4.2.3

    if layout:                                                           # 4.2.4 + 4.2.5
        kt = extract_key_trace(agreed_stego, layout.kt_len)
        eb = recover_from_key_trace(em, kt, layout, R)
    else:
        eb = em

    sb = rm_decode_bits(eb, rm, 8 * h0 * w0)                             # 4.2.6
    return bits_to_image(sb, h0, w0), key                                # 4.2.7


# --------------------------------------------------------------------------
# Metrics (Eq. 39-40)
# --------------------------------------------------------------------------
def psnr(a, b, cap=100.0):
    """PSNR in dB; identical images are reported as `cap` like the paper (100 dB)."""
    mse = np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2)
    return cap if mse == 0 else min(cap, 10 * np.log10(255.0 ** 2 / mse))


def bit_error_rate(a, b):
    return float(np.mean(image_to_bits(a) != image_to_bits(b)))
