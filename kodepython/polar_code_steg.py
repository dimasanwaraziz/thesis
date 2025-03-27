# -*- coding: utf-8 -*-
"""
polar_code_steg.py: Steganografi Gambar dalam Gambar menggunakan LSB
                    dengan Error Correction Code Polar Codes (menggunakan affes).
"""

import numpy as np
from PIL import Image
import affes.polar_core as affes_pc  # Pastikan affes terinstal
import math
import sys
import os

# --- Fungsi Helper Umum (Disalin dari reed_muller_steg.py) ---


def image_to_bits(image_path):
    """Mengubah gambar menjadi representasi bit (termasuk dimensi)."""
    try:
        img = Image.open(image_path).convert("RGB")  # Konversi ke RGB untuk konsistensi
        width, height = img.size
        pixels = np.array(img).flatten()
        width_bits = format(width, "032b")
        height_bits = format(height, "032b")
        header_bits = width_bits + height_bits
        data_bits = "".join(format(p, "08b") for p in pixels)
        print(
            f"Gambar rahasia '{os.path.basename(image_path)}': {width}x{height}, Header: {len(header_bits)} bits, Data: {len(data_bits)} bits."
        )
        return header_bits + data_bits, width, height, "RGB"
    except FileNotFoundError:
        print(f"Error: File gambar rahasia '{image_path}' tidak ditemukan.")
        sys.exit(1)
    except Exception as e:
        print(f"Error saat memproses gambar rahasia: {e}")
        sys.exit(1)


def bits_to_image(bit_string, output_path):
    """Mengubah representasi bit kembali menjadi gambar."""
    try:
        if len(bit_string) < 64:
            print(
                f"Error: Data bit ({len(bit_string)} bits) tidak cukup untuk header (64 bits)."
            )
            return False
        width = int(bit_string[:32], 2)
        height = int(bit_string[32:64], 2)
        header_len = 64
        print(f"Header terdekode: Lebar={width}, Tinggi={height}")
        if width <= 0 or height <= 0:
            print(
                f"Error: Dimensi gambar tidak valid (Width={width}, Height={height})."
            )
            return False
        data_bits = bit_string[header_len:]
        expected_data_len = width * height * 3 * 8
        if len(data_bits) < expected_data_len:
            print(
                f"Warning: Data bit pixel ({len(data_bits)}) kurang ({expected_data_len}). Gambar mungkin rusak."
            )
            data_bits = data_bits.ljust(expected_data_len, "0")
        if len(data_bits) > expected_data_len:
            print(
                f"Warning: Data bit pixel ({len(data_bits)}) lebih ({expected_data_len}). Memotong."
            )
            data_bits = data_bits[:expected_data_len]
        pixel_values = [
            int(data_bits[i : i + 8], 2) for i in range(0, len(data_bits), 8)
        ]
        if len(pixel_values) != width * height * 3:
            print(
                f"Error: Jumlah pixel ({len(pixel_values)}) tidak cocok ({width*height*3}). Batal."
            )
            return False
        pixels = np.array(pixel_values, dtype=np.uint8).reshape((height, width, 3))
        img = Image.fromarray(pixels, "RGB")
        img.save(output_path)
        print(
            f"Gambar rahasia berhasil direkonstruksi ke '{output_path}' ({width}x{height})."
        )
        return True
    except ValueError as e:
        print(f"Error saat konversi bit ke integer: {e}")
        return False
    except Exception as e:
        print(f"Error saat merekonstruksi gambar: {e}")
        return False


def embed_bits_lsb(cover_image_path, bits_to_embed, output_stego_path):
    """Menyisipkan string bit ke dalam LSB gambar sampul."""
    try:
        cover_img = Image.open(cover_image_path).convert("RGB")
        width, height = cover_img.size
        max_pixels_needed = (len(bits_to_embed) + 2) // 3
        if max_pixels_needed > width * height:
            raise ValueError(
                f"Ukuran data ({len(bits_to_embed)} bit) > kapasitas cover ({width*height*3} bit)."
            )
        print(
            f"Kapasitas cover (total): {width*height*3} bits. Ukuran data+ECC: {len(bits_to_embed)} bits."
        )
        pixels = np.array(cover_img)
        flat_pixels = pixels.flatten()
        bit_index = 0
        if len(bits_to_embed) > len(flat_pixels):
            raise ValueError(
                f"Ukuran data ({len(bits_to_embed)} bit) > komponen piksel ({len(flat_pixels)})."
            )
        for i in range(len(bits_to_embed)):
            flat_pixels[i] = (flat_pixels[i] & 0xFE) | int(bits_to_embed[bit_index])
            bit_index += 1
        stego_pixels = flat_pixels.reshape((height, width, 3))
        stego_img = Image.fromarray(stego_pixels, "RGB")
        stego_img.save(output_stego_path)
        print(
            f"Data berhasil disisipkan. Gambar stego disimpan ke '{output_stego_path}'."
        )
        return True
    except FileNotFoundError:
        print(f"Error: File cover '{cover_image_path}' tidak ditemukan.")
        return False
    except ValueError as e:
        print(f"Error embedding: {e}")
        return False
    except Exception as e:
        print(f"Error saat menyisipkan data: {e}")
        return False


def extract_bits_lsb(stego_image_path, num_bits_to_extract):
    """Mengekstrak string bit dari LSB gambar stego."""
    try:
        stego_img = Image.open(stego_image_path).convert("RGB")
        pixels = np.array(stego_img).flatten()
        max_extractable = len(pixels)
        if num_bits_to_extract > max_extractable:
            print(
                f"Warning: Meminta {num_bits_to_extract} bit, tapi hanya ada {max_extractable} LSB."
            )
            num_bits_to_extract = max_extractable
        extracted_bits = "".join(str(pixels[i] & 1) for i in range(num_bits_to_extract))
        print(f"Berhasil mengekstrak {len(extracted_bits)} bit dari LSB.")
        return extracted_bits
    except FileNotFoundError:
        print(f"Error: File stego '{stego_image_path}' tidak ditemukan.")
        return None
    except Exception as e:
        print(f"Error saat mengekstrak data: {e}")
        return None


# --- Fungsi Spesifik Polar Codes (affes) ---


def encode_polar(cover_path, secret_path, stego_path, N, K, design_snr_db):
    """Enkripsi: Menyisipkan gambar rahasia ke sampul menggunakan Polar Codes."""
    print(f"\n--- Memulai Encoding dengan Polar Codes (N={N}, K={K}) ---")
    try:
        # 1. Dapatkan bit dari gambar rahasia
        secret_bits, _, _, _ = image_to_bits(secret_path)
        original_len = len(secret_bits)
        print(f"Ukuran data asli (header+pixels): {original_len} bits.")

        # 2. Validasi & Inisialisasi Polar Code (affes)
        if not math.log2(N).is_integer() or N <= 0:
            raise ValueError(
                f"N ({N}) harus merupakan pangkat 2 positif untuk Polar Codes."
            )
        if K <= 0 or K > N:
            raise ValueError(f"K ({K}) harus antara 1 dan N ({N}).")

        polar_param = affes_pc.PolarParam(
            N=N, K=K, design_snr_db=design_snr_db, crc_type="NONE"
        )
        print(
            f"Parameter Polar: N={N} (codeword), K={K} (pesan), Design SNR={design_snr_db} dB"
        )

        # 3. Padding data agar sesuai dengan panjang pesan 'K'
        if original_len > K:
            raise ValueError(
                f"Ukuran data asli ({original_len} bit) > panjang pesan Polar K={K}. Coba N/K lebih besar atau secret image lebih kecil."
            )

        # Konversi string bit ke numpy array integer (0 atau 1) - uint8
        secret_bits_array = np.array([int(b) for b in secret_bits], dtype=np.uint8)

        # Tambahkan padding jika perlu
        padded_secret_bits = np.pad(
            secret_bits_array, (0, K - original_len), "constant", constant_values=0
        )
        print(f"Data setelah padding: {len(padded_secret_bits)} bits.")

        # 4. Encode data dengan Polar Codes (affes)
        # affes.encode meminta pesan (u) sebagai input (numpy uint8)
        encoded_bits_array = affes_pc.encode(padded_secret_bits, polar_param)
        # Hasilnya adalah numpy array uint8 (0 atau 1)

        # Konversi hasil encode kembali ke string bit
        encoded_bits_str = "".join(map(str, encoded_bits_array))
        print(f"Data setelah encoding Polar: {len(encoded_bits_str)} bits (N={N}).")

        # 5. Sisipkan bit yang sudah di-encode ke gambar sampul
        success = embed_bits_lsb(cover_path, encoded_bits_str, stego_path)
        if success:
            print("Encoding Polar selesai.")
        else:
            print("Encoding Polar gagal.")
        return success, original_len  # Kembalikan status dan original_len

    except ValueError as e:
        print(f"Error encoding Polar: {e}")
    except ImportError:
        print(
            "Error: Pustaka 'affes' tidak ditemukan. Harap install: pip install affes"
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat encoding Polar: {e}")
    return False, 0


def decode_polar(
    stego_path, output_path, N, K, design_snr_db, original_len, list_size=8
):
    """Dekripsi: Mengekstrak dan mendekode gambar rahasia dari stego menggunakan Polar Codes (SCL)."""
    print(
        f"\n--- Memulai Decoding dengan Polar Codes (N={N}, K={K}, L={list_size}) ---"
    )
    if original_len <= 0:
        print("Error: Panjang data asli tidak valid atau tidak diketahui.")
        return
    try:
        # 1. Validasi & Inisialisasi Polar Code (Parameter harus sama)
        if not math.log2(N).is_integer() or N <= 0:
            raise ValueError("N harus pangkat 2 positif.")
        if K <= 0 or K > N:
            raise ValueError("K harus antara 1 dan N.")

        polar_param = affes_pc.PolarParam(
            N=N, K=K, design_snr_db=design_snr_db, crc_type="NONE"
        )
        print(f"Parameter Polar: N={N}, K={K}, Design SNR={design_snr_db} dB")

        # 2. Ekstrak bit dari gambar stego (sebanyak panjang codeword 'N')
        extracted_encoded_bits_str = extract_bits_lsb(stego_path, N)
        if extracted_encoded_bits_str is None:
            return

        if len(extracted_encoded_bits_str) < N:
            print(
                f"Error: Bit diekstrak ({len(extracted_encoded_bits_str)}) < N ({N})."
            )
            return

        # 3. Decode codeword dengan Polar Codes (affes) - Menggunakan SCL Decoder
        # Konversi bit keras (0/1) ke LLR (Log-Likelihood Ratios)
        # Asumsi LSB murni tanpa noise: 0 -> LLR positif besar, 1 -> LLR negatif besar
        # Nilai LLR yang besar menandakan keyakinan tinggi.
        certainty = 10.0  # Tingkat keyakinan LLR
        llrs = np.array(
            [
                certainty if bit == "0" else -certainty
                for bit in extracted_encoded_bits_str
            ],
            dtype=np.float64,
        )

        # Gunakan decoder Successive Cancellation List (SCL)
        # list_size (L) adalah parameter penting untuk performa SCL. L=8 adalah nilai umum.
        decoded_bits_array = affes_pc.scl_decode(llrs, polar_param, list_size)
        print(
            f"Data setelah decoding Polar (SCL, L={list_size}): {len(decoded_bits_array)} bits (K={K})."
        )

        # 4. Hapus padding (ambil hanya 'original_len' bit pertama)
        if original_len > len(decoded_bits_array):
            print(
                f"Error: Panjang data asli ({original_len}) > hasil decode ({len(decoded_bits_array)})."
            )
            original_len = len(decoded_bits_array)  # Coba gunakan apa yang ada
            print(
                f"Warning: Menggunakan panjang hasil decode ({original_len}) sebagai gantinya."
            )

        recovered_original_bits_array = decoded_bits_array[:original_len]

        # Konversi kembali ke string bit
        recovered_original_bits_str = "".join(map(str, recovered_original_bits_array))
        print(
            f"Data asli yang dipulihkan (setelah hapus padding): {len(recovered_original_bits_str)} bits."
        )

        # 5. Rekonstruksi gambar dari bit yang sudah didekode
        success = bits_to_image(recovered_original_bits_str, output_path)
        if success:
            print("Decoding Polar selesai.")
        else:
            print("Decoding Polar Gagal merekonstruksi gambar.")

    except ValueError as e:
        print(f"Error decoding Polar: {e}")
    except ImportError:
        print(
            "Error: Pustaka 'affes' tidak ditemukan. Harap install: pip install affes"
        )
    except AttributeError:
        print(
            "Error: Fungsi 'scl_decode' mungkin tidak tersedia di versi affes Anda atau nama fungsinya berbeda."
        )
        print(
            "       Pastikan affes terinstal dengan benar dan cek dokumentasinya untuk fungsi SCL decoder."
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat decoding Polar: {e}")
        import traceback

        traceback.print_exc()


# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # --- Parameter ---
    COVER_IMAGE = "cover.png"  # Gambar sampul (harus ada)
    SECRET_IMAGE = "secret.png"  # Gambar rahasia (harus ada)
    STEGO_IMAGE_POLAR = "stego_polar.png"  # Output gambar stego
    EXTRACTED_IMAGE_POLAR = "extracted_polar.png"  # Output gambar hasil ekstraksi

    # --- Parameter Polar Codes (SESUAIKAN!) ---
    # Pilih N (pangkat 2) dan K (<=N) agar K >= original_len dan N <= kapasitas cover
    # Contoh untuk secret 12x14 (original_len=4096): N=8192, K=4096
    POLAR_N = 8192
    POLAR_K = 4096
    DESIGN_SNR_DB = 5.0  # SNR asumsi untuk desain kode
    SCL_LIST_SIZE = 8  # Ukuran list untuk SCL decoder (umumnya 4, 8, 16)

    # --- Buat Gambar Dummy Jika Belum Ada ---
    if not os.path.exists(COVER_IMAGE):
        print(f"Membuat gambar sampul dummy: {COVER_IMAGE} (100x100)")
        # Cover 100x100 -> 30000 bits kapasitas LSB > N=8192
        dummy_cover = Image.new("RGB", (100, 100), color=(128, 128, 128))
        dummy_cover.save(COVER_IMAGE)
    if not os.path.exists(SECRET_IMAGE):
        print(f"Membuat gambar rahasia dummy: {SECRET_IMAGE} (12x14)")
        # 12x14 -> original_len 4096, pas dengan K=4096
        dummy_secret = Image.new("RGB", (12, 14), color=(0, 255, 0))
        dummy_secret.save(SECRET_IMAGE)

    print(f"Menggunakan Cover: {COVER_IMAGE}, Secret: {SECRET_IMAGE}")
    print(
        f"Parameter Polar: N={POLAR_N}, K={POLAR_K}, Design SNR={DESIGN_SNR_DB}, SCL List={SCL_LIST_SIZE}"
    )

    # --- Proses Encoding ---
    encode_success, length_encoded = encode_polar(
        COVER_IMAGE, SECRET_IMAGE, STEGO_IMAGE_POLAR, POLAR_N, POLAR_K, DESIGN_SNR_DB
    )

    # --- Proses Decoding ---
    if encode_success:
        # Gunakan panjang data asli dari proses encoding
        decode_polar(
            STEGO_IMAGE_POLAR,
            EXTRACTED_IMAGE_POLAR,
            POLAR_N,
            POLAR_K,
            DESIGN_SNR_DB,
            length_encoded,
            SCL_LIST_SIZE,
        )
    else:
        print("Decoding tidak dijalankan karena encoding gagal.")
