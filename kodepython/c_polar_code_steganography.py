import cv2
import numpy as np
from scipy.special import expit
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def polar_encode(data):
    """Simulasi encoding Polar Code dengan sigmoid sebagai representasi probabilitas."""
    return np.round(expit((data - 0.5) * 20)).astype(np.uint8)


def polar_decode(data):
    """Dekode data biner kembali dari hasil embedding Polar Code."""
    return (data > 0.5).astype(np.uint8)


def embed_image(host_img, secret_img, num_lsb=2):
    """Menyisipkan secret image menggunakan Multiple LSB."""
    host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
    secret_bin = np.unpackbits(secret_img.flatten())

    if len(secret_bin) * (8 // num_lsb) > host_gray.size:
        raise ValueError("Secret image terlalu besar untuk di-embed dalam host image.")

    encoded_data = polar_encode(secret_bin)
    encoded_data = np.packbits(encoded_data).astype(np.uint8)

    host_gray_flat = host_gray.flatten()
    data_index = 0

    for i in range(len(encoded_data)):
        mask = 0xFF - (2**num_lsb - 1)
        host_gray_flat[data_index] = (host_gray_flat[data_index] & mask) | (encoded_data[i] & (2**num_lsb - 1))
        data_index += 1

    embedded_img = host_gray_flat.reshape(host_gray.shape)
    return embedded_img


def extract_image(embedded_img, secret_shape, num_lsb=2):
    """Ekstraksi gambar yang telah disisipkan."""
    embedded_flat = embedded_img.flatten()
    num_bits = np.prod(secret_shape) * 8
    extracted_bytes = []
    data_index = 0

    for _ in range(num_bits // 8):
        byte = 0
        for j in range(8 // num_lsb):
            byte |= (embedded_flat[data_index] & (2**num_lsb - 1)) << (j * num_lsb)
            data_index += 1
        extracted_bytes.append(byte)

    decoded_data = np.array(extracted_bytes, dtype=np.uint8)

    expected_size = np.prod(secret_shape)
    if decoded_data.size < expected_size:
        decoded_data = np.pad(decoded_data, (0, expected_size - decoded_data.size), mode="constant")
    elif decoded_data.size > expected_size:
        decoded_data = decoded_data[:expected_size]

    return decoded_data.reshape(secret_shape)


def compute_capacity(secret_img, host_img):
    """Menghitung kapasitas penyisipan dalam bit per pixel (bpp)."""
    return np.prod(secret_img.shape) / np.prod(host_img.shape)


# ---- Contoh Penggunaan ----
host = cv2.imread("host_image.png")
secret = cv2.imread("secret_image.png", cv2.IMREAD_GRAYSCALE)

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
print(f"Kapasitas setelah embedding: {capacity_before:.4f} bpp") # kapasitas tetap sama