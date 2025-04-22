import cv2
import numpy as np
import random
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
from reedsolo import RSCodec, ReedSolomonError

# ===== Reed-Solomon Implementation for Image Steganography =====
def reed_muller_encode(data, n=4, k=11):
    """Simulates Reed-Muller Code encoding using Reed-Solomon."""
    rsc = RSCodec(2**n - k)
    encoded_data = b""
    for byte in data.tobytes():
        encoded_data += rsc.encode(bytes([byte]))
    return np.frombuffer(encoded_data, dtype=np.uint8)

def reed_muller_decode(data, n=4, k=11):
    """Decodes binary data from Reed-Muller Code embedding."""
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
    """Embeds secret image using Reed-Muller Code."""
    host_gray = cv2.cvtColor(host_img, cv2.COLOR_BGR2GRAY)
    secret_bin = secret_img.flatten()
    encoded_data = reed_muller_encode(secret_bin, n, k)
    
    if len(encoded_data) > host_gray.size:
        raise ValueError("Secret image too large to embed in host image.")
        
    host_gray_flat = host_gray.flatten()
    random_indices = np.random.permutation(len(host_gray_flat))[: len(encoded_data)]
    host_gray_flat[random_indices] = encoded_data
    embedded_img = host_gray_flat.reshape(host_gray.shape)
    
    return embedded_img

def extract_image_reed_muller(embedded_img, secret_shape, n=4, k=11):
    """Extracts image embedded using Reed-Muller decoding."""
    embedded_flat = embedded_img.flatten()
    num_secret_bytes = np.prod(secret_shape)
    expected_encoded_size = num_secret_bytes * (2**n // k)
    
    extracted_bytes = embedded_flat[:expected_encoded_size]
    decoded_data = reed_muller_decode(extracted_bytes, n, k)
    
    # Handle size mismatch
    if decoded_data.size < num_secret_bytes:
        decoded_data = np.pad(
            decoded_data, (0, num_secret_bytes - decoded_data.size), mode="constant"
        )
    elif decoded_data.size > num_secret_bytes:
        decoded_data = decoded_data[:num_secret_bytes]
    
    return decoded_data.reshape(secret_shape)

def compute_capacity(secret_img, host_img):
    """Calculates embedding capacity in bits per pixel (bpp)."""
    return np.prod(secret_img.shape) / np.prod(host_img.shape)

# ===== LSB Steganography Implementation =====
def lsb_embed(cover_pixel, data_bit):
    """Embeds a single bit in the least significant bit of a pixel."""
    return (cover_pixel & ~1) | data_bit

def lsb_extract(stego_pixel):
    """Extracts the least significant bit from a pixel."""
    return stego_pixel & 1

# ===== Blum Blum Shub PRNG Implementation =====
def blum_blum_shub(seed, length):
    """
    Generates a sequence of pseudorandom bits using the Blum-Blum-Shub algorithm.
    
    Args:
        seed: The initial seed value
        length: Number of bits to generate
        
    Returns:
        A list of pseudorandom bits
    """
    p = 107  # Example prime number
    q = 191  # Another example prime number
    n = p * q
    x = seed
    result = []
    
    for _ in range(length):
        x = (x * x) % n
        result.append(x % 2)  # Take LSB
        
    return result

# ===== Reed-Muller (1,m) Code Implementation =====
def generate_generator_matrix_rm1m(m):
    """Generates generator matrix for RM(1, m)."""
    n = 2**m
    k = m + 1
    G = [[0] * n for _ in range(k)]
    
    # First row is all 1s (for overall parity)
    G[0] = [1] * n
    
    # Next rows are binary representations of indices
    for i in range(1, k):
        for j in range(n):
            if (j >> (i - 1)) & 1:
                G[i][j] = 1
                
    return G

def encode_rm1m(message, m):
    """Encodes a message using RM(1, m)."""
    G = generate_generator_matrix_rm1m(m)
    n = 2**m
    k = m + 1
    
    if len(message) != k:
        raise ValueError("Message length must be equal to m + 1.")
        
    codeword = [0] * n
    for i in range(n):
        for j in range(k):
            codeword[i] ^= message[j] * G[j][i]
            
    return codeword

def majority_decode_rm1m(received_word, m):
    """Performs majority logic decoding for RM(1, m)."""
    n = 2**m
    k = m + 1
    
    # Calculate overall parity
    overall_parity = 0
    for bit in received_word:
        overall_parity ^= bit
        
    # Calculate parity for each information bit
    information_parities = [0] * m
    for i in range(m):
        for j in range(n):
            if (j >> i) & 1:
                information_parities[i] ^= received_word[j]
                
    # Make decision based on majority
    decoded_message = [overall_parity]
    for parity in information_parities:
        decoded_message.append(parity)
        
    return decoded_message

# ===== Example Usage for Image Steganography =====
def run_steganography_example():
    # Load images
    host = cv2.imread("host_image.png")
    secret = cv2.imread("secret_image.png", cv2.IMREAD_GRAYSCALE)
    
    # Calculate capacity
    capacity_before = compute_capacity(secret, host)
    print(f"Capacity before embedding: {capacity_before:.4f} bpp")
    
    # Embed secret image
    embedded = embed_image_reed_muller(host, secret)
    cv2.imwrite("embedded_reed_muller.png", embedded.astype(np.uint8))
    
    # Extract secret image
    extracted = extract_image_reed_muller(embedded, secret.shape)
    cv2.imwrite("extracted_reed_muller.png", extracted.astype(np.uint8))
    
    # Calculate metrics
    capacity_after = compute_capacity(extracted, host)
    print(f"Capacity after embedding: {capacity_after:.4f} bpp")
    
    host_gray = cv2.cvtColor(host, cv2.COLOR_BGR2GRAY)
    psnr = peak_signal_noise_ratio(host_gray, embedded)
    ssim = structural_similarity(host_gray, embedded)
    
    print(f"PSNR: {psnr:.2f} dB")
    print(f"SSIM: {ssim:.4f}")

# ===== Example Usage for Reed-Muller Coding =====
def run_rm_coding_example():
    m = 4  # Example: RM(1, 4)
    k = m + 1
    message = [1, 0, 1, 0, 1]  # 5-bit message
    
    # Encoding
    codeword = encode_rm1m(message, m)
    print(f"Message: {message}")
    print(f"Encoded Codeword: {codeword}")
    
    # Simulate error (e.g., flip one bit)
    received_word = list(codeword)  # Copy codeword
    error_position = 3
    received_word[error_position] = 1 - received_word[error_position]  # Flip bit
    print(f"Codeword with Error: {received_word}")
    
    # Decoding
    decoded_message = majority_decode_rm1m(received_word, m)
    print(f"Decoded Message: {decoded_message}")

# ===== Example for Simple Reed-Muller and LSB Embedding =====
def run_simple_encoding_example():
    # Simple Reed-Muller encoding example
    data = [1, 0, 1, 0]
    
    # Simple encoder (just for illustration)
    def simple_reed_muller_encode(data):
        return data + [sum(data) % 2]  # Add parity bit
        
    def simple_reed_muller_decode(encoded_data):
        return encoded_data[:-1]  # Remove parity bit
    
    encoded = simple_reed_muller_encode(data)
    print(f"Data: {data}, Encoded: {encoded}")
    
    decoded = simple_reed_muller_decode(encoded)
    print(f"Encoded: {encoded}, Decoded: {decoded}")
    
    # LSB Embedding example
    cover = 128
    secret = 1
    stego = lsb_embed(cover, secret)
    print(f"Cover: {cover}, Secret: {secret}, Stego: {stego}")
    
    extracted = lsb_extract(stego)
    print(f"Stego: {stego}, Extracted: {extracted}")
    
    # Blum Blum Shub example
    seed = random.randint(1, 1000)  # Choose random seed
    random_bits = blum_blum_shub(seed, 10)
    print(f"Seed: {seed}, Random Bits: {random_bits}")

# Uncomment to run examples
# if __name__ == "__main__":
#     run_steganography_example()
#     run_rm_coding_example()
#     run_simple_encoding_example()