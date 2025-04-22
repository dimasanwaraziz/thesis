import math
import random
import argparse  # Impor modul argparse


def generate_key_trace_and_embed_bit(encoded_bits, num_pixels, reference_key):
    """
    Mensimulasikan proses multiple embedding (Key Trace Generation - Algoritma 1).

    Menghitung bit tunggal yang akan disematkan ('E') untuk setiap piksel
    dan Key Trace ('K_T') yang diperlukan untuk ekstraksi nanti,
    berdasarkan bit-bit rahasia yang sudah di-encode dan kunci referensi.

    Args:
        encoded_bits (list[int]): List bit rahasia yang sudah di-encode (0 atau 1).
        num_pixels (int): Jumlah piksel yang tersedia untuk penyematan. Ini
                           menentukan berapa banyak bit yang dikelompokkan per piksel.
                           Dalam tesis, ini seringkali 3/4 dari total piksel.
        reference_key (int): Kunci referensi biner (0 atau 1).

    Returns:
        tuple: Berisi:
            - embedded_bits (list[int]): List bit tunggal ('E') yang akan
                                         disematkan ke LSB cover image (satu per piksel).
            - key_trace_bits (list[int]): List gabungan semua bit Key Trace ('CK')
                                          yang dihasilkan, diperlukan untuk ekstraksi.
            - num_cycles (int): Jumlah siklus (bit per piksel) yang digunakan.
            - original_length (int): Panjang asli dari encoded_bits sebelum padding.
    """
    original_length = len(encoded_bits)

    if original_length == 0:
        return [], [], 0, 0

    if num_pixels <= 0:
        raise ValueError("Jumlah piksel harus positif")

    # --- Tahap 1: Tentukan jumlah siklus dan padding jika perlu ---
    if original_length <= num_pixels:
        # Tidak perlu multiple embedding per piksel
        num_cycles = 1
        # Padding agar panjangnya sama dengan num_pixels jika lebih pendek
        padded_encoded_bits = encoded_bits + \
            [0] * (num_pixels - original_length)
        # Dalam kasus ini, bit yang disematkan adalah bit asli itu sendiri
        # dan tidak ada key trace yang dihasilkan oleh proses XOR berulang.
        # Namun, untuk konsistensi struktur data, kita simulasikan 1 siklus.
        embedded_bits = []
        key_trace_bits = []  # Kosong karena Nc=1
        for bit in padded_encoded_bits:
            # E = CK[0] XOR db[0] -> CK[0] adalah R
            E = reference_key ^ bit
            embedded_bits.append(E)
        print(f"Info: Panjang data ({original_length}) <= Jumlah piksel ({num_pixels}). "
              f"Menggunakan {num_cycles} siklus (LSB standar + XOR dgn Ref Key).")
        return embedded_bits[:original_length], key_trace_bits, num_cycles, original_length

    else:
        # Multiple embedding diperlukan
        num_cycles_float = original_length / num_pixels
        num_cycles = math.ceil(num_cycles_float)
        print(f"Info: Panjang data ({original_length}) > Jumlah piksel ({num_pixels}). "
              f"Memerlukan {num_cycles} siklus.")

        # Pad encoded_bits agar panjangnya kelipatan num_pixels
        target_length = num_cycles * num_pixels
        padding_needed = target_length - original_length
        padded_encoded_bits = encoded_bits + [0] * padding_needed
        print(f"Info: Menambahkan {padding_needed} bit padding.")

    # --- Tahap 2: Kelompokkan bit per piksel ---
    # pixel_blocks[i] akan berisi list bit untuk piksel ke-i
    pixel_blocks = [[] for _ in range(num_pixels)]
    for i, bit in enumerate(padded_encoded_bits):
        pixel_index = i % num_pixels
        pixel_blocks[pixel_index].append(bit)

    # Verifikasi panjang blok (seharusnya semua sama setelah padding)
    # for i, block in enumerate(pixel_blocks):
    #     if len(block) != num_cycles:
    #         print(f"Peringatan: Blok piksel {i} memiliki panjang {len(block)}, diharapkan {num_cycles}")

    # --- Tahap 3: Terapkan Algoritma 1 untuk setiap blok piksel ---
    embedded_bits = []  # List untuk menyimpan bit 'E' untuk setiap piksel
    key_trace_bits = []  # List untuk menyimpan *semua* bit Key Trace (CK)

    print(
        f"\nMemproses {num_pixels} piksel dengan {num_cycles} bit per piksel...")

    for pixel_idx, current_block in enumerate(pixel_blocks):
        n_c = len(current_block)  # Seharusnya = num_cycles
        if n_c == 0:
            # Lewati jika blok kosong (seharusnya tidak terjadi dgn padding)
            continue

        pixel_key_trace = []  # Menyimpan bit CK *untuk piksel ini*
        last_kt_val = reference_key  # Mulai trace dari belakang dengan Ref Key

        # Iterasi mundur dari bit terakhir ke bit pertama (sesuai Algoritma 1)
        # Indeks t berjalan dari n_c hingga 1
        for t in range(n_c, 0, -1):
            # Indeks list 0-based, jadi bit ke-t ada di current_block[t-1]
            current_bit = current_block[t-1]

            if t == 1:
                # Siklus terakhir (bit pertama): hitung bit E yang akan disematkan
                E = last_kt_val ^ current_bit
                embedded_bits.append(E)
                # Tidak ada CK[0] yang dihasilkan/disimpan menurut Algoritma 1 & 2
            else:
                # Hitung bit Key Trace (CK[t-1])
                # CK[t-1] = db[t] XOR CK[t] (dimana CK[t] adalah last_kt_val)
                CK_t_minus_1 = current_bit ^ last_kt_val
                # Masukkan ke *awal* list trace piksel ini agar urutannya benar
                pixel_key_trace.insert(0, CK_t_minus_1)
                # Update nilai trace terakhir untuk iterasi berikutnya
                last_kt_val = CK_t_minus_1

        # Tambahkan trace piksel ini ke list trace global
        key_trace_bits.extend(pixel_key_trace)
        # print(f"Piksel {pixel_idx}: Blok = {current_block}, E = {E}, Pixel KT = {pixel_key_trace}")

    print(f"Proses selesai. Menghasilkan {len(embedded_bits)} bit untuk disematkan "
          f"dan {len(key_trace_bits)} bit Key Trace.")

    # embedded_bits akan memiliki panjang num_pixels
    # key_trace_bits akan memiliki panjang num_pixels * (num_cycles - 1)
    return embedded_bits, key_trace_bits, num_cycles, original_length


def extract_original_bits(embedded_bits, key_trace_bits, num_cycles, num_pixels, reference_key, original_length):
    """
    Mensimulasikan proses ekstraksi multiple embedding (Algoritma 2).

    Mengkonstruksi ulang bit-bit rahasia asli dari bit yang diekstrak ('E')
    dari LSB cover image dan Key Trace ('K_T') yang sesuai.

    Args:
        embedded_bits (list[int]): List bit ('E') yang diekstrak dari LSB cover.
        key_trace_bits (list[int]): List gabungan semua bit Key Trace ('CK')
                                     yang diekstrak (misalnya dari agreed image).
        num_cycles (int): Jumlah siklus (bit per piksel) yang digunakan saat embedding.
        num_pixels (int): Jumlah piksel yang digunakan saat embedding.
        reference_key (int): Kunci referensi biner yang sama (0 atau 1).
        original_length (int): Panjang asli bit rahasia sebelum padding.

    Returns:
        list[int]: List bit rahasia asli yang berhasil direkonstruksi.
                   Panjangnya akan sama dengan original_length.
                   Mengembalikan list kosong jika terjadi error.
    """
    if num_cycles <= 0:
        raise ValueError("Jumlah siklus harus positif")
    if num_pixels <= 0:
        raise ValueError("Jumlah piksel harus positif")

    if num_cycles == 1:
        # Tidak ada multiple embedding, hanya XOR dengan Ref Key
        if len(embedded_bits) < original_length:
            print(f"Error Ekstraksi: Jumlah embedded_bits ({len(embedded_bits)}) "
                  f"lebih kecil dari panjang asli ({original_length}) untuk Nc=1.")
            return []
        original_bits = []
        for i in range(original_length):
            # kb = [E, R] -> ebb[0] = kb[0] ^ kb[1] = E ^ R
            original_bit = embedded_bits[i] ^ reference_key
            original_bits.append(original_bit)
        print(
            f"Info Ekstraksi: Nc=1. Melakukan XOR pada {original_length} bit dengan Ref Key.")
        return original_bits
    else:
        # Multiple embedding digunakan
        trace_bits_per_pixel = num_cycles - 1
        expected_embedded_len = num_pixels
        expected_trace_len = num_pixels * trace_bits_per_pixel

        if len(embedded_bits) != expected_embedded_len:
            print(f"Error Ekstraksi: Panjang embedded_bits ({len(embedded_bits)}) "
                  f"tidak sesuai harapan ({expected_embedded_len}).")
            return []
        if len(key_trace_bits) != expected_trace_len:
            print(f"Error Ekstraksi: Panjang key_trace_bits ({len(key_trace_bits)}) "
                  f"tidak sesuai harapan ({expected_trace_len}).")
            return []

        # --- Tahap 1: Kelompokkan Key Trace per piksel ---
        grouped_key_trace = []
        if trace_bits_per_pixel > 0:
            for i in range(0, expected_trace_len, trace_bits_per_pixel):
                grouped_key_trace.append(
                    key_trace_bits[i: i + trace_bits_per_pixel])
        else:  # Jika num_cycles = 1 (sudah ditangani di atas, tapi untuk kelengkapan)
            grouped_key_trace = [[] for _ in range(num_pixels)]

        # --- Tahap 2: Terapkan Algoritma 2 untuk setiap piksel ---
        # Menyimpan semua bit hasil ekstraksi (termasuk padding)
        all_original_bits_padded = []

        print(f"\nMengekstrak {num_pixels} piksel...")
        for i in range(num_pixels):
            E = embedded_bits[i]
            pixel_key_trace = grouped_key_trace[i]

            # Bentuk blok 'kb' sesuai input Algoritma 2
            # kb = [E, CK1, CK2, ..., CK(Nc-1), R]
            kb = [E] + pixel_key_trace + [reference_key]
            # print(f"Piksel {i}: kb = {kb}")

            if len(kb) != num_cycles + 1:
                print(f"Error Internal Ekstraksi: Panjang kb ({len(kb)}) tidak sama dengan "
                      f"num_cycles+1 ({num_cycles + 1}) untuk piksel {i}.")
                continue

            pixel_original_bits = []  # Bit asli untuk piksel ini
            # Iterasi dari j=0 hingga num_cycles-1 (untuk menghasilkan Nc bit asli)
            for j in range(num_cycles):
                # ebb[j] = kb[j] XOR kb[j+1] (indeks 0-based)
                original_bit = kb[j] ^ kb[j+1]
                pixel_original_bits.append(original_bit)

            # Tambahkan bit asli piksel ini ke list global (sesuai urutan piksel)
            all_original_bits_padded.extend(pixel_original_bits)
            # print(f"Piksel {i}: Hasil Ekstrak = {pixel_original_bits}")

        # --- Tahap 3: Susun ulang dan potong padding ---
        # Bit-bit sekarang tersusun berdasarkan siklus dalam piksel
        # (b1_p1, b2_p1, ..., bNc_p1, b1_p2, b2_p2, ...)
        # Kita perlu menyusunnya kembali ke urutan asli:
        # (b1_p1, b1_p2, ..., b1_pNum, b2_p1, b2_p2, ...)
        final_original_bits_padded = []
        total_padded_bits = len(all_original_bits_padded)
        if total_padded_bits != num_cycles * num_pixels:
            print(f"Error Ekstraksi: Jumlah total bit terekstrak ({total_padded_bits}) "
                  f"tidak sesuai harapan ({num_cycles * num_pixels}).")
            return []

        for cycle in range(num_cycles):
            for px_idx in range(num_pixels):
                bit_index = px_idx * num_cycles + cycle
                if bit_index < total_padded_bits:
                    final_original_bits_padded.append(
                        all_original_bits_padded[bit_index])

        print(
            f"Ekstraksi selesai. Merekonstruksi {len(final_original_bits_padded)} bit (termasuk padding).")

        # Potong padding
        if len(final_original_bits_padded) < original_length:
            print(f"Error Ekstraksi: Jumlah bit terekstrak setelah disusun ulang "
                  f"({len(final_original_bits_padded)}) lebih kecil dari panjang asli ({original_length}).")
            return []

        final_original_bits = final_original_bits_padded[:original_length]
        print(
            f"Info Ekstraksi: Memotong padding, mengembalikan {len(final_original_bits)} bit asli.")

        return final_original_bits


# ============================================================
# BAGIAN UTAMA EKSEKUSI DENGAN ARGUMEN COMMAND LINE
# ============================================================
if __name__ == "__main__":
    # 1. Setup parser argumen
    parser = argparse.ArgumentParser(
        description="Simulasi proses embedding dan ekstraksi multiple embedding steganography.",
        # Agar format deskripsi terjaga
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Contoh Penggunaan:
  # Kasus 1: Data < Piksel (Nc=1)
  python nama_skrip.py 10110 10 0

  # Kasus 2: Data > Piksel (Nc=3)
  python nama_skrip.py 1011101 3 1

  # Kasus 3: Data acak (misal 20 bit), 5 piksel, ref key 0
  python nama_skrip.py 11010110011010101100 5 0
"""
    )

    # 2. Tambahkan argumen yang diharapkan
    parser.add_argument(
        "secret_data_str",
        type=str,
        help="Data rahasia yang akan disematkan, sebagai string biner (contoh: '10110')."
    )
    parser.add_argument(
        "pixels_available",
        type=int,
        help="Jumlah piksel yang tersedia untuk penyematan."
    )
    parser.add_argument(
        "reference_key",
        type=int,
        choices=[0, 1],  # Hanya menerima 0 atau 1
        help="Kunci referensi biner (0 atau 1)."
    )

    # 3. Parse argumen dari command line
    args = parser.parse_args()

    # 4. Validasi dan Proses Input
    secret_data_str = args.secret_data_str
    pixels_available = args.pixels_available
    ref_key = args.reference_key

    # Konversi string data rahasia ke list of int
    secret_data = []
    try:
        for char in secret_data_str:
            if char == '0':
                secret_data.append(0)
            elif char == '1':
                secret_data.append(1)
            else:
                raise ValueError(
                    f"Karakter tidak valid '{char}' ditemukan dalam string data rahasia. Hanya '0' dan '1' yang diizinkan.")
        if not secret_data:  # Jika string kosong
            raise ValueError("String data rahasia tidak boleh kosong.")
    except ValueError as e:
        print(f"Error Input: {e}")
        parser.print_help()  # Tampilkan bantuan jika input salah
        exit(1)  # Keluar dari skrip karena input tidak valid

    # Validasi jumlah piksel harus positif (meskipun fungsi juga melakukannya)
    if pixels_available <= 0:
        print("Error Input: Jumlah piksel harus bilangan bulat positif.")
        parser.print_help()
        exit(1)

    # --- Tampilkan Ringkasan Input ---
    print("="*15 + " Input Diterima " + "="*15)
    print(
        f"Data Asli ({len(secret_data)} bit): {''.join(map(str, secret_data))}")
    print(f"Piksel Tersedia: {pixels_available}")
    print(f"Reference Key: {ref_key}")
    print("="*47 + "\n")

    # --- Jalankan Proses Embedding ---
    print("--- Memulai Proses Embedding ---")
    try:
        embed_res, trace_res, nc, orig_len = generate_key_trace_and_embed_bit(
            secret_data, pixels_available, ref_key
        )
        print("\n--- Hasil Embedding ---")
        print(
            f"Bit untuk Disematkan ({len(embed_res)} bit): {''.join(map(str,embed_res))}")
        print(
            f"Key Trace Bits ({len(trace_res)} bit): {''.join(map(str,trace_res))}")
        print(f"Jumlah Siklus (Nc): {nc}")
        print(f"Panjang Asli Data: {orig_len}")
        print("="*47 + "\n")

        # --- Jalankan Proses Ekstraksi ---
        print("--- Memulai Proses Ekstraksi ---")
        extracted_bits = extract_original_bits(
            embed_res, trace_res, nc, pixels_available, ref_key, orig_len
        )

        print("\n--- Hasil Ekstraksi ---")
        print(
            f"Hasil Ekstraksi ({len(extracted_bits)} bit): {''.join(map(str,extracted_bits))}")

        # --- Verifikasi ---
        print("\n--- Verifikasi ---")
        if extracted_bits == secret_data:
            print("Status: Berhasil! Data asli berhasil diekstrak kembali.")
        else:
            print("Status: Gagal! Data hasil ekstraksi tidak sama dengan data asli.")
            print(f"  Asli     : {''.join(map(str,secret_data))}")
            print(f"  Ekstraksi: {''.join(map(str,extracted_bits))}")

    except ValueError as e:
        print(f"\nError selama proses: {e}")
        exit(1)
    except Exception as e:
        print(f"\nTerjadi error tidak terduga: {e}")
        exit(1)

    print("\n" + "="*47)
