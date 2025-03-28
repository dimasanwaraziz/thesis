import cv2
import numpy as np
import matplotlib.pyplot as plt
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import sys

# Load secret image dan hasil ekstraksi dari parameter input
if len(sys.argv) != 3:
    raise ValueError("Gunakan: python testing_polar.py <path_secret_image> <path_extracted_image>")

secret_path = sys.argv[1]
extracted_path = sys.argv[2]

secret = cv2.imread(secret_path, cv2.IMREAD_GRAYSCALE)
extracted = cv2.imread(extracted_path, cv2.IMREAD_GRAYSCALE)

if secret is None or extracted is None:
    raise ValueError("Gambar secret atau extracted tidak ditemukan!")

# Pastikan ukuran sama
if secret.shape != extracted.shape:
    raise ValueError("Ukuran secret image dan extracted image tidak sama!")

# 1. **Menghitung PSNR**
psnr_value = peak_signal_noise_ratio(secret, extracted)
print(f"PSNR Secret Image: {psnr_value:.2f} dB")

# 2. **Menghitung SSIM**
ssim_value = structural_similarity(secret, extracted)
print(f"SSIM Secret Image: {ssim_value:.4f}")

# 3. **Menghitung Bit Error Rate (BER)**
bit_errors = np.sum(secret.flatten() != extracted.flatten())  # Hitung bit yang berbeda
total_bits = np.prod(secret.shape) * 8  # Total bit dalam secret image
ber_value = bit_errors / total_bits
print(f"Bit Error Rate (BER): {ber_value:.6f}")

# 4. **Menampilkan Secret Image & Ekstraksi**
plt.figure(figsize=(10, 5))

plt.subplot(1, 2, 1)
plt.title("Secret Image Asli")
plt.imshow(secret, cmap="gray")
plt.axis("off")

plt.subplot(1, 2, 2)
plt.title("Secret Image Ekstrak")
plt.imshow(extracted, cmap="gray")
plt.axis("off")

plt.show()

# 5. **Visualisasi Perbedaan dengan Heatmap**
diff = np.abs(secret.astype(np.int16) - extracted.astype(np.int16))  # Hitung perbedaan absolut
plt.figure(figsize=(6, 5))
plt.title("Peta Perbedaan Secret Image")
plt.imshow(diff, cmap="hot")
plt.colorbar(label="Perbedaan Intensitas")
plt.axis("off")
plt.show()
