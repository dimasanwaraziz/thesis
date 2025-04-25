import textwrap

# --- Definisi Tabel Konstanta DES ---

# Initial Permutation (IP) - Standar, 0-based index (Untuk Perbandingan)
IP_TABLE = [57, 49, 41, 33, 25, 17,  9,  1,
            59, 51, 43, 35, 27, 19, 11,  3,
            61, 53, 45, 37, 29, 21, 13,  5,
            63, 55, 47, 39, 31, 23, 15,  7,
            56, 48, 40, 32, 24, 16,  8,  0,
            58, 50, 42, 34, 26, 18, 10,  2,
            60, 52, 44, 36, 28, 20, 12,  4,
            62, 54, 46, 38, 30, 22, 14,  6]

# Final Permutation (FP = IP^-1) - Masih dibutuhkan karena invers IP
FP_TABLE = [39,  7, 47, 15, 55, 23, 63, 31,
            38,  6, 46, 14, 54, 22, 62, 30,
            37,  5, 45, 13, 53, 21, 61, 29,
            36,  4, 44, 12, 52, 20, 60, 28,
            35,  3, 43, 11, 51, 19, 59, 27,
            34,  2, 42, 10, 50, 18, 58, 26,
            33,  1, 41,  9, 49, 17, 57, 25]

# Expansion Permutation (E)
E_TABLE = [31,  0,  1,  2,  3,  4,
           3,  4,  5,  6,  7,  8,
           7,  8,  9, 10, 11, 12,
           11, 12, 13, 14, 15, 16,
           15, 16, 17, 18, 19, 20,
           19, 20, 21, 22, 23, 24,
           23, 24, 25, 26, 27, 28,
           27, 28, 29, 30, 31,  0]

# Permutation Function (P)
P_TABLE = [15,  6, 19, 20, 28, 11, 27, 16,
           0, 14, 22, 25,  4, 17, 30,  9,
           1,  7, 23, 13, 31, 26,  2,  8,
           18, 12, 29,  5, 21, 10,  3, 24]

# Permuted Choice 1 (PC-1) - 56 bit output
PC1_TABLE = [56, 48, 40, 32, 24, 16,  8,
             0, 57, 49, 41, 33, 25, 17,
             9,  1, 58, 50, 42, 34, 26,
             18, 10,  2, 59, 51, 43, 35,
             62, 54, 46, 38, 30, 22, 14,
             6, 61, 53, 45, 37, 29, 21,
             13,  5, 60, 52, 44, 36, 28,
             20, 12,  4, 27, 19, 11,  3]

# Permuted Choice 2 (PC-2) - 48 bit output
PC2_TABLE = [13, 16, 10, 23,  0,  4,
             2, 27, 14,  5, 20,  9,
             22, 18, 11,  3, 25,  7,
             15,  6, 26, 19, 12,  1,
             40, 51, 30, 36, 46, 54,
             29, 39, 50, 44, 32, 47,
             43, 48, 38, 55, 33, 52,
             45, 41, 49, 35, 28, 31]

# S-Boxes (S1 to S8) - Sama seperti sebelumnya
S_BOX = [
    # S1
    [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
     [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
     [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
     [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]],
    # S2 - S8 sama ... (dihapus untuk keringkasan, tapi harus ada di kode asli)
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

# --- Fungsi Helper ---


def bin_to_hex(bin_string):
    """Konversi string biner ke string heksadesimal."""
    scale = 16  # equals to hexadecimal
    num_of_bits = len(bin_string)
    if num_of_bits % 4 != 0:
        bin_string = '0' * (4 - num_of_bits % 4) + bin_string
    try:
        return hex(int(bin_string, 2))[2:].upper().zfill(len(bin_string)//4)
    except ValueError:
        return "Invalid Binary String"  # Handle jika input bukan biner murni


def permute(input_bits, table):
    """Melakukan permutasi bit berdasarkan tabel yang diberikan (Metode Standar)."""
    output_bits = ""
    for i in table:
        if i < len(input_bits):
            output_bits += input_bits[i]
        else:
            raise IndexError(
                f"Indeks permutasi {i} di luar jangkauan untuk input panjang {len(input_bits)}")
    return output_bits


def xor(bits1, bits2):
    """Melakukan operasi XOR bitwise antara dua string biner."""
    if len(bits1) != len(bits2):
        raise ValueError(
            f"Panjang bit untuk XOR tidak sama: {len(bits1)} vs {len(bits2)}")
    result = ""
    for i in range(len(bits1)):
        result += str(int(bits1[i]) ^ int(bits2[i]))
    return result


def shift_left(bits, n):
    """Melakukan pergeseran kiri sirkular sebanyak n bit."""
    n = n % len(bits)
    return bits[n:] + bits[:n]


# --- Fungsi Initial Permutation Menggunakan Logika Matriks (Manual) ---
def initial_permutation_manual_correct(input_bin_64):
    """
    Melakukan Initial Permutation (IP) pada input 64-bit
    berdasarkan logika pembacaan kolom matriks 8x8 (bottom-to-top),
    tanpa menggunakan IP_TABLE secara eksplisit (Metode Manual).
    """
    if len(input_bin_64) != 64:
        raise ValueError("Input untuk Initial Permutation harus 64 bit")
    if not all(c in '01' for c in input_bin_64):
        raise ValueError("Input harus berupa string biner ('0' atau '1')")

    output_bits = [''] * 64
    output_idx = 0
    column_read_order = [1, 3, 5, 7, 0, 2, 4, 6]

    for col_idx in column_read_order:
        for row_idx in range(7, -1, -1):
            input_index = row_idx * 8 + col_idx
            if output_idx < 64:
                output_bits[output_idx] = input_bin_64[input_index]
                output_idx += 1
            else:
                raise IndexError("Indeks output melebihi 63")

    return "".join(output_bits)


# --- Fungsi Inti DES ---

def generate_keys(key_bin_64):
    """Menghasilkan 16 kunci ronde 48-bit dari kunci 64-bit."""
    if len(key_bin_64) != 64:
        raise ValueError("Kunci awal harus 64 bit")
    if not all(c in '01' for c in key_bin_64):
        raise ValueError("Kunci awal harus berupa string biner ('0' atau '1')")

    key_permuted_56 = permute(key_bin_64, PC1_TABLE)
    C = key_permuted_56[:28]
    D = key_permuted_56[28:]

    round_keys = []
    print("\n--- Generating Round Keys ---")
    for i in range(16):
        shifts = SHIFT_SCHEDULE[i]
        C = shift_left(C, shifts)
        D = shift_left(D, shifts)
        CD_combined = C + D
        round_key = permute(CD_combined, PC2_TABLE)
        round_keys.append(round_key)
        # print(f" K{i+1:<2} (bin): {textwrap.fill(round_key, width=48)}") # Komentari agar output tidak terlalu panjang
    print(" (Round keys generated)")
    return round_keys


def des_round_function(right_32_bin, round_key_48_bin):
    """Menjalankan fungsi Feistel f(R, K)."""
    expanded_r = permute(right_32_bin, E_TABLE)
    xor_result = xor(expanded_r, round_key_48_bin)
    sbox_output = ""
    for i in range(8):
        block_6bit = xor_result[i*6: (i+1)*6]
        row = int(block_6bit[0] + block_6bit[5], 2)
        col = int(block_6bit[1:5], 2)
        sbox_val = S_BOX[i][row][col]
        sbox_output += bin(sbox_val)[2:].zfill(4)
    final_f_result = permute(sbox_output, P_TABLE)
    return final_f_result


def process_des(input_bin_64, round_keys, mode='encrypt'):
    """Menjalankan proses enkripsi atau dekripsi DES."""
    if len(input_bin_64) != 64:
        raise ValueError("Input data harus 64 bit")
    if not all(c in '01' for c in input_bin_64):
        raise ValueError("Input data harus berupa string biner ('0' atau '1')")

    print(
        f"\n--- Starting DES {'Encryption' if mode == 'encrypt' else 'Decryption'} ---")
    print(f"Input Block (bin): {textwrap.fill(input_bin_64, width=64)}")
    print(f"Input Block (hex): {bin_to_hex(input_bin_64)}")

    # --- LANGKAH 1: Initial Permutation (IP) ---
    print("\n--- Initial Permutation Comparison ---")

    # Metode 1: Menggunakan tabel IP_TABLE standar dan fungsi permute
    permuted_input_std = permute(input_bin_64, IP_TABLE)
    print(f" IP Result (Standard - permute) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(permuted_input_std, width=64)}")
    print(f"  Hex: {bin_to_hex(permuted_input_std)}")

    # Metode 2: Menggunakan logika manual (pembacaan kolom bottom-to-top)
    permuted_input_manual = initial_permutation_manual_correct(input_bin_64)
    print(f" IP Result (Manual Logic) ".center(70, "-"))
    print(f"  Bin: {textwrap.fill(permuted_input_manual, width=64)}")
    print(f"  Hex: {bin_to_hex(permuted_input_manual)}")

    # Bandingkan hasil kedua metode
    if permuted_input_std == permuted_input_manual:
        print("\n---> Hasil IP dari kedua metode SAMA (MATCH) <---")
        # Pilih salah satu hasil untuk melanjutkan proses DES
        permuted_input = permuted_input_manual  # atau permuted_input_std
    else:
        print("\n---> !!! Hasil IP dari kedua metode BERBEDA (MISMATCH) !!! <---")
        # Hentikan atau lanjutkan dengan salah satu (misal: manual) untuk debug
        permuted_input = permuted_input_manual
        print("     (Melanjutkan proses DES dengan hasil metode manual)")

    print("-" * 70)  # Penutup bagian perbandingan

    # --- Lanjutan Proses DES ---
    # Bagi jadi L0 dan R0
    L = permuted_input[:32]
    R = permuted_input[32:]
    print(f" L0: {L}")
    print(f" R0: {R}")

    # Tentukan urutan kunci ronde
    keys_to_use = round_keys
    if mode == 'decrypt':
        keys_to_use = round_keys[::-1]

    # 2. 16 Rounds
    for i in range(16):
        # print(f"\n--- Round {i+1} ---") # Komentari agar output tidak terlalu panjang
        L_prev = L
        R_prev = R
        key_index = i
        f_result = des_round_function(R_prev, keys_to_use[key_index])
        R = xor(L_prev, f_result)
        L = R_prev
        # print(f" f(R{i}, K{i+1 if mode == 'encrypt' else 16-i}) = {f_result}") # Komentari
        # print(f" L{i+1}: {L}") # Komentari
        # print(f" R{i+1}: {R}") # Komentari

    # 3. Gabungkan R16 dan L16 (Urutan dibalik sebelum FP)
    final_block_before_fp = R + L
    print(
        f"\nBlock after 16 rounds (R16L16): {textwrap.fill(final_block_before_fp, width=64)}")

    # 4. Final Permutation (FP = IP^-1) - Pakai permute dengan FP_TABLE
    output_bin_64 = permute(final_block_before_fp, FP_TABLE)
    print(
        f"After Final Permutation (FP): {textwrap.fill(output_bin_64, width=64)}")

    output_hex = bin_to_hex(output_bin_64)
    print(
        f"\nFinal {'Ciphertext' if mode == 'encrypt' else 'Plaintext'} (hex): {output_hex}")
    # print(f"Final {'Ciphertext' if mode == 'encrypt' else 'Plaintext'} (bin): {textwrap.fill(output_bin_64, width=64)}") # Komentari
    return output_bin_64, output_hex


# --- Contoh Penggunaan ---
if __name__ == "__main__":
    # Hex: 0123456789ABCDEF
    plaintext_bin = "0000000100100011010001010110011110001001101010111100110111101111"
    # Hex: 133457799BBCDFF1
    key_bin = "0001001100110100010101110111100110011011101111001101111111110001"

    print(f"Plaintext (bin): {textwrap.fill(plaintext_bin, width=64)}")
    print(f"Key       (bin): {textwrap.fill(key_bin, width=64)}")
    print(f"Plaintext (hex): {bin_to_hex(plaintext_bin)}")
    print(f"Key       (hex): {bin_to_hex(key_bin)}")

    # Validasi input dasar
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

    # Verifikasi Ciphertext
    expected_ciphertext_hex = "85E813540F0AB405"
    print(f"\nExpected Ciphertext (hex): {expected_ciphertext_hex}")
    if ciphertext_hex == expected_ciphertext_hex:
        print("Encryption Result: MATCH")
    else:
        print("Encryption Result: MISMATCH")

    # 3. Dekripsi
    decrypted_bin, decrypted_hex = process_des(
        ciphertext_bin, round_keys_list, mode='decrypt')

    # Verifikasi Dekripsi
    original_plaintext_hex = bin_to_hex(plaintext_bin)
    print(f"\nOriginal Plaintext (hex): {original_plaintext_hex}")
    print(f"Decrypted Result   (hex): {decrypted_hex}")
    if decrypted_hex == original_plaintext_hex:
        print("Decryption Result: MATCH")
    else:
        print("Decryption Result: MISMATCH")
