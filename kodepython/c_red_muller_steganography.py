import cv2
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from reedsolo import RSCodec, ReedSolomonError


def reed_muller_encode(data, n=4, k=11):
    """Simulasi encoding Reed-Muller Code."""
    rsc = RSCodec(2**n - k)
    encoded_data = b""
    for byte in data.tobytes():
        encoded_data += rsc.encode(bytes([byte]))
    return np.frombuffer(encoded_data, dtype=np.uint8)


def reed_muller_decode(data, n=4, k=11):
    """Dekode data biner kembali dari hasil embedding Reed-Muller Code."""
    rsc = RSCodec(2**n - k)
    decoded_data = b""
    for i in range(0, len(data), 2**n):
        chunk = data[i : i + 2**n]
        if len(chunk) < 2**n:
            chunk = np.pad(chunk, (0, 2**n - len(chunk)), mode="constant")
        try:
            decoded_data += rsc.decode(bytes(chunk))[0]
        except ReedSolomonError:
            decoded_data += b"\x00"
    return np.frombuffer(decoded_data, dtype=np.uint8)


def embed_image_reed_muller(host_img, secret_img, n=4, k=11):
    """Menyisipkan secret image menggunakan Reed-Muller Code."""
    host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
    secret_bin = secret_img.flatten()

    encoded_data = reed_muller_encode(secret_bin, n, k)

    if len(encoded_data) > host_gray.size:
        raise ValueError("Secret image terlalu besar untuk di-embed dalam host image.")

    host_gray_flat = host_gray.flatten()
    random_indices = np.random.permutation(len(host_gray_flat))[: len(encoded_data)]
    host_gray_flat[random_indices] = encoded_data

    embedded_img = host_gray_flat.reshape(host_gray.shape)
    return embedded_img


def extract_image_reed_muller(embedded_img, secret_shape, n=4, k=11):
    """Ekstraksi gambar yang telah disisipkan menggunakan Reed-Muller decoding."""
    embedded_flat = embedded_img.flatten()
    num_secret_bytes = np.prod(secret_shape)
    expected_encoded_size = num_secret_bytes * (2**n // k)

    extracted_bytes = embedded_flat[:expected_encoded_size]
    decoded_data = reed_muller_decode(extracted_bytes, n, k)

    # Penanganan ukuran data yang tidak sesuai
    if decoded_data.size < num_secret_bytes:
        decoded_data = np.pad(
            decoded_data, (0, num_secret_bytes - decoded_data.size), mode="constant"
        )
    elif decoded_data.size > num_secret_bytes:
        decoded_data = decoded_data[:num_secret_bytes]

    return decoded_data.reshape(secret_shape)


def compute_capacity(secret_img, host_img):
    """Menghitung kapasitas penyisipan dalam bit per pixel (bpp)."""
    return np.prod(secret_img.shape) / np.prod(host_img.shape)


# ---- Contoh Penggunaan ----
host = cv2.imread("host_image.png")
secret = cv2.imread("secret_image.png", cv2.IMREAD_GRAYSCALE)

capacity_before = compute_capacity(secret, host)
print(f"Kapasitas sebelum embedding: {capacity_before:.4f} bpp")

embedded = embed_image_reed_muller(host, secret)
cv2.imwrite("embedded_reed_muller.png", embedded.astype(np.uint8))

extracted = extract_image_reed_muller(embedded, secret.shape)
cv2.imwrite("extracted_reed_muller.png", extracted.astype(np.uint8))

capacity_after = compute_capacity(extracted, host)
print(f"Kapasitas setelah embedding: {capacity_after:.4f} bpp")

host_gray = cv2.cvtColor(host, cv2.COLOR_BGR2GRAY)
psnr = peak_signal_noise_ratio(host_gray, embedded)
ssim = structural_similarity(host_gray, embedded)

print(f"PSNR: {psnr:.2f} dB")
print(f"SSIM: {ssim:.4f}")
