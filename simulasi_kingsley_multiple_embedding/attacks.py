"""
Attacks used in Section 6.3 of the paper. Noise follows MATLAB imnoise
semantics (intensities normalised to [0, 1]), which is what the reported
variances/densities refer to.
"""
import io

import numpy as np
from PIL import Image, ImageDraw


def _to_uint8(x):
    return np.clip(np.round(x * 255.0), 0, 255).astype(np.uint8)


def gaussian(img, var, rng, mean=0.0):
    x = img.astype(np.float64) / 255.0
    return _to_uint8(x + rng.normal(mean, np.sqrt(var), img.shape))


def salt_and_pepper(img, density, rng):
    out = img.copy()
    u = rng.random(img.shape)
    out[u < density / 2] = 0
    out[(u >= density / 2) & (u < density)] = 255
    return out


def speckle(img, var, rng):
    # J = I + n*I, n uniform with zero mean and variance `var`.
    x = img.astype(np.float64) / 255.0
    a = np.sqrt(3.0 * var)
    return _to_uint8(x + x * rng.uniform(-a, a, img.shape))


def crop(img, rows, cols):
    """Blank out the cropping area (Table 3 gives it as row/column ranges)."""
    out = img.copy()
    out[rows[0]:rows[1], cols[0]:cols[1]] = 0
    return out


def scratch(img, count, rng, width=3):
    """Random straight scratches drawn in black or white."""
    pil = Image.fromarray(img)
    draw = ImageDraw.Draw(pil)
    h, w = img.shape
    for _ in range(count):
        x0, x1 = rng.integers(0, w, 2)
        y0, y1 = rng.integers(0, h, 2)
        draw.line([(int(x0), int(y0)), (int(x1), int(y1))],
                  fill=int(rng.choice([0, 255])), width=width)
    return np.array(pil)


def jpeg(img, quality):
    buf = io.BytesIO()
    Image.fromarray(img).save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return np.array(Image.open(buf).convert("L"))


def attack_suite():
    """(label, function(img, rng)) pairs mirroring Tables 2-5."""
    return [
        ("Gaussian var 0.01",       lambda im, r: gaussian(im, 0.01, r)),
        ("Salt & pepper 0.05",      lambda im, r: salt_and_pepper(im, 0.05, r)),
        ("Speckle var 0.04",        lambda im, r: speckle(im, 0.04, r)),
        ("Gaussian var 0.1",        lambda im, r: gaussian(im, 0.1, r)),
        ("Salt & pepper 0.5",       lambda im, r: salt_and_pepper(im, 0.5, r)),
        ("Speckle var 0.4",         lambda im, r: speckle(im, 0.4, r)),
        ("Crop 0-512 x 0-360",      lambda im, r: crop(im, (0, 512), (0, 360))),
        ("Crop 70-422 x 80-422",    lambda im, r: crop(im, (70, 422), (80, 422))),
        ("Crop 20-435 x 40-452",    lambda im, r: crop(im, (20, 435), (40, 452))),
        ("Scratch single",          lambda im, r: scratch(im, 1, r)),
        ("Scratch multiple (10)",   lambda im, r: scratch(im, 10, r)),
        ("JPEG Q=90",               lambda im, r: jpeg(im, 90)),
        ("JPEG Q=75",               lambda im, r: jpeg(im, 75)),
    ]
