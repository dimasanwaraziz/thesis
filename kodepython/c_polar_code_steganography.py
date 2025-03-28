import cv2
import numpy as np
from scipy.special import expit
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import sys


def polar_encode(data):
    """Simulasi encoding Polar Code dengan sigmoid sebagai representasi probabilitas."""
    return np.round(expit((data - 0.5) * 10)).astype(np.uint8)


def polar_decode(data):
    """Dekode data biner kembali dari hasil embedding Polar Code."""
    return (data > 0.5).astype(np.uint8)


def embed_image(host_img, secret_img, num_lsb=2):
    """Menyisipkan secret image menggunakan Multiple LSB."""
    host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
    secret_bin = np.unpackbits(secret_img.flatten())

    max_capacity = (host_gray.size * num_lsb) // 8
    if len(secret_bin) // 8 > max_capacity:
        raise ValueError("Secret image terlalu besar untuk di-embed dalam host image.")

    encoded_data = polar_encode(secret_bin)
    encoded_data = np.packbits(encoded_data).astype(np.uint8)

    host_gray_flat = host_gray.flatten()
    data_index = 0

    for i in range(len(encoded_data)):
        for bit in range(8 // num_lsb):
            if data_index >= len(host_gray_flat):
                break
            mask = 0xFF - (2**num_lsb - 1)
            host_gray_flat[data_index] = (host_gray_flat[data_index] & mask) | (
                (encoded_data[i] >> (bit * num_lsb)) & (2**num_lsb - 1)
            )
            data_index += 1

    embedded_img = host_gray_flat.reshape(host_gray.shape)
    return embedded_img


def extract_image(embedded_img, secret_shape, num_lsb=2):
    """Ekstraksi gambar yang telah disisipkan."""
    embedded_flat = embedded_img.flatten()
    num_bits = np.prod(secret_shape) * 8
    extracted_bits = []

    data_index = 0
    for _ in range(num_bits):
        extracted_bits.append(embedded_flat[data_index] & (2**num_lsb - 1))
        data_index += 1

    extracted_bits = np.array(extracted_bits, dtype=np.uint8)
    extracted_bytes = np.packbits(extracted_bits)

    expected_size = np.prod(secret_shape)
    if extracted_bytes.size < expected_size:
        extracted_bytes = np.pad(
            extracted_bytes, (0, expected_size - extracted_bytes.size), mode="constant"
        )
    elif extracted_bytes.size > expected_size:
        extracted_bytes = extracted_bytes[:expected_size]

    return extracted_bytes.reshape(secret_shape)


def compute_capacity(secret_img, host_img):
    """Menghitung kapasitas penyisipan dalam bit per pixel (bpp)."""
    return (np.prod(secret_img.shape) * 8) / np.prod(host_img.shape)


# ---- Contoh Penggunaan ----
if len(sys.argv) != 3:
    print("Usage: python c_polar_code_steganography.py <host_image_path> <secret_image_path>")
    sys.exit(1)

host_image_path = sys.argv[1]
secret_image_path = sys.argv[2]

host = cv2.imread(host_image_path)
secret = cv2.imread(secret_image_path, cv2.IMREAD_GRAYSCALE)

capacity_before = compute_capacity(secret, host)
print(f"Kapasitas sebelum embedding: {capacity_before:.4f} bpp")

embedded = embed_image(host, secret, num_lsb=2)
cv2.imwrite("embedded_polar_code.png", embedded.astype(np.uint8))

extracted = extract_image(embedded, secret.shape, num_lsb=2)
cv2.imwrite("extracted_polar_code.png", extracted.astype(np.uint8))

host_gray = cv2.cvtColor(host, cv2.COLOR_BGR2GRAY)
psnr = peak_signal_noise_ratio(host_gray, embedded)
ssim = structural_similarity(host_gray, embedded)

print(f"PSNR: {psnr:.2f} dB")
print(f"SSIM: {ssim:.4f}")
print(f"Kapasitas setelah embedding: {capacity_before:.4f} bpp")  # Kapasitas tetap sama
