"""
Checks against the worked examples in the paper plus round-trip tests.
Run with `python test_kingsley.py` (or pytest).
"""
import numpy as np

import kingsley_stego as ks


def bits(s):
    return np.array([int(c) for c in s], dtype=np.uint8)


def test_rm14_parameters():
    rm = ks.RM1(4)
    assert (rm.k, rm.N, rm.dmin, rm.t) == (5, 16, 8, 3)        # Section 2, example after Eq. 4
    expected = ["0000000011111111", "0000111100001111", "0011001100110011",
                "0101010101010101", "1111111111111111"]
    assert ["".join(map(str, row)) for row in rm.G] == expected


def test_rm14_encode_example():
    # u = 10101 -> row1 xor row3 xor row5. The paper prints 0000111001101011,
    # but its own decoding example (p. 19) yields 1100110000110011.
    rm = ks.RM1(4)
    assert "".join(map(str, rm.encode(bits("10101")[None])[0])) == "1100110000110011"


def test_rm14_decode_example():
    # Received word from Section 2.3 (3 bit errors) decodes to 10101.
    rm = ks.RM1(4)
    assert "".join(map(str, rm.decode(bits("1110110010111011")[None])[0])) == "10101"


def test_rm14_corrects_up_to_t_errors():
    rng = np.random.default_rng(1)
    rm = ks.RM1(4)
    msg = rng.integers(0, 2, (2000, rm.k), dtype=np.uint8)
    cw = rm.encode(msg)
    for row in cw:
        row[rng.choice(rm.N, rm.t, replace=False)] ^= 1
    assert np.array_equal(rm.decode(cw), msg)


def test_padding_example():
    # Section 4.1.1: 1010111100110 -> 10101, 11100, 11000
    blocks = ks.to_blocks(bits("1010111100110"), 5)
    assert ["".join(map(str, b)) for b in blocks] == ["10101", "11100", "11000"]


def test_modulus_function_roundtrip():
    rng = np.random.default_rng(2)
    for n in range(1, 5):
        x = rng.integers(0, 256, 5000).astype(np.uint8)
        x[:4] = [0, 1, 254, 255]
        z = rng.integers(0, 2 ** n, 5000)
        xp = ks.modulus_embed(x, z, n)
        assert np.array_equal(ks.modulus_extract(xp, n), z)
        assert np.abs(xp.astype(int) - x.astype(int)).max() <= 2 ** n


def test_modulus_n1_changes_by_one():
    x = np.arange(256, dtype=np.uint8)
    for z in (0, 1):
        xp = ks.modulus_embed(x, np.full(256, z), 1)
        assert np.abs(xp.astype(int) - x.astype(int)).max() <= 1


def test_key_trace_example():
    # db = 101101, R = 0 -> E = 0, Key Trace = 11011 (worked example in the notes)
    layout = ks.cycle_layout(6, 1)
    em, kt = ks.generate_key_trace(bits("101101"), layout, 0)
    assert em.tolist() == [0] and kt.tolist() == [1, 1, 0, 1, 1]
    assert ks.recover_from_key_trace(em, kt, layout, 0).tolist() == bits("101101").tolist()


def test_key_trace_roundtrip_fractional_nc():
    rng = np.random.default_rng(3)
    for ET, P in [(1000, 300), (1179648, 196608), (700, 699), (5, 5)]:
        layout = ks.cycle_layout(ET, P)
        assert layout.h + layout.h_prime == P
        assert layout.kt_len == ET - P
        eb = rng.integers(0, 2, ET, dtype=np.uint8)
        for R in (0, 1):
            em, kt = ks.generate_key_trace(eb, layout, R)
            assert len(em) == P and len(kt) == layout.kt_len
            parity = np.concatenate([g.sum(axis=1) % 2 for g in ks._groups(eb, layout)])
            assert np.array_equal(em, parity.astype(np.uint8) ^ R)    # E = parity(block) xor R
            assert np.array_equal(ks.recover_from_key_trace(em, kt, layout, R), eb)


def test_agreed_image_roundtrip():
    rng = np.random.default_rng(4)
    agreed = rng.integers(0, 256, (64, 64)).astype(np.uint8)
    for kt_len in (100, 4096, 983040 // 64, 3 * 4096 + 1234):
        kt = rng.integers(0, 2, kt_len, dtype=np.uint8)
        out = ks.embed_key_trace(agreed, kt)
        assert np.array_equal(ks.extract_key_trace(out, kt_len), kt)


def test_vcs_roundtrip():
    rng = np.random.default_rng(5)
    key = ks.key_to_matrix(262139, 0.01, 10, 6)
    s1, s2 = ks.vcs_split(key, rng)
    assert s1.shape == (key.shape[0], 2 * key.shape[1])
    assert np.array_equal(ks.vcs_decode(ks.vcs_stack(s1, s2)), key)
    assert ks.matrix_to_key(key)["seed"] == 262139


def test_bbs_positions_distinct():
    pos = ks.random_positions(262139, 5000, 6000)
    assert len(np.unique(pos)) == 5000 and pos.max() < 6000


def test_end_to_end_small_and_multiple_embedding():
    rng = np.random.default_rng(6)
    cover = rng.integers(0, 256, (128, 128)).astype(np.uint8)
    agreed = rng.integers(0, 256, (128, 128)).astype(np.uint8)
    # 10x6 secret: E_T <= 3/4 HW (no Key Trace); 48x40: Nc ~ 4 (multiple embedding)
    for shape in [(10, 6), (48, 40)]:
        secret = rng.integers(0, 256, shape).astype(np.uint8)
        stego, agreed_stego, s1, info = ks.embed(cover, secret, agreed, seed=262139, rng=rng)
        recovered, key = ks.extract(stego, agreed_stego, s1)
        assert np.array_equal(recovered, secret), (shape, info)
        assert np.abs(stego.astype(int) - cover.astype(int)).max() <= 1


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
    for name, fn in tests:
        fn()
        print(f"PASS {name}")
    print(f"\n{len(tests)} tests passed")
