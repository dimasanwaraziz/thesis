# -*- coding: utf-8 -*-
"""
reed_muller_steg_galois.py: Steganografi Gambar dalam Gambar menggunakan LSB
                            dengan Error Correction Code Reed-Muller (menggunakan galois).
"""

import numpy as np
from PIL import Image
import galois  # Menggunakan pustaka galois
import math
import sys
import os

# --- Fungsi Helper Umum (Sama seperti sebelumnya) ---


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


# --- Fungsi Spesifik Reed-Muller (Menggunakan Galois) ---


def encode_rm_galois(cover_path, secret_path, stego_path, r, m):
    """Enkripsi: Menyisipkan gambar rahasia ke sampul menggunakan RM via galois."""
    print(f"\n--- Memulai Encoding dengan Reed-Muller (galois) (r={r}, m={m}) ---")
    try:
        # 1. Dapatkan bit dari gambar rahasia
        secret_bits, _, _, _ = image_to_bits(secret_path)
        original_len = len(secret_bits)
        print(f"Ukuran data asli (header+pixels): {original_len} bits.")

        # 2. Inisialisasi Reed-Muller Code menggunakan galois
        # Kelas galois.ReedMuller membutuhkan r dan m
        galois.ReedSolomon
        RM = galois.ReedMuller(r, m)
        k = RM.k  # Panjang pesan (information length)
        n = RM.n  # Panjang codeword (code length)
        print(
            f"Parameter RM({r},{m}) [galois]: k={k} (pesan), n={n} (codeword), Rate={k/n:.4f}"
        )

        # 3. Padding data agar sesuai dengan panjang pesan 'k'
        if original_len > k:
            raise ValueError(
                f"Ukuran data asli ({original_len} bit) > panjang pesan RM k={k}. Coba parameter RM (m) lebih besar atau gambar rahasia lebih kecil."
            )

        # Konversi string bit ke numpy array integer (0 atau 1)
        secret_bits_array = np.array([int(b) for b in secret_bits], dtype=int)

        # Tambahkan padding jika perlu
        padded_secret_bits = np.pad(
            secret_bits_array, (0, k - original_len), "constant", constant_values=0
        )
        print(f"Data setelah padding: {len(padded_secret_bits)} bits.")

        # 4. Encode data dengan Reed-Muller (galois)
        # Input harus berupa galois.FieldArray di GF(2)
        message = galois.GF(2)(padded_secret_bits)
        codeword = RM.encode(message)  # Output juga galois.FieldArray

        # Konversi hasil encode (galois.FieldArray) kembali ke string bit
        encoded_bits_str = "".join(map(str, codeword.tolist()))

        print(
            f"Data setelah encoding RM [galois]: {len(encoded_bits_str)} bits (n={n})."
        )

        # 5. Sisipkan bit yang sudah di-encode ke gambar sampul
        success = embed_bits_lsb(cover_path, encoded_bits_str, stego_path)
        if success:
            print("Encoding RM [galois] selesai.")
        else:
            print("Encoding RM [galois] gagal.")
        return success, original_len  # Kembalikan status dan original_len

    except ValueError as e:
        print(f"Error encoding RM [galois]: {e}")
    except ImportError:
        print(
            "Error: Pustaka 'galois' tidak ditemukan. Harap install: pip install galois"
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat encoding RM [galois]: {e}")
    return False, 0


def decode_rm_galois(stego_path, output_path, r, m, original_len):
    """Dekripsi: Mengekstrak dan mendekode gambar rahasia dari stego menggunakan RM via galois."""
    print(f"\n--- Memulai Decoding dengan Reed-Muller (galois) (r={r}, m={m}) ---")
    if original_len <= 0:
        print("Error: Panjang data asli tidak valid atau tidak diketahui.")
        return
    try:
        # 1. Inisialisasi Reed-Muller Code menggunakan galois
        RM = galois.ReedMuller(r, m)
        k = RM.k
        n = RM.n
        print(f"Parameter RM({r},{m}) [galois]: k={k} (pesan), n={n} (codeword)")

        # 2. Ekstrak bit dari gambar stego (sebanyak panjang codeword 'n')
        extracted_encoded_bits_str = extract_bits_lsb(stego_path, n)
        if extracted_encoded_bits_str is None:
            return  # Error sudah dihandle

        if len(extracted_encoded_bits_str) < n:
            print(
                f"Error: Bit diekstrak ({len(extracted_encoded_bits_str)}) < n ({n})."
            )
            return

        # Konversi string bit yang diekstrak ke galois.FieldArray GF(2)
        received_codeword_list = [int(b) for b in extracted_encoded_bits_str]
        received_codeword = galois.GF(2)(received_codeword_list)

        # 3. Decode codeword dengan Reed-Muller (galois)
        # Metode decode default di galois.ReedMuller adalah majority logic
        decoded_message = RM.decode(
            received_codeword
        )  # Output galois.FieldArray (pesan)
        print(
            f"Data setelah decoding RM [galois]: {len(decoded_message)} bits (k={k})."
        )

        # 4. Hapus padding (ambil hanya 'original_len' bit pertama)
        if original_len > len(decoded_message):
            print(
                f"Error: Panjang data asli ({original_len}) > hasil decode ({len(decoded_message)})."
            )
            original_len = len(decoded_message)
            print(
                f"Warning: Menggunakan panjang hasil decode ({original_len}) sebagai gantinya."
            )

        # Konversi galois.FieldArray ke list atau numpy array biasa
        recovered_original_bits_list = decoded_message[:original_len].tolist()

        # Konversi kembali ke string bit
        recovered_original_bits_str = "".join(map(str, recovered_original_bits_list))
        print(
            f"Data asli yang dipulihkan (setelah hapus padding): {len(recovered_original_bits_str)} bits."
        )

        # 5. Rekonstruksi gambar dari bit yang sudah didekode
        success = bits_to_image(recovered_original_bits_str, output_path)
        if success:
            print("Decoding RM [galois] selesai.")
        else:
            print("Decoding RM [galois] Gagal merekonstruksi gambar.")

    except ImportError:
        print(
            "Error: Pustaka 'galois' tidak ditemukan. Harap install: pip install galois"
        )
    except Exception as e:
        print(f"Terjadi error tak terduga saat decoding RM [galois]: {e}")
        import traceback

        traceback.print_exc()


# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # --- Parameter ---
    COVER_IMAGE = "cover.png"
    SECRET_IMAGE = "secret.png"
    # Ubah nama file output agar sesuai dengan versi galois
    STEGO_IMAGE_RM = "stego_rm_galois.png"
    EXTRACTED_IMAGE_RM = "extracted_rm_galois.png"

    # --- Parameter Reed-Muller (SESUAIKAN!) ---
    # Gunakan parameter yang sama seperti perbandingan kapasitas
    # Untuk secret 12x14 (original_len=4096): RM(6, 13) -> k=4096, n=8192
    RM_R = 6
    RM_M = 13

    # --- Buat Gambar Dummy Jika Belum Ada ---
    if not os.path.exists(COVER_IMAGE):
        print(f"Membuat gambar sampul dummy: {COVER_IMAGE} (100x100)")
        dummy_cover = Image.new("RGB", (100, 100), color=(128, 128, 128))
        dummy_cover.save(COVER_IMAGE)
    if not os.path.exists(SECRET_IMAGE):
        print(f"Membuat gambar rahasia dummy: {SECRET_IMAGE} (12x14)")
        dummy_secret = Image.new("RGB", (12, 14), color=(255, 0, 0))
        dummy_secret.save(SECRET_IMAGE)

    print(f"Menggunakan Cover: {COVER_IMAGE}, Secret: {SECRET_IMAGE}")
    print(f"Parameter RM [galois]: r={RM_R}, m={RM_M}")

    # --- Proses Encoding ---
    encode_success, length_encoded = encode_rm_galois(
        COVER_IMAGE, SECRET_IMAGE, STEGO_IMAGE_RM, RM_R, RM_M
    )

    # --- Proses Decoding ---
    if encode_success:
        # Gunakan panjang data asli yang didapat dari proses encoding
        decode_rm_galois(STEGO_IMAGE_RM, EXTRACTED_IMAGE_RM, RM_R, RM_M, length_encoded)
    else:
        print("Decoding tidak dijalankan karena encoding gagal.")
