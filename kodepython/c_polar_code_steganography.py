import cv2
import numpy as np
from scipy.special import expit  # Sigmoid function (Polar Code approximation)
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def polar_encode(data):
    """Simulasi encoding Polar Code dengan sigmoid sebagai representasi probabilitas."""
    return np.round(expit((data - 0.5) * 20)).astype(np.uint8)  # Scaling lebih tajam


def polar_decode(data):
    """Dekode data biner kembali dari hasil embedding Polar Code."""
    return (data > 0.5).astype(np.uint8)  # Ambil threshold dari probabilitas


# def embed_image(host_img, secret_img):
#     """Menyisipkan gambar menggunakan Polar Code."""
#     host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
#     secret_bin = np.unpackbits(secret_img.flatten())

#     if len(secret_bin) > host_gray.size:
#         raise ValueError("Secret image terlalu besar untuk di-embed dalam host image.")

#     encoded_data = polar_encode(secret_bin)
#     encoded_data = encoded_data[: host_gray.size]

#     host_gray_flat = host_gray.flatten()
#     random_indices = np.random.permutation(len(host_gray_flat))[: len(encoded_data)]
#     host_gray_flat[random_indices] = (
#         host_gray_flat[random_indices] & 0xFE
#     ) | encoded_data

#     embedded_img = host_gray_flat.reshape(host_gray.shape)
#     return embedded_img
def embed_image(host_img, secret_img, num_lsb=2):
    """Menyisipkan secret image menggunakan Multiple LSB (default: 2-bit)."""
    host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
    secret_bin = np.unpackbits(secret_img.flatten())

    if len(secret_bin) * (8 // num_lsb) > host_gray.size:
        raise ValueError("Secret image terlalu besar untuk di-embed dalam host image.")

    encoded_data = polar_encode(secret_bin)
    encoded_data = np.packbits(encoded_data).astype(np.uint8)  # Pastikan uint8

    host_gray_flat = host_gray.flatten()
    random_indices = np.random.permutation(len(host_gray_flat))[: len(encoded_data)]

    # Multiple LSB embedding (gunakan num_lsb bit)
    mask = 0xFF - (2**num_lsb - 1)  # Contoh: num_lsb=2 -> mask = 0xFC
    encoded_data = encoded_data & (2**num_lsb - 1)  # Batasi encoded_data ke num_lsb bit

    # Pastikan operasi tetap dalam batas uint8 (0-255)
    host_gray_flat[random_indices] = (host_gray_flat[random_indices] & mask) | encoded_data

    embedded_img = host_gray_flat.reshape(host_gray.shape)
    return embedded_img




def extract_image(embedded_img, secret_shape):
    """Ekstraksi gambar yang telah disisipkan menggunakan Polar Code decoding."""
    embedded_flat = embedded_img.flatten()
    num_bits = np.prod(secret_shape) * 8
    extracted_bits = embedded_flat[:num_bits] & 1

    padded_bits = np.pad(
        extracted_bits, (0, 8 - len(extracted_bits) % 8), mode="constant"
    )
    decoded_data = np.packbits(padded_bits)

    expected_size = np.prod(secret_shape)
    if decoded_data.size < expected_size:
        decoded_data = np.pad(
            decoded_data, (0, expected_size - decoded_data.size), mode="constant"
        )
    elif decoded_data.size > expected_size:
        decoded_data = decoded_data[:expected_size]

    return decoded_data.reshape(secret_shape)


def compute_capacity(secret_img, host_img):
    """Menghitung kapasitas penyisipan dalam bit per pixel (bpp)."""
    return np.prod(secret_img.shape) / np.prod(host_img.shape)


# ---- Contoh Penggunaan ----
host = cv2.imread("host_image.png")  # Gambar host
secret = cv2.imread("secret_image.png", cv2.IMREAD_GRAYSCALE)  # Gambar rahasia

# Cek kapasitas penyisipan sebelum embedding
capacity_before = compute_capacity(secret, host)
print(f"Kapasitas sebelum embedding: {capacity_before:.4f} bpp")

# Embed gambar
embedded = embed_image(host, secret, num_lsb=2)
cv2.imwrite("embedded_polar_code.png", embedded.astype(np.uint8))

# Ekstrak kembali gambar rahasia
extracted = extract_image(embedded, secret.shape)
cv2.imwrite("extracted_polar_code.png", extracted.astype(np.uint8))

# Hitung kapasitas setelah ekstraksi
capacity_after = np.prod(extracted.shape) / np.prod(host.shape)
print(f"Kapasitas setelah embedding: {capacity_after:.4f} bpp")

# Evaluasi kualitas gambar setelah embedding
host_gray = cv2.cvtColor(host, cv2.COLOR_BGR2GRAY)
psnr = peak_signal_noise_ratio(host_gray, embedded)
ssim = structural_similarity(host_gray, embedded)

print(f"PSNR: {psnr:.2f} dB")
print(f"SSIM: {ssim:.4f}")
