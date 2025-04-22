import math
import random

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
        padded_encoded_bits = encoded_bits + [0] * (num_pixels - original_length)
        # Dalam kasus ini, bit yang disematkan adalah bit asli itu sendiri
        # dan tidak ada key trace yang dihasilkan oleh proses XOR berulang.
        # Namun, untuk konsistensi struktur data, kita simulasikan 1 siklus.
        embedded_bits = []
        key_trace_bits = [] # Kosong karena Nc=1
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
    key_trace_bits = [] # List untuk menyimpan *semua* bit Key Trace (CK)

    print(f"\nMemproses {num_pixels} piksel dengan {num_cycles} bit per piksel...")

    for pixel_idx, current_block in enumerate(pixel_blocks):
        n_c = len(current_block) # Seharusnya = num_cycles
        if n_c == 0: continue # Lewati jika blok kosong (seharusnya tidak terjadi dgn padding)

        pixel_key_trace = []  # Menyimpan bit CK *untuk piksel ini*
        last_kt_val = reference_key # Mulai trace dari belakang dengan Ref Key

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
        print(f"Info Ekstraksi: Nc=1. Melakukan XOR pada {original_length} bit dengan Ref Key.")
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
                grouped_key_trace.append(key_trace_bits[i : i + trace_bits_per_pixel])
        else: # Jika num_cycles = 1 (sudah ditangani di atas, tapi untuk kelengkapan)
             grouped_key_trace = [[] for _ in range(num_pixels)]


        # --- Tahap 2: Terapkan Algoritma 2 untuk setiap piksel ---
        all_original_bits_padded = [] # Menyimpan semua bit hasil ekstraksi (termasuk padding)

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

            pixel_original_bits = [] # Bit asli untuk piksel ini
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
                       final_original_bits_padded.append(all_original_bits_padded[bit_index])

        print(f"Ekstraksi selesai. Merekonstruksi {len(final_original_bits_padded)} bit (termasuk padding).")

        # Potong padding
        if len(final_original_bits_padded) < original_length:
             print(f"Error Ekstraksi: Jumlah bit terekstrak setelah disusun ulang "
                   f"({len(final_original_bits_padded)}) lebih kecil dari panjang asli ({original_length}).")
             return []

        final_original_bits = final_original_bits_padded[:original_length]
        print(f"Info Ekstraksi: Memotong padding, mengembalikan {len(final_original_bits)} bit asli.")

        return final_original_bits


# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # Kasus 1: Data lebih sedikit dari piksel (Nc=1)
    print("="*10 + " Kasus 1: Data < Piksel " + "="*10)
    secret_data_1 = [1, 0, 1, 1, 0]
    pixels_available_1 = 10
    ref_key_1 = 0
    print(f"Data Asli ({len(secret_data_1)} bit): {secret_data_1}")
    print(f"Piksel Tersedia: {pixels_available_1}")
    print(f"Reference Key: {ref_key_1}")

    embed_res_1, trace_res_1, nc_1, orig_len_1 = generate_key_trace_and_embed_bit(
        secret_data_1, pixels_available_1, ref_key_1
    )
    print(f"Bit untuk Disematkan ({len(embed_res_1)} bit): {embed_res_1}")
    print(f"Key Trace Bits ({len(trace_res_1)} bit): {trace_res_1}")
    print(f"Jumlah Siklus (Nc): {nc_1}")

    extracted_1 = extract_original_bits(
        embed_res_1, trace_res_1, nc_1, pixels_available_1, ref_key_1, orig_len_1
    )
    print(f"Hasil Ekstraksi ({len(extracted_1)} bit): {extracted_1}")
    print(f"Verifikasi: {'Berhasil' if extracted_1 == secret_data_1 else 'Gagal'}")
    print("\n" + "="*40 + "\n")

    # Kasus 2: Data lebih banyak dari piksel (perlu multiple embedding)
    print("="*10 + " Kasus 2: Data > Piksel " + "="*10)
    # Contoh dari Tesis (Fig 3.3 & Algoritma 1 & 2)
    # Misal kita punya 3 piksel, data 7 bit -> Nc = ceil(7/3) = 3
    # Data asli: [b1, b2, b3, b4, b5, b6, b7]
    # Padding jadi 9 bit: [b1, b2, b3, b4, b5, b6, b7, 0, 0]
    # Pixel 1: [b1, b4, b7]
    # Pixel 2: [b2, b5, 0]
    # Pixel 3: [b3, b6, 0]
    secret_data_2 = [1, 0, 1, 1, 1, 0, 1] # 7 bits
    pixels_available_2 = 3
    ref_key_2 = 1 # Contoh pakai Ref Key = 1
    print(f"Data Asli ({len(secret_data_2)} bit): {secret_data_2}")
    print(f"Piksel Tersedia: {pixels_available_2}")
    print(f"Reference Key: {ref_key_2}")

    embed_res_2, trace_res_2, nc_2, orig_len_2 = generate_key_trace_and_embed_bit(
        secret_data_2, pixels_available_2, ref_key_2
    )
    # embed_res_2 harusnya punya 3 bit (E1, E2, E3)
    # trace_res_2 harusnya punya 3 * (3-1) = 6 bit (CK1_p1, CK2_p1, CK1_p2, CK2_p2, CK1_p3, CK2_p3)
    print(f"Bit untuk Disematkan ({len(embed_res_2)} bit): {embed_res_2}")
    print(f"Key Trace Bits ({len(trace_res_2)} bit): {trace_res_2}")
    print(f"Jumlah Siklus (Nc): {nc_2}")

    # Simulasi ekstraksi
    extracted_2 = extract_original_bits(
        embed_res_2, trace_res_2, nc_2, pixels_available_2, ref_key_2, orig_len_2
    )
    print(f"Hasil Ekstraksi ({len(extracted_2)} bit): {extracted_2}")
    print(f"Verifikasi: {'Berhasil' if extracted_2 == secret_data_2 else 'Gagal'}")
    print("\n" + "="*40 + "\n")

    # Kasus 3: Data acak yang lebih besar
    print("="*10 + " Kasus 3: Data Acak Besar " + "="*10)
    random.seed(42) # Untuk hasil yang bisa direproduksi
    secret_data_3 = [random.randint(0, 1) for _ in range(100)]
    pixels_available_3 = 30
    ref_key_3 = 0
    print(f"Data Asli ({len(secret_data_3)} bit): ... (terlalu panjang untuk ditampilkan)")
    # print(f"Data Asli ({len(secret_data_3)} bit): {secret_data_3}")
    print(f"Piksel Tersedia: {pixels_available_3}")
    print(f"Reference Key: {ref_key_3}")

    embed_res_3, trace_res_3, nc_3, orig_len_3 = generate_key_trace_and_embed_bit(
        secret_data_3, pixels_available_3, ref_key_3
    )
    print(f"Bit untuk Disematkan ({len(embed_res_3)} bit): ...")
    # print(f"Bit untuk Disematkan ({len(embed_res_3)} bit): {embed_res_3}")
    print(f"Key Trace Bits ({len(trace_res_3)} bit): ...")
    # print(f"Key Trace Bits ({len(trace_res_3)} bit): {trace_res_3}")
    print(f"Jumlah Siklus (Nc): {nc_3}")

    extracted_3 = extract_original_bits(
        embed_res_3, trace_res_3, nc_3, pixels_available_3, ref_key_3, orig_len_3
    )
    print(f"Hasil Ekstraksi ({len(extracted_3)} bit): ...")
    # print(f"Hasil Ekstraksi ({len(extracted_3)} bit): {extracted_3}")
    print(f"Verifikasi: {'Berhasil' if extracted_3 == secret_data_3 else 'Gagal'}")
    print("\n" + "="*40 + "\n")