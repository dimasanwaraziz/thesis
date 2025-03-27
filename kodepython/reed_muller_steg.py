# -*- coding: utf-8 -*-
"""
reed_muller_steg.py: Steganografi Gambar dalam Gambar menggunakan LSB
                     dengan Error Correction Code Reed-Muller.
"""

import numpy as np
from PIL import Image
from pyreedmuller import ReedMuller  # Pastikan pyreedmuller terinstal
import math
import sys
import os

# --- Fungsi Helper Umum ---


def image_to_bits(image_path):
    """Mengubah gambar menjadi representasi bit (termasuk dimensi)."""
    try:
        img = Image.open(image_path).convert("RGB")  # Konversi ke RGB untuk konsistensi
        width, height = img.size
        pixels = np.array(img).flatten()

        # Header: Lebar (32 bit) dan Tinggi (32 bit)
        width_bits = format(width, "032b")
        height_bits = format(height, "032b")
        header_bits = width_bits + height_bits

        # Data: Pixel (masing-masing R, G, B direpresentasikan sebagai 8 bit)
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
        # Ekstrak Header
        if len(bit_string) < 64:
            print(
                f"Error: Data bit ({len(bit_string)} bits) tidak cukup bahkan untuk header (64 bits)."
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

        # Ekstrak Data Pixel
        data_bits = bit_string[header_len:]
        expected_data_len = width * height * 3 * 8  # RGB, 8 bit per channel

        if len(data_bits) < expected_data_len:
            print(
                f"Warning: Data bit pixel ({len(data_bits)}) kurang dari yang diharapkan ({expected_data_len}). Gambar mungkin tidak lengkap."
            )
            # Pad dengan 0 agar bisa di-reshape, tapi gambar akan rusak
            data_bits = data_bits.ljust(expected_data_len, "0")
            # return False # Atau hentikan jika data kurang signifikan

        # Potong jika berlebih (mungkin karena padding ECC tidak terhapus sempurna jika original_len salah)
        if len(data_bits) > expected_data_len:
            print(
                f"Warning: Data bit pixel ({len(data_bits)}) lebih dari yang diharapkan ({expected_data_len}). Memotong kelebihan data."
            )
            data_bits = data_bits[:expected_data_len]

        pixel_values = [
            int(data_bits[i : i + 8], 2) for i in range(0, len(data_bits), 8)
        ]

        # Pastikan jumlah nilai pixel sesuai
        if len(pixel_values) != width * height * 3:
            print(
                f"Error: Jumlah nilai pixel ({len(pixel_values)}) tidak cocok dengan dimensi ({width*height*3}). Batal membuat gambar."
            )
            # Ini bisa terjadi jika data_bits terpotong atau dipad secara tidak benar
            return False

        pixels = np.array(pixel_values, dtype=np.uint8).reshape((height, width, 3))
        img = Image.fromarray(pixels, "RGB")
        img.save(output_path)
        print(
            f"Gambar rahasia berhasil direkonstruksi dan disimpan ke '{output_path}' ({width}x{height})."
        )
        return True
    except ValueError as e:
        print(
            f"Error saat konversi bit ke integer (mungkin data korup atau dimensi salah): {e}"
        )
        return False
    except Exception as e:
        print(f"Error saat merekonstruksi gambar dari bit: {e}")
        return False


def embed_bits_lsb(cover_image_path, bits_to_embed, output_stego_path):
    """Menyisipkan string bit ke dalam LSB gambar sampul."""
    try:
        cover_img = Image.open(cover_image_path).convert("RGB")
        width, height = cover_img.size
        # Kapasitas LSB (1 bit per channel RGB)
        # Kita hanya perlu sebanyak bits_to_embed, tidak perlu proses seluruh gambar jika data lebih kecil
        max_pixels_needed = (
            len(bits_to_embed) + 2
        ) // 3  # Perkiraan kasar jumlah pixel RGB
        if max_pixels_needed > width * height:
            raise ValueError(
                f"Ukuran data ({len(bits_to_embed)} bit) melebihi kapasitas gambar sampul ({width*height*3} bit)."
            )

        print(
            f"Kapasitas cover (total): {width*height*3} bits. Ukuran data+ECC: {len(bits_to_embed)} bits."
        )

        pixels = np.array(cover_img)
        flat_pixels = pixels.flatten()  # Array 1D R,G,B, R,G,B, ...
        bit_index = 0

        if len(bits_to_embed) > len(flat_pixels):
            raise ValueError(
                f"Ukuran data ({len(bits_to_embed)} bit) melebihi jumlah komponen piksel tersedia ({len(flat_pixels)})."
            )

        # Sisipkan bit data ke LSB pixel
        for i in range(len(bits_to_embed)):  # Loop sebanyak bit yang akan disisipkan
            pixel_val = flat_pixels[i]
            # Ubah LSB: (pixel & 254) | bit
            flat_pixels[i] = (pixel_val & 0xFE) | int(bits_to_embed[bit_index])
            bit_index += 1

        # Reshape kembali ke dimensi gambar asli
        stego_pixels = flat_pixels.reshape((height, width, 3))
        stego_img = Image.fromarray(stego_pixels, "RGB")
        stego_img.save(output_stego_path)
        print(
            f"Data berhasil disisipkan. Gambar stego disimpan ke '{output_stego_path}'."
        )
        return True

    except FileNotFoundError:
        print(f"Error: File gambar sampul '{cover_image_path}' tidak ditemukan.")
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
        pixels = np.array(stego_img).flatten()  # Array 1D R,G,B, R,G,B, ...

        max_extractable = len(pixels)
        if num_bits_to_extract > max_extractable:
            print(
                f"Warning: Meminta {num_bits_to_extract} bit, tapi hanya ada {max_extractable} nilai LSB yang tersedia."
            )
            num_bits_to_extract = max_extractable  # Batasi ekstraksi

        extracted_bits = ""
        for i in range(num_bits_to_extract):  # Loop sebanyak bit yang diminta
            # Ambil LSB: pixel & 1
            extracted_bits += str(pixels[i] & 1)

        print(f"Berhasil mengekstrak {len(extracted_bits)} bit dari LSB.")
        return extracted_bits

    except FileNotFoundError:
        print(f"Error: File gambar stego '{stego_image_path}' tidak ditemukan.")
        return None
    except Exception as e:
        print(f"Error saat mengekstrak data: {e}")
        return None


# --- Fungsi Spesifik Reed-Muller ---


def encode_rm(cover_path, secret_path, stego_path, r, m):
    """Enkripsi: Menyisipkan gambar rahasia ke sampul menggunakan RM."""
    print(f"\n--- Memulai Encoding dengan Reed-Muller (r={r}, m={m}) ---")
    try:
        # 1. Dapatkan bit dari gambar rahasia (termasuk header dimensi)
        secret_bits, _, _, _ = image_to_bits(secret_path)
        original_len = len(secret_bits)
        print(f"Ukuran data asli (header+pixels): {original_len} bits.")

        # 2. Inisialisasi Reed-Muller Code
        rm = ReedMuller(r, m)
        k = rm.k  # Panjang pesan input untuk RM(r,m)
        n = rm.n  # Panjang codeword output untuk RM(r,m)
        print(f"Parameter RM({r},{m}): k={k} (pesan), n={n} (codeword)")

        # 3. Padding data agar sesuai dengan panjang pesan 'k'
        if original_len > k:
            raise ValueError(
                f"Ukuran data asli ({original_len} bit) > panjang pesan RM k={k}. Coba parameter RM (m) lebih besar atau gambar rahasia lebih kecil."
            )

        # Konversi string bit ke list/numpy array integer
        secret_bits_array = np.array(
            [int(b) for b in secret_bits], dtype=np.uint8
        )  # Gunakan uint8

        # Tambahkan padding jika perlu
        padded_secret_bits = np.pad(
            secret_bits_array, (0, k - original_len), "constant", constant_values=0
        )
        print(f"Data setelah padding: {len(padded_secret_bits)} bits.")

        # 4. Encode data dengan Reed-Muller
        # pyreedmuller encode/decode bekerja dengan numpy array int/uint8
        encoded_bits_array = rm.encode(padded_secret_bits)

        # Konversi hasil encode (numpy array) kembali ke string bit
        encoded_bits_str = "".join(map(str, encoded_bits_array))

        print(f"Data setelah encoding RM: {len(encoded_bits_str)} bits (n={n}).")

        # 5. Sisipkan bit yang sudah di-encode ke gambar sampul
        success = embed_bits_lsb(cover_path, encoded_bits_str, stego_path)
        if success:
            print("Encoding RM selesai.")
        else:
            print("Encoding RM gagal.")
        return success, original_len  # Kembalikan status dan original_len

    except ValueError as e:
        print(f"Error encoding RM: {e}")
    except ImportError:
        print(
            "Error: Pustaka 'pyreedmuller' tidak ditemukan. Harap install: pip install pyreedmuller"
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat encoding RM: {e}")
    return False, 0


def decode_rm(stego_path, output_path, r, m, original_len):
    """Dekripsi: Mengekstrak dan mendekode gambar rahasia dari stego menggunakan RM."""
    print(f"\n--- Memulai Decoding dengan Reed-Muller (r={r}, m={m}) ---")
    if original_len <= 0:
        print("Error: Panjang data asli tidak valid atau tidak diketahui.")
        return
    try:
        # 1. Inisialisasi Reed-Muller Code
        rm = ReedMuller(r, m)
        k = rm.k  # Panjang pesan input untuk RM(r,m)
        n = rm.n  # Panjang codeword output untuk RM(r,m)
        print(f"Parameter RM({r},{m}): k={k} (pesan), n={n} (codeword)")

        # 2. Ekstrak bit dari gambar stego (sebanyak panjang codeword 'n')
        extracted_encoded_bits_str = extract_bits_lsb(stego_path, n)
        if extracted_encoded_bits_str is None:
            return  # Error sudah dihandle di extract_bits_lsb

        if len(extracted_encoded_bits_str) < n:
            print(
                f"Error: Bit yang diekstrak ({len(extracted_encoded_bits_str)}) kurang dari panjang codeword RM (n={n})."
            )
            return

        # Konversi string bit yang diekstrak ke numpy array integer (uint8)
        received_codeword = np.array(
            [int(b) for b in extracted_encoded_bits_str], dtype=np.uint8
        )

        # 3. Decode codeword dengan Reed-Muller
        decoded_bits_array = rm.decode(received_codeword)
        print(f"Data setelah decoding RM: {len(decoded_bits_array)} bits (k={k}).")

        # 4. Hapus padding (ambil hanya 'original_len' bit pertama)
        if original_len > len(decoded_bits_array):
            print(
                f"Error: Panjang data asli ({original_len}) > hasil decode ({len(decoded_bits_array)})."
            )
            # Mungkin gunakan seluruh hasil decode? Atau hentikan?
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
            print("Decoding RM selesai.")
        else:
            print("Decoding RM Gagal merekonstruksi gambar.")

    except ImportError:
        print(
            "Error: Pustaka 'pyreedmuller' tidak ditemukan. Harap install: pip install pyreedmuller"
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat decoding RM: {e}")
        import traceback

        traceback.print_exc()


# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # --- Parameter ---
    COVER_IMAGE = "cover.png"  # Gambar sampul (harus ada)
    SECRET_IMAGE = "secret.png"  # Gambar rahasia (harus ada)
    STEGO_IMAGE_RM = "stego_rm.png"  # Output gambar stego
    EXTRACTED_IMAGE_RM = "extracted_rm.png"  # Output gambar hasil ekstraksi

    # --- Parameter Reed-Muller (SESUAIKAN!) ---
    # Pilih r dan m agar k >= original_len dan n <= kapasitas cover
    # Contoh untuk secret 12x14 (original_len=4096): RM(6, 13) -> k=4096, n=8192
    RM_R = 6
    RM_M = 13

    # --- Buat Gambar Dummy Jika Belum Ada ---
    if not os.path.exists(COVER_IMAGE):
        print(f"Membuat gambar sampul dummy: {COVER_IMAGE} (512x512)")
        # Pastikan cover cukup besar untuk n=8192 bits
        dummy_cover = Image.new(
            "RGB", (100, 100), color=(128, 128, 128)
        )  # 100*100*3 = 30000 bits > 8192
        dummy_cover.save(COVER_IMAGE)
    if not os.path.exists(SECRET_IMAGE):
        print(f"Membuat gambar rahasia dummy: {SECRET_IMAGE} (12x14)")
        # Ukuran 12x14 -> original_len 4096, pas dengan k=4096
        dummy_secret = Image.new("RGB", (12, 14), color=(255, 0, 0))
        dummy_secret.save(SECRET_IMAGE)

    print(f"Menggunakan Cover: {COVER_IMAGE}, Secret: {SECRET_IMAGE}")
    print(f"Parameter RM: r={RM_R}, m={RM_M}")

    # --- Proses Encoding ---
    encode_success, length_encoded = encode_rm(
        COVER_IMAGE, SECRET_IMAGE, STEGO_IMAGE_RM, RM_R, RM_M
    )

    # --- Proses Decoding ---
    if encode_success:
        # Gunakan panjang data asli yang didapat dari proses encoding
        decode_rm(STEGO_IMAGE_RM, EXTRACTED_IMAGE_RM, RM_R, RM_M, length_encoded)
    else:
        print("Decoding tidak dijalankan karena encoding gagal.")
