#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulasi Enkripsi dan Dekripsi DES (Data Encryption Standard)
Implementasi ini dibuat tanpa library kriptografi eksternal untuk tujuan edukasi.
Menampilkan output detail setiap tahapan, termasuk format matriks untuk data biner.
PERINGATAN: DES tidak aman untuk penggunaan modern. Gunakan AES.
"""

# ==============================================================================
# Konstanta Standar DES
# ==============================================================================

# Initial Permutation (IP)
IP_TABLE = [
    58,
    50,
    42,
    34,
    26,
    18,
    10,
    2,
    60,
    52,
    44,
    36,
    28,
    20,
    12,
    4,
    62,
    54,
    46,
    38,
    30,
    22,
    14,
    6,
    64,
    56,
    48,
    40,
    32,
    24,
    16,
    8,
    57,
    49,
    41,
    33,
    25,
    17,
    9,
    1,
    59,
    51,
    43,
    35,
    27,
    19,
    11,
    3,
    61,
    53,
    45,
    37,
    29,
    21,
    13,
    5,
    63,
    55,
    47,
    39,
    31,
    23,
    15,
    7,
]

# Final Permutation (FP or IP^-1)
FP_TABLE = [
    40,
    8,
    48,
    16,
    56,
    24,
    64,
    32,
    39,
    7,
    47,
    15,
    55,
    23,
    63,
    31,
    38,
    6,
    46,
    14,
    54,
    22,
    62,
    30,
    37,
    5,
    45,
    13,
    53,
    21,
    61,
    29,
    36,
    4,
    44,
    12,
    52,
    20,
    60,
    28,
    35,
    3,
    43,
    11,
    51,
    19,
    59,
    27,
    34,
    2,
    42,
    10,
    50,
    18,
    58,
    26,
    33,
    1,
    41,
    9,
    49,
    17,
    57,
    25,
]

# Expansion (E) Table
E_TABLE = [
    32,
    1,
    2,
    3,
    4,
    5,
    4,
    5,
    6,
    7,
    8,
    9,
    8,
    9,
    10,
    11,
    12,
    13,
    12,
    13,
    14,
    15,
    16,
    17,
    16,
    17,
    18,
    19,
    20,
    21,
    20,
    21,
    22,
    23,
    24,
    25,
    24,
    25,
    26,
    27,
    28,
    29,
    28,
    29,
    30,
    31,
    32,
    1,
]

# Permutation (P) Table
P_TABLE = [
    16,
    7,
    20,
    21,
    29,
    12,
    28,
    17,
    1,
    15,
    23,
    26,
    5,
    18,
    31,
    10,
    2,
    8,
    24,
    14,
    32,
    27,
    3,
    9,
    19,
    13,
    30,
    6,
    22,
    11,
    4,
    25,
]

# S-Boxes (Substitution Boxes)
S_BOX = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]

# Permuted Choice 1 (PC-1) - Untuk Key Schedule
PC1_TABLE = [
    57,
    49,
    41,
    33,
    25,
    17,
    9,
    1,
    58,
    50,
    42,
    34,
    26,
    18,
    10,
    2,
    59,
    51,
    43,
    35,
    27,
    19,
    11,
    3,
    60,
    52,
    44,
    36,
    63,
    55,
    47,
    39,
    31,
    23,
    15,
    7,
    62,
    54,
    46,
    38,
    30,
    22,
    14,
    6,
    61,
    53,
    45,
    37,
    29,
    21,
    13,
    5,
    28,
    20,
    12,
    4,
]

# Permuted Choice 2 (PC-2) - Untuk Key Schedule
PC2_TABLE = [
    14,
    17,
    11,
    24,
    1,
    5,
    3,
    28,
    15,
    6,
    21,
    10,
    23,
    19,
    12,
    4,
    26,
    8,
    16,
    7,
    27,
    20,
    13,
    2,
    41,
    52,
    31,
    37,
    47,
    55,
    30,
    40,
    51,
    45,
    33,
    48,
    44,
    49,
    39,
    56,
    34,
    53,
    46,
    42,
    50,
    36,
    29,
    32,
]

# Jumlah pergeseran kiri (left shift) untuk setiap putaran dalam Key Schedule
SHIFT_TABLE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]


# ==============================================================================
# Fungsi Bantuan
# ==============================================================================


def string_to_bits(text):
    """Konversi string ASCII ke string biner."""
    bits = ""
    for char in text:
        binary = bin(ord(char))[2:].zfill(8)
        bits += binary
    return bits


def bits_to_string(bits):
    """Konversi string biner ke string ASCII, tangani potensi error."""
    chars = []
    # Pastikan panjang bit adalah kelipatan 8
    padded_len = (len(bits) + 7) // 8 * 8
    bits = bits.ljust(padded_len, "0")
    for i in range(0, len(bits), 8):
        byte = bits[i : i + 8]
        try:
            # Coba konversi ke integer lalu ke karakter
            value = int(byte, 2)
            # Hanya konversi jika dalam rentang ASCII yang bisa dicetak atau karakter umum
            # (Anda mungkin ingin menyesuaikan ini)
            if 32 <= value <= 126 or value in [
                0,
                9,
                10,
                13,
            ]:  # Printable ASCII + NULL, TAB, LF, CR
                chars.append(chr(value))
            else:
                chars.append("?")  # Ganti byte non-printable/non-ASCII dengan '?'
        except ValueError:
            # Jika int(byte, 2) gagal (seharusnya tidak terjadi jika input adalah '0'/'1')
            chars.append("?")
    return "".join(chars)


def bits_to_hex(bits):
    """Konversi string biner ke string heksadesimal."""
    hex_string = ""
    for i in range(0, len(bits), 4):
        nibble = bits[i : i + 4]
        hex_char = hex(int(nibble, 2))[2:]
        hex_string += hex_char
    return hex_string.upper()


def hex_to_bits(hex_string):
    """Konversi string heksadesimal ke string biner."""
    bits = ""
    for hex_char in hex_string.lower():  # Konversi ke lowercase untuk konsistensi
        binary = bin(int(hex_char, 16))[2:].zfill(4)
        bits += binary
    return bits


def permute(k, table):
    """Melakukan permutasi pada blok bit 'k' berdasarkan 'table'."""
    return "".join([k[bit_pos - 1] for bit_pos in table])


def xor(bits1, bits2):
    """Melakukan operasi XOR pada dua string biner."""
    return "".join(["1" if b1 != b2 else "0" for b1, b2 in zip(bits1, bits2)])


def left_circular_shift(bits, n):
    """Melakukan pergeseran sirkular ke kiri sebanyak 'n' bit."""
    return bits[n:] + bits[:n]


def split_bits(bits, n):
    """Membagi string biner menjadi potongan-potongan berukuran 'n'."""
    return [bits[i : i + n] for i in range(0, len(bits), n)]


# Versi Baru (Spasi antar setiap bit)
def print_bits_as_matrix(label, bits, row_len=8, indent="  "):
    """
    Mencetak string biner dalam format matriks dengan indentasi konsisten
    dan spasi antar SETIAP bit (kolom).
    """
    print(f"{indent}{label}:")  # Cetak label
    if not bits:
        print(f"{indent}  (empty)")
        return

    matrix_line_indent = indent + "  "  # Indentasi untuk baris data

    for i in range(0, len(bits), row_len):
        row_bits = bits[i : i + row_len]  # Ambil bit untuk satu baris

        # Gunakan ' '.join() untuk menyisipkan spasi antar setiap karakter
        formatted_row = " ".join(row_bits)

        # Cetak baris yang sudah diformat dengan spasi
        print(f"{matrix_line_indent}{formatted_row}")


# ==============================================================================
# Fungsi Inti DES (dengan Output Detail dan Format Matriks)
# ==============================================================================


def generate_round_keys(key_bits):
    """Menghasilkan 16 kunci putaran dari kunci 64-bit dengan output matriks."""
    print("\n--- Key Schedule Generation ---")
    if len(key_bits) != 64:
        raise ValueError("Kunci harus 64 bit")
    print_bits_as_matrix("Initial Key (64 bits)", key_bits, 8, indent="")

    key_permuted = permute(key_bits, PC1_TABLE)
    # 56 bits -> 8x7
    print_bits_as_matrix(
        "Key after PC-1 (56 bits)", key_permuted, 8, indent=""
    )  # Baris terakhir 7 bit

    C = key_permuted[:28]
    D = key_permuted[28:]
    # 28 bits -> 4x7
    print_bits_as_matrix("C0 (28 bits)", C, 7, indent="")
    print_bits_as_matrix("D0 (28 bits)", D, 7, indent="")

    round_keys = []
    for i in range(16):
        print(f"\n  --- Key Generation Round {i+1} ---")
        shift_amount = SHIFT_TABLE[i]
        print(f"  Shift amount: {shift_amount}")
        print_bits_as_matrix(f"C{i}", C, 7, indent="  ")
        print_bits_as_matrix(f"D{i}", D, 7, indent="  ")
        C = left_circular_shift(C, shift_amount)
        D = left_circular_shift(D, shift_amount)
        print_bits_as_matrix(f"C{i+1} (after shift)", C, 7, indent="  ")
        print_bits_as_matrix(f"D{i+1} (after shift)", D, 7, indent="  ")

        CD = C + D
        print_bits_as_matrix(
            f"C{i+1}D{i+1} (56 bits)", CD, 8, indent="  "
        )  # Baris terakhir 7 bit

        round_key = permute(CD, PC2_TABLE)
        # 48 bits -> 8x6
        print_bits_as_matrix(
            f"Round Key K{i+1} (48 bits)", round_key, 8, indent="  "
        )  # Baris terakhir 6 bit
        round_keys.append(round_key)

    print("--- End Key Schedule Generation ---")
    return round_keys


def function_F(right_half_32bits, round_key_48bits):
    """Fungsi F dalam putaran Feistel DES dengan output detail."""
    print(f"    -- Function F Start --")
    # Input R (32 bit -> 8x4)
    print_bits_as_matrix("Input R (32 bits)", right_half_32bits, 8, indent="    ")
    # Input K (48 bit -> 8x6)
    print_bits_as_matrix("Input K (48 bits)", round_key_48bits, 8, indent="    ")

    expanded_bits = permute(right_half_32bits, E_TABLE)
    # E(R) (48 bit -> 8x6)
    print_bits_as_matrix("E(R) (48 bits)", expanded_bits, 8, indent="    ")

    xored_bits = xor(expanded_bits, round_key_48bits)
    # E(R) XOR K (48 bit -> 8x6)
    print_bits_as_matrix("E(R) XOR K (48 bits)", xored_bits, 8, indent="    ")

    sbox_output = ""
    blocks_6bit = split_bits(xored_bits, 6)
    print(f"    Input to S-Boxes (8 blocks of 6 bits):")
    print(f"      {blocks_6bit}")
    for i in range(8):
        block = blocks_6bit[i]
        row = int(block[0] + block[5], 2)
        col = int(block[1:5], 2)
        sbox_val = S_BOX[i][row][col]
        sbox_out_bits = bin(sbox_val)[2:].zfill(4)
        print(
            f"      S-Box {i+1}: Input={block} -> Row={row}, Col={col} -> Val={sbox_val} -> Output={sbox_out_bits}"
        )
        sbox_output += sbox_out_bits
    # S-Box Output (32 bit -> 8x4)
    print_bits_as_matrix("S-Box Output (32 bits)", sbox_output, 8, indent="    ")

    final_output_32bits = permute(sbox_output, P_TABLE)
    # P(S-Box Output) (32 bit -> 8x4)
    print_bits_as_matrix(
        "P(S-Box Output) (32 bits)", final_output_32bits, 8, indent="    "
    )
    print(f"    -- Function F End --")
    return final_output_32bits


def des_encrypt_block(plaintext_bits, key_bits):
    """Mengenkripsi satu blok 64-bit dengan output detail dan format matriks."""
    print("\n\n========== DES ENCRYPTION START ==========")
    if len(plaintext_bits) != 64:
        raise ValueError("Plaintext harus 64 bit")
    print_bits_as_matrix("Plaintext (64 bits)", plaintext_bits, 8, indent="")

    round_keys = generate_round_keys(key_bits)

    permuted_block = permute(plaintext_bits, IP_TABLE)
    print("\nAfter Initial Permutation (IP):")
    print_bits_as_matrix("IP Result", permuted_block, 8, indent="")

    L = permuted_block[:32]
    R = permuted_block[32:]
    print_bits_as_matrix("L0", L, 8, indent="")
    print_bits_as_matrix("R0", R, 8, indent="")

    for i in range(16):
        print(f"\n--- Encryption Round {i+1} ---")
        L_prev = L
        R_prev = R
        print_bits_as_matrix(f"L{i}", L_prev, 8, indent="  ")
        print_bits_as_matrix(f"R{i}", R_prev, 8, indent="  ")

        f_result = function_F(R_prev, round_keys[i])
        print(f"  Result of F(R{i}, K{i+1}):")
        print_bits_as_matrix("F Output", f_result, 8, indent="  ")

        L = R_prev
        R = xor(L_prev, f_result)
        print(f"  New L{i+1} = R{i}:")
        print_bits_as_matrix(f"L{i+1}", L, 8, indent="  ")
        print(f"  New R{i+1} = L{i} XOR F:")
        print_bits_as_matrix(f"R{i+1}", R, 8, indent="  ")

    print("\n--- After 16 Rounds ---")
    print_bits_as_matrix("L16", L, 8, indent="")
    print_bits_as_matrix("R16", R, 8, indent="")
    final_LR = R + L  # Swap
    print("Before Final Permutation (R16L16):")
    print_bits_as_matrix("R16L16", final_LR, 8, indent="")

    ciphertext_bits = permute(final_LR, FP_TABLE)
    print("\nAfter Final Permutation (FP):")
    print_bits_as_matrix("Ciphertext", ciphertext_bits, 8, indent="")
    print("========== DES ENCRYPTION END ==========")
    return ciphertext_bits


def des_decrypt_block(ciphertext_bits, key_bits):
    """Mendekripsi satu blok 64-bit dengan output detail dan format matriks."""
    print("\n\n========== DES DECRYPTION START ==========")
    if len(ciphertext_bits) != 64:
        raise ValueError("Ciphertext harus 64 bit")
    print_bits_as_matrix("Ciphertext (64 bits)", ciphertext_bits, 8, indent="")

    # Generate keys again, but we won't print the schedule this time
    # Assuming it was printed during encryption for comparison
    round_keys = generate_round_keys(key_bits)
    print("\n(Key schedule generation skipped in decryption output for brevity)")

    permuted_block = permute(ciphertext_bits, IP_TABLE)
    print("\nAfter Initial Permutation (IP):")
    print_bits_as_matrix("IP Result", permuted_block, 8, indent="")

    L = permuted_block[:32]  # Ini R16 enkripsi
    R = permuted_block[32:]  # Ini L16 enkripsi
    print_bits_as_matrix("L_initial (R16 from enc)", L, 8, indent="")
    print_bits_as_matrix("R_initial (L16 from enc)", R, 8, indent="")

    # Putaran dengan kunci terbalik (K16, K15, ..., K1)
    for i in range(15, -1, -1):
        round_num_dec = 16 - i
        print(f"\n--- Decryption Round {round_num_dec} (Using K{i+1}) ---")
        L_prev = L
        R_prev = R
        print_bits_as_matrix(f"L_in (R{i+1} from enc)", L_prev, 8, indent="  ")
        print_bits_as_matrix(f"R_in (L{i+1} from enc)", R_prev, 8, indent="  ")

        # Panggil function_F (akan print detailnya sendiri)
        f_result = function_F(R_prev, round_keys[i])
        print(f"  Result of F(R_in, K{i+1}):")
        print_bits_as_matrix("F Output", f_result, 8, indent="  ")

        L = R_prev  # L baru adalah R sebelumnya
        R = xor(L_prev, f_result)  # R baru adalah L sebelumnya XOR F
        print(f"  New L_out (R{i} from enc) = R_in:")
        print_bits_as_matrix(f"L_out", L, 8, indent="  ")
        print(f"  New R_out (L{i} from enc) = L_in XOR F:")
        print_bits_as_matrix(f"R_out", R, 8, indent="  ")

    print("\n--- After 16 Rounds of Decryption ---")
    print_bits_as_matrix("L0 (from decryption)", L, 8, indent="")  # Seharusnya L0 asli
    print_bits_as_matrix("R0 (from decryption)", R, 8, indent="")  # Seharusnya R0 asli
    final_LR = R + L  # Swap: R0 diikuti L0
    print("Before Final Permutation (R0L0):")
    print_bits_as_matrix("R0L0", final_LR, 8, indent="")

    plaintext_bits = permute(final_LR, FP_TABLE)
    print("\nAfter Final Permutation (FP):")
    print_bits_as_matrix("Decrypted Plaintext", plaintext_bits, 8, indent="")
    print("========== DES DECRYPTION END ==========")
    return plaintext_bits


# ==============================================================================
# Contoh Penggunaan
# ==============================================================================

if __name__ == "__main__":
    plaintext_str = "TestDES!"  # 8 karakter ASCII
    key_str = "MySecret"  # 8 karakter ASCII

    print("=" * 70)
    print(" Memulai Simulasi DES")
    print("=" * 70)
    print(f"Plaintext Asli : '{plaintext_str}'")
    print(f"Kunci Asli     : '{key_str}'")

    # --- Konversi ke Biner ---
    try:
        plaintext_bits = string_to_bits(plaintext_str)
        key_bits = string_to_bits(key_str)
        if len(plaintext_bits) != 64:
            print("\nError: Plaintext harus tepat 8 karakter ASCII (64 bit).")
            exit()
        if len(key_bits) != 64:
            print("\nError: Kunci harus tepat 8 karakter ASCII (64 bit).")
            exit()
    except Exception as e:
        print(f"\nError saat konversi input ke biner: {e}")
        exit()

    # --- Enkripsi ---
    try:
        ciphertext_bits = des_encrypt_block(plaintext_bits, key_bits)
        ciphertext_hex = bits_to_hex(ciphertext_bits)

        print("\n--- Hasil Enkripsi Final ---")
        print(f"Ciphertext hex : {ciphertext_hex}")
        print_bits_as_matrix("Ciphertext bits", ciphertext_bits, 8, indent="")
    except Exception as e:
        print(f"\nError saat enkripsi: {e}")
        ciphertext_bits = None  # Tandai agar tidak melanjutkan dekripsi

    # --- Dekripsi ---
    if ciphertext_bits:  # Hanya jalankan jika enkripsi berhasil
        try:
            decrypted_bits = des_decrypt_block(ciphertext_bits, key_bits)
            decrypted_str = bits_to_string(decrypted_bits)

            print("\n--- Hasil Dekripsi Final ---")
            print_bits_as_matrix("Decrypted bits", decrypted_bits, 8, indent="")
            print(
                f"Decrypted text : '{decrypted_str}'"
            )  # Tampilkan dalam kutip agar jelas

            # --- Verifikasi ---
            print("\n--- Verifikasi ---")
            if decrypted_str == plaintext_str:
                print(
                    "✅ Verifikasi BERHASIL: Plaintext asli sama dengan hasil dekripsi."
                )
            else:
                print(
                    "❌ Verifikasi GAGAL: Plaintext asli berbeda dengan hasil dekripsi."
                )
                print(f"   Expected: '{plaintext_str}'")
                print(f"   Got     : '{decrypted_str}'")
        except Exception as e:
            print(f"\nError saat dekripsi: {e}")

    print("\n" + "=" * 70)
    print(" Simulasi DES Selesai")
    print("=" * 70)
