import textwrap

# ==============================================================================
# --- BAGIAN 1: DEFINISI TABEL KONSTANTA STANDAR DES ---
# ==============================================================================
# Tabel-tabel ini tetap didefinisikan untuk keperluan perbandingan
# dan untuk permutasi yang tidak dibuat versi manualnya (misal: FP, P, PC2).

# Initial Permutation (IP) - Standar, 0-based index (Untuk Perbandingan)
IP_TABLE = [57, 49, 41, 33, 25, 17,  9,  1,
            59, 51, 43, 35, 27, 19, 11,  3,
            61, 53, 45, 37, 29, 21, 13,  5,
            63, 55, 47, 39, 31, 23, 15,  7,
            56, 48, 40, 32, 24, 16,  8,  0,
            58, 50, 42, 34, 26, 18, 10,  2,
            60, 52, 44, 36, 28, 20, 12,  4,
            62, 54, 46, 38, 30, 22, 14,  6]

# Final Permutation (FP = IP^-1) - Invers dari IP
FP_TABLE = [39,  7, 47, 15, 55, 23, 63, 31,
            38,  6, 46, 14, 54, 22, 62, 30,
            37,  5, 45, 13, 53, 21, 61, 29,
            36,  4, 44, 12, 52, 20, 60, 28,
            35,  3, 43, 11, 51, 19, 59, 27,
            34,  2, 42, 10, 50, 18, 58, 26,
            33,  1, 41,  9, 49, 17, 57, 25]

# Expansion Permutation (E) - Standar (Untuk Perbandingan)
E_TABLE = [31,  0,  1,  2,  3,  4,
           3,  4,  5,  6,  7,  8,
           7,  8,  9, 10, 11, 12,
           11, 12, 13, 14, 15, 16,
           15, 16, 17, 18, 19, 20,
           19, 20, 21, 22, 23, 24,
           23, 24, 25, 26, 27, 28,
           27, 28, 29, 30, 31,  0]

# Permutation Function (P) - Di dalam F-function
P_TABLE = [15,  6, 19, 20, 28, 11, 27, 16,
           0, 14, 22, 25,  4, 17, 30,  9,
           1,  7, 23, 13, 31, 26,  2,  8,
           18, 12, 29,  5, 21, 10,  3, 24]

# Permuted Choice 1 (PC-1) - Key Schedule (Untuk Perbandingan)
PC1_TABLE = [56, 48, 40, 32, 24, 16,  8,
             0, 57, 49, 41, 33, 25, 17,
             9,  1, 58, 50, 42, 34, 26,
             18, 10,  2, 59, 51, 43, 35,
             62, 54, 46, 38, 30, 22, 14,
             6, 61, 53, 45, 37, 29, 21,
             13,  5, 60, 52, 44, 36, 28,
             20, 12,  4, 27, 19, 11,  3]

# Permuted Choice 2 (PC-2) - Key Schedule
PC2_TABLE = [13, 16, 10, 23,  0,  4,
             2, 27, 14,  5, 20,  9,
             22, 18, 11,  3, 25,  7,
             15,  6, 26, 19, 12,  1,
             40, 51, 30, 36, 46, 54,
             29, 39, 50, 44, 32, 47,
             43, 48, 38, 55, 33, 52,
             45, 41, 49, 35, 28, 31]

# S-Boxes (S1 to S8)
S_BOX = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    # S2
    [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
     [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
     [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
     [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]],
    # S3
    [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
     [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
     [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
     [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]],
    # S4
    [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
     [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
     [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
     [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]],
    # S5
    [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]],
    # S6
    [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
     [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
     [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
     [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]],
    # S7
    [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
     [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
     [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
     [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]],
    # S8
    [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
     [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
     [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
     [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]]
]

# Jadwal Pergeseran Kiri untuk Key Schedule
SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


# ==============================================================================
# --- BAGIAN 2: FUNGSI HELPER DASAR ---
# ==============================================================================

def format_bits_as_matrix(bit_string, rows, cols):
    """
    Memformat string biner menjadi representasi matriks (string multi-baris).
    Menambahkan spasi antar kolom untuk kejelasan.
    """
    expected_len = rows * cols
    actual_len = len(bit_string)

    if actual_len != expected_len:
        # Jika panjang tidak sesuai, kembalikan pesan error atau string asli
        return f" [Error: Len={actual_len}, Expected={expected_len}] {bit_string} "

    matrix_lines = []
    for r in range(rows):
        start_idx = r * cols
        end_idx = start_idx + cols
        row_bits = bit_string[start_idx:end_idx]
        # Format baris dengan spasi antar bit
        formatted_row = " ".join(row_bits)
        # Tambahkan indentasi agar rapi saat dicetak di dalam ronde
        matrix_lines.append("      " + formatted_row)

    # Gabungkan semua baris matriks dengan newline
    return "\n".join(matrix_lines)


def bin_to_hex(bin_string):
    """Konversi string biner (64 bit) ke string heksadesimal (16 char)."""
    if len(bin_string) != 64:
        print(
            f"Warning: bin_to_hex menerima {len(bin_string)} bit, padding/truncating to 64 for hex.")
        # Atau raise ValueError("Input untuk bin_to_hex harus 64 bit")
    scale = 16  # Basis heksadesimal
    num_of_bits = len(bin_string)
    # Pastikan kelipatan 4
    if num_of_bits % 4 != 0:
        bin_string = '0' * (4 - num_of_bits % 4) + bin_string
        num_of_bits = len(bin_string)  # Update panjang setelah padding

    try:
        hex_val = hex(int(bin_string, 2))[2:].upper()
        # Pastikan panjang 16 karakter hex (untuk 64 bit input)
        return hex_val.zfill(num_of_bits // 4)
    except ValueError:
        return "Invalid Binary String"


def xor(bits1, bits2):
    """Melakukan operasi XOR bitwise antara dua string biner."""
    if len(bits1) != len(bits2):
        raise ValueError(
            f"Panjang bit XOR tidak sama: {len(bits1)} vs {len(bits2)}")
    # Cara lebih Pythonic menggunakan list comprehension dan join
    return "".join(str(int(b1) ^ int(b2)) for b1, b2 in zip(bits1, bits2))


def shift_left(bits, n):
    """Melakukan pergeseran kiri sirkular sebanyak n bit."""
    n = n % len(bits)  # Menghindari pergeseran lebih dari panjang bit
    return bits[n:] + bits[:n]


def permute(input_bits, table):
    """Melakukan permutasi bit berdasarkan tabel yang diberikan (Metode Standar)."""
    # Cara lebih Pythonic
    try:
        return "".join(input_bits[i] for i in table)
    except IndexError as e:
        # Menangkap error jika tabel meminta indeks di luar jangkauan input_bits
        max_index_req = max(table)
        raise IndexError(f"Tabel permutasi meminta indeks {max_index_req}, "
                         f"tetapi panjang input hanya {len(input_bits)}. Error: {e}")
    except TypeError as e:
        # Menangkap error jika input_bits bukan string atau table bukan iterable
        raise TypeError(f"Tipe input salah untuk permute. Error: {e}")


# ==============================================================================
# --- BAGIAN 3: FUNGSI PERMUTASI/EKSPANSI MANUAL BERDASARKAN LOGIKA POLA ---
# ==============================================================================

def initial_permutation_manual_correct(input_bin_64):
    """
    MANUAL IP: Melakukan Initial Permutation (IP) 64-bit berdasarkan
    logika pembacaan kolom matriks 8x8 (kolom [1,3,5,7,0,2,4,6] dibaca Btm-Up).
    """
    if len(input_bin_64) != 64:
        raise ValueError("IP Manual: Input harus 64 bit")
    if not all(c in '01' for c in input_bin_64):
        raise ValueError("IP Manual: Input harus biner")

    output_bits = [''] * 64
    output_idx = 0
    # Urutan kolom input yg dibaca
    column_read_order = [1, 3, 5, 7, 0, 2, 4, 6]

    for col_idx in column_read_order:
        for row_idx in range(7, -1, -1):  # Baca dari bawah ke atas
            input_index = row_idx * 8 + col_idx
            # Tidak perlu cek output_idx < 64 jika column_read_order dan range(7,-1,-1) benar
            output_bits[output_idx] = input_bin_64[input_index]
            output_idx += 1

    return "".join(output_bits)


def pc1_pattern_logic(key_bin_64):
    """
    MANUAL PC-1: Melakukan Permuted Choice 1 (PC-1) 64->56 bit berdasarkan
    pola kolom/baris (C0: pola kompleks; D0: Kolom 6,5,4 Btm-Up + Kolom 3[3..0]).
    """
    if len(key_bin_64) != 64:
        raise ValueError("PC-1 Manual: Input harus 64 bit")
    if not all(c in '01' for c in key_bin_64):
        raise ValueError("PC-1 Manual: Input harus biner")

    output_bits = []

    # --- Bagian 1: Menghasilkan C0 (Output bit 0-27) ---
    # Pola C0 kompleks, diimplementasikan sesuai urutan tabel PC1_TABLE standar
    # Col 0: baris 7->1 (7 bit), lalu baris 0 (1 bit)
    for row_idx in range(7, 0, -1):
        output_bits.append(key_bin_64[row_idx * 8 + 0])
    output_bits.append(key_bin_64[0 * 8 + 0])
    # Col 1: baris 7->2 (6 bit), lalu baris 1 (1 bit), lalu baris 0 (1 bit)
    for row_idx in range(7, 1, -1):
        output_bits.append(key_bin_64[row_idx * 8 + 1])
    output_bits.append(key_bin_64[1 * 8 + 1])
    output_bits.append(key_bin_64[0 * 8 + 1])
    # Col 2: baris 7->3 (5 bit), lalu baris 2, 1, 0 (3 bit)
    for row_idx in range(7, 2, -1):
        output_bits.append(key_bin_64[row_idx * 8 + 2])
    output_bits.append(key_bin_64[2 * 8 + 2])
    output_bits.append(key_bin_64[1 * 8 + 2])
    output_bits.append(key_bin_64[0 * 8 + 2])
    # Col 3: baris 7->4 (4 bit)
    for row_idx in range(7, 3, -1):
        output_bits.append(key_bin_64[row_idx * 8 + 3])
    if len(output_bits) != 28:
        raise ValueError(f"PC-1 Manual C0 error: {len(output_bits)} bits")

    # --- Bagian 2: Menghasilkan D0 (Output bit 28-55) ---
    # Bagian 2A: Bit 28-51 (24 bit pertama D0) - Kolom 6, 5, 4 Btm-Up
    d0_part_a_cols = [6, 5, 4]
    for col_idx in d0_part_a_cols:
        for row_idx in range(7, -1, -1):
            output_bits.append(key_bin_64[row_idx * 8 + col_idx])
    # Bagian 2B: Bit 52-55 (4 bit terakhir D0) - Kolom 3, baris 3->0
    d0_part_b_col = 3
    for row_idx in range(3, -1, -1):
        output_bits.append(key_bin_64[row_idx * 8 + d0_part_b_col])
    if len(output_bits) != 56:
        raise ValueError(f"PC-1 Manual total error: {len(output_bits)} bits")

    return "".join(output_bits)


def expansion_logic(right_32_bin):
    """
    MANUAL E: Melakukan Expansion Permutation (E) 32->48 bit berdasarkan pola:
    Untuk blok output ke-i: bit_akhir[i-1] + 4bit[i] + bit_awal[i+1] (wrap-around).
    """
    if len(right_32_bin) != 32:
        raise ValueError("Expansion Manual: Input harus 32 bit")
    if not all(c in '01' for c in right_32_bin):
        raise ValueError("Expansion Manual: Input harus biner")

    output_bits = []
    n_bits = 32

    for i in range(8):  # 8 blok output
        # Bit pertama: bit terakhir grup input sebelumnya
        prev_bit_index = (4 * i - 1 + n_bits) % n_bits
        output_bits.append(right_32_bin[prev_bit_index])
        # 4 bit tengah: 4 bit grup input saat ini
        for j in range(4):
            output_bits.append(right_32_bin[4 * i + j])
        # Bit terakhir: bit pertama grup input berikutnya
        next_bit_index = (4 * i + 4) % n_bits
        output_bits.append(right_32_bin[next_bit_index])

    if len(output_bits) != 48:
        raise ValueError(f"Expansion Manual error: {len(output_bits)} bits")
    return "".join(output_bits)


# ==============================================================================
# --- BAGIAN 4: FUNGSI INTI ALGORITMA DES ---
# ==============================================================================

def generate_keys(key_bin_64):
    """
    Key Schedule: Menghasilkan 16 kunci ronde 48-bit dari kunci 64-bit.
    Menggunakan PC-1 (bisa manual atau standar), pergeseran kiri, dan PC-2.
    """
    if len(key_bin_64) != 64:
        raise ValueError("Generate Keys: Input harus 64 bit")
    if not all(c in '01' for c in key_bin_64):
        raise ValueError("Generate Keys: Input harus biner")

    print("\n--- Generating Round Keys ---")
    print(f"Input Key 64-bit (bin): {textwrap.fill(key_bin_64, width=64)}")

    # --- Langkah 1: Permuted Choice 1 (PC-1) ---
    print("\n--- Permuted Choice 1 (PC-1) Comparison ---")
    # Hitung standar u/ perbandingan
    key_permuted_56_std = permute(key_bin_64, PC1_TABLE)
    key_permuted_56_pattern = pc1_pattern_logic(
        key_bin_64)  # Hitung pakai pola manual

    print(f" PC-1 Result (Standard - permute) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(key_permuted_56_std, width=56)}")
    print(format_bits_as_matrix(key_permuted_56_std, 8, 7))
    print(f" PC-1 Result (Manual Pattern Logic) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(key_permuted_56_pattern, width=56)}")

    if key_permuted_56_std == key_permuted_56_pattern:
        print("\n---> Hasil PC-1 dari Standard vs Pattern Logic SAMA (MATCH) <---")
        key_permuted_56 = key_permuted_56_pattern  # Lanjutkan dengan hasil pola
    else:
        print("\n---> !!! Hasil PC-1 BERBEDA (MISMATCH) !!! <---")
        key_permuted_56 = key_permuted_56_std  # Fallback ke standar jika pola salah
        print("     (Melanjutkan dengan hasil metode standard)")
    print("-" * 70)

    # --- Langkah 2: Split C0 dan D0 ---
    C = key_permuted_56[:28]
    D = key_permuted_56[28:]
    print(f" C0 (from selected PC-1): {C}")
    print(f" D0 (from selected PC-1): {D}")

    # --- Langkah 3 & 4: Generate 16 Round Keys ---
    round_keys = []
    for i in range(16):
        # Shift Left C dan D
        shifts = SHIFT_SCHEDULE[i]
        C = shift_left(C, shifts)
        D = shift_left(D, shifts)
        # Gabungkan dan lakukan Permuted Choice 2 (PC-2) - pakai tabel standar
        CD_combined = C + D
        round_key = permute(CD_combined, PC2_TABLE)
        round_keys.append(round_key)

    print("\n(16 Round keys generated successfully)")
    # print("\n--- Round Keys (K1-K16) ---") # Aktifkan jika ingin lihat kunci ronde
    # for i, k in enumerate(round_keys):
    #     print(f" K{i+1:<2} (bin): {textwrap.fill(k, width=48)}")
    return round_keys


def des_round_function(right_32_bin, round_key_48_bin):
    """
    F-Function: Menjalankan fungsi Feistel f(R, K) dalam satu ronde DES.
    Menggunakan Ekspansi (manual), XOR, S-Box, dan Permutasi P.
    """
    # 1. Expansion (E) 32->48 bit - Menggunakan logika manual
    expanded_r = expansion_logic(right_32_bin)

    # 2. Key Mixing (XOR)
    xor_result = xor(expanded_r, round_key_48_bin)

    # 3. Substitution (S-Boxes) 48->32 bit
    sbox_output = ""
    for i in range(8):  # Untuk setiap S-Box
        block_6bit = xor_result[i*6: (i+1)*6]
        # Bit 1 & 6 -> baris (0-3), Bit 2-5 -> kolom (0-15)
        row = int(block_6bit[0] + block_6bit[5], 2)
        col = int(block_6bit[1:5], 2)
        sbox_val = S_BOX[i][row][col]  # Ambil nilai desimal dari S-Box
        sbox_output += bin(sbox_val)[2:].zfill(4)  # Konversi ke 4 bit biner

    # 4. Permutation (P) 32->32 bit - Menggunakan tabel standar
    final_f_result = permute(sbox_output, P_TABLE)

    return final_f_result


def process_des(input_bin_64, round_keys, mode='encrypt'):
    """
    Proses Utama DES: Menjalankan enkripsi atau dekripsi 64-bit blok.
    Melibatkan IP (manual), 16 ronde Feistel, dan FP (standar).
    """
    if len(input_bin_64) != 64:
        raise ValueError("Proses DES: Input harus 64 bit")
    if not all(c in '01' for c in input_bin_64):
        raise ValueError("Proses DES: Input harus biner")
    if mode not in ['encrypt', 'decrypt']:
        raise ValueError("Mode harus 'encrypt' or 'decrypt'")

    op_mode = 'Encryption' if mode == 'encrypt' else 'Decryption'
    print(f"\n--- Starting DES {op_mode} ---")
    print(f"Input Block (bin): {textwrap.fill(input_bin_64, width=64)}")
    print(f"Input Block (hex): {bin_to_hex(input_bin_64)}")

    # --- Langkah 1: Initial Permutation (IP) ---
    # (Bagian perbandingan IP tetap sama, bisa dikomentari jika sudah yakin benar)
    print("\n--- Initial Permutation (IP) Comparison ---")
    permuted_input_std = permute(input_bin_64, IP_TABLE)
    permuted_input_manual = initial_permutation_manual_correct(input_bin_64)
    print(f" IP Result (Standard - permute) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(permuted_input_std, width=64)}")
    # print(f"  Hex: {bin_to_hex(permuted_input_std)}") # Komen hex IP jika terlalu ramai
    print(f" IP Result (Manual Logic) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(permuted_input_manual, width=64)}")
    # print(f"  Hex: {bin_to_hex(permuted_input_manual)}") # Komen hex IP jika terlalu ramai

    if permuted_input_std == permuted_input_manual:
        print("\n---> Hasil IP dari kedua metode SAMA (MATCH) <---")
        permuted_input = permuted_input_manual
    else:
        print("\n---> !!! Hasil IP BERBEDA (MISMATCH) !!! <---")
        permuted_input = permuted_input_std
        print("     (Melanjutkan dengan hasil metode standard)")
    print("-" * 70)

    # --- Langkah 2: Split L0 dan R0 ---
    L = permuted_input[:32]
    R = permuted_input[32:]
    print(f"\nAfter IP (using chosen method):")
    print(f" L0:")
    print(format_bits_as_matrix(L, 4, 8))  # Tampilkan L0 sebagai matrix
    print(f" R0:")
    print(format_bits_as_matrix(R, 4, 8))  # Tampilkan R0 sebagai matrix

    # Tentukan urutan kunci ronde (dibalik untuk dekripsi)
    keys_to_use = round_keys if mode == 'encrypt' else round_keys[::-1]

    # --- Langkah 3: 16 Ronde Feistel ---
    print("\n--- Running 16 Rounds ---")
    print("-" * 70)
    for i in range(16):
        L_prev = L
        R_prev = R
        round_num = i + 1
        key_num_display = round_num if mode == 'encrypt' else 16 - i

        # Panggil F-function (yang sudah pakai expansion_logic manual)
        f_result = des_round_function(R_prev, keys_to_use[i])

        # Hitung L baru = R lama
        L = R_prev
        # Hitung R baru = L lama XOR F(R lama, K ronde)
        R = xor(L_prev, f_result)

        # --- Tampilkan Hasil Ronde ke-i ---
        print(f"Round {round_num:>2}:")
        print(f"  K[{key_num_display:<2}] applied to R{i:<2} = {R_prev}")
        print(f"  f(R{i:<2}, K{key_num_display:<2})           = {f_result}")
        print(f"  L{round_num:<2} = R{i:<2}                = {L}")
        print(f"  R{round_num:<2} = L{i:<2} XOR f(...)      = {R}")
        print("-" * 70)
        # ---------------------------------

    print("(16 rounds completed)")

    # --- Langkah 4: Swap Final & Final Permutation (FP) ---
    # Gabungkan R16 dan L16 (swap terakhir)
    final_block_before_fp = R + L
    print(
        f"\nBlock after 16 rounds (R16L16): {textwrap.fill(final_block_before_fp, width=64)}")

    # Lakukan Final Permutation (FP) - Menggunakan tabel standar
    output_bin_64 = permute(final_block_before_fp, FP_TABLE)
    print(
        f"After Final Permutation (FP): {textwrap.fill(output_bin_64, width=64)}")
    # print(f"DEBUG: Panjang output_bin_64 sebelum bin_to_hex: {len(output_bin_64)}") # Boleh dihapus jika sdh OK

    # Konversi ke Hex
    output_hex = bin_to_hex(output_bin_64)
    print(
        f"\nFinal {'Ciphertext' if mode == 'encrypt' else 'Plaintext'} (hex): {output_hex}")

    return output_bin_64, output_hex


# ==============================================================================
# --- BAGIAN 5: EKSEKUSI CONTOH ---
# ==============================================================================
if __name__ == "__main__":
    # Contoh Plaintext dan Key (sama seperti sebelumnya)
    # Hex: 0123456789ABCDEF
    plaintext_bin = "0000000100100011010001010110011110001001101010111100110111101111"
    # Hex: 133457799BBCDFF1
    key_bin = "0001001100110100010101110111100110011011101111001101111111110001"
    expected_ciphertext_hex = "85E813540F0AB405"  # Hasil standar yg diharapkan

    print("="*70)
    print(" DES Implementation with Manual Logic Components ".center(70))
    print("="*70)
    print(f"Plaintext (bin): {textwrap.fill(plaintext_bin, width=64)}")
    print(f"Key       (bin): {textwrap.fill(key_bin, width=64)}")
    print(f"Plaintext (hex): {bin_to_hex(plaintext_bin)}")
    print(f"Key       (hex): {bin_to_hex(key_bin)}")
    print(f"Expected Ciphertext (hex): {expected_ciphertext_hex}")
    print("-"*70)

    # Validasi input dasar
    try:
        if len(plaintext_bin) != 64:
            raise ValueError("Plaintext harus 64 bit")
        if len(key_bin) != 64:
            raise ValueError("Key harus 64 bit")
        if not all(c in '01' for c in plaintext_bin):
            raise ValueError("Plaintext harus biner")
        if not all(c in '01' for c in key_bin):
            raise ValueError("Key harus biner")

        # 1. Generate Kunci Ronde
        round_keys_list = generate_keys(key_bin)

        # 2. Enkripsi
        ciphertext_bin, ciphertext_hex = process_des(
            plaintext_bin, round_keys_list, mode='encrypt')

        # Verifikasi Enkripsi
        print("\n--- Verification ---")
        print(f"Expected Ciphertext : {expected_ciphertext_hex}")
        print(f"Actual Ciphertext   : {ciphertext_hex}")
        if ciphertext_hex == expected_ciphertext_hex:
            print(">>> Encryption Result: MATCH <<<")
        else:
            print(">>> Encryption Result: MISMATCH <<<")
        print("-"*70)

        # 3. Dekripsi
        decrypted_bin, decrypted_hex = process_des(
            ciphertext_bin, round_keys_list, mode='decrypt')

        # Verifikasi Dekripsi
        original_plaintext_hex = bin_to_hex(plaintext_bin)
        print("\n--- Verification ---")
        print(f"Original Plaintext : {original_plaintext_hex}")
        print(f"Decrypted Result   : {decrypted_hex}")
        if decrypted_hex == original_plaintext_hex:
            print(">>> Decryption Result: MATCH <<<")
        else:
            print(">>> Decryption Result: MISMATCH <<<")
        print("="*70)

    except Exception as e:
        print(f"\n!!! An error occurred during execution: {e} !!!")
        import traceback
        traceback.print_exc()
