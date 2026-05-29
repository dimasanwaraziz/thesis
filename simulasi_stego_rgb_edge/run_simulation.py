import os
import random
import string
import numpy as np
import cv2
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity as ssim

from stego_rgb_edge import encode_image, decode_image

def calculate_psnr(img1, img2):
    mse = np.mean((img1.astype(np.float64) - img2.astype(np.float64)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * np.log10((255.0 ** 2) / mse)

def calculate_ssim(img1, img2):
    ssims = []
    for i in range(img1.shape[2]):
        c_ssim = ssim(img1[:, :, i], img2[:, :, i], data_range=255.0)
        ssims.append(c_ssim)
    return np.mean(ssims)

def generate_random_string(length):
    # Generates a random alphanumeric string
    letters = string.ascii_letters + string.digits + " ,.!?\n"
    return ''.join(random.choice(letters) for _ in range(length))

def generate_synthetic_cover(path, size=512):
    # Generates a beautiful gradient-textured cover image for testing
    print("Generating a synthetic cover image...")
    # Create gradient channels
    y, x = np.mgrid[0:size, 0:size]
    # Red gradient
    r = (np.sin(x / 30.0) * 127 + 128).astype(np.uint8)
    # Green channel with complex textures (good for edges)
    g = ((x * y) / (size * size / 255.0)).astype(np.uint8)
    # Blue gradient
    b = (np.cos(y / 20.0) * 127 + 128).astype(np.uint8)
    
    img = np.zeros((size, size, 3), dtype=np.uint8)
    img[:, :, 0] = b
    img[:, :, 1] = g
    img[:, :, 2] = r
    
    cv2.imwrite(path, img)
def preprocess_image(img, max_diff=55):
    # Pull extreme channel differences closer to the pixel average
    # to avoid steganography boundary overflow/clipping.
    img_float = img.astype(np.float64)
    avg = np.mean(img_float, axis=2, keepdims=True)
    diff = img_float - avg
    diff_clipped = np.clip(diff, -max_diff, max_diff)
    adjusted = avg + diff_clipped
    return np.clip(adjusted, 0, 255).astype(np.uint8)

def estimate_exact_capacity(img, log_threshold=64, min_edge_pixels=950):
    from stego_rgb_edge import compute_log_image, is_edge_block, lookup_table
    h, w, _ = img.shape
    g_chan = img[:, :, 1].astype(np.float64)
    r_chan = img[:, :, 2].astype(np.float64)
    b_chan = img[:, :, 0].astype(np.float64)
    
    log_image = compute_log_image(img[:, :, 1], ksize=5, sigma=0.5)
    
    blocks_y = h // 32
    blocks_x = w // 32
    
    total_bits = 0
    for by in range(blocks_y):
        for bx in range(blocks_x):
            y_start = by * 32
            x_start = bx * 32
            
            log_block = log_image[y_start:y_start+32, x_start:x_start+32]
            is_edge = is_edge_block(log_block, threshold=log_threshold, min_edge_pixels=min_edge_pixels)
            
            # Sum capacity of all non-benchmark pixels
            for i in range(1024):
                if i == 0:
                    continue
                ry = i // 32
                rx = i % 32
                cy = y_start + ry
                cx = x_start + rx
                
                d1 = g_chan[cy, cx] - r_chan[cy, cx]
                n1, _ = lookup_table(abs(d1), is_edge)
                
                d2 = g_chan[cy, cx] - b_chan[cy, cx]
                n2, _ = lookup_table(abs(d2), is_edge)
                
                total_bits += (n1 + n2)
    return total_bits

def main():
    cover_path = "cover.png"
    stego_path = "stego.png"
    
    # 1. Setup cover image
    if not os.path.exists(cover_path):
        # Look for host_image.png in parent kodepython
        parent_host = "../kodepython/host_image.png"
        parent_test = "../kodepython/test_image.png"
        if os.path.exists(parent_host):
            print(f"Found host image in parent directory: {parent_host}. Copying...")
            img = cv2.imread(parent_host)
            # Resize to 512x512 if too large, to speed up simulation
            if img.shape[0] > 512 or img.shape[1] > 512:
                img = cv2.resize(img, (512, 512))
            cv2.imwrite(cover_path, img)
        elif os.path.exists(parent_test):
            print(f"Found test image in parent directory: {parent_test}. Copying...")
            img = cv2.imread(parent_test)
            if img.shape[0] > 512 or img.shape[1] > 512:
                img = cv2.resize(img, (512, 512))
            cv2.imwrite(cover_path, img)
        else:
            generate_synthetic_cover(cover_path, size=512)
            
    cover_img = cv2.imread(cover_path)
    print("Preprocessing cover image to prevent boundary overflow/clipping...")
    cover_img = preprocess_image(cover_img, max_diff=55)
    cv2.imwrite(cover_path, cover_img)
    
    h, w, c = cover_img.shape
    print(f"Cover Image dimensions: {w}x{h} ({c} channels)")
    
    # 2. Calculate exact payload capacity
    print("Estimating exact payload capacity...")
    exact_capacity_bits = estimate_exact_capacity(cover_img)
    exact_capacity_chars = exact_capacity_bits // 8
    print(f"Exact Max Capacity: {exact_capacity_bits:,} bits ({exact_capacity_chars:,} characters)")
    
    # Fill up to 98% of capacity to prevent index out of bounds
    payload_len = (exact_capacity_bits - 1032) // 8
    print(f"Generating random payload of {payload_len:,} characters...")
    original_message = generate_random_string(payload_len)
    
    # 3. Encode message
    print("\n--- Encoding ---")
    log_threshold = 64
    min_edge_pixels = 950
    total_embedded, total_bitstream = encode_image(
        cover_path, original_message, stego_path, 
        log_threshold=log_threshold, min_edge_pixels=min_edge_pixels
    )
    print(f"Successfully embedded {total_embedded:,} / {total_bitstream:,} bits of bitstream.")
    
    # 4. Decode message
    print("\n--- Decoding ---")
    extracted_message = decode_image(stego_path, log_threshold=log_threshold)
    print(f"Successfully extracted message. Length: {len(extracted_message):,} characters.")
    
    # 5. Verify correctness
    print("\n--- Verification ---")
    messages_match = (original_message == extracted_message)
    print(f"Result: Messages match EXACTLY? {messages_match}")
    if not messages_match:
        print("Error: Extracted message does not match original message!")
        # Print differences
        mismatches = 0
        for idx in range(min(len(original_message), len(extracted_message))):
            if original_message[idx] != extracted_message[idx]:
                print(f"Mismatch at index {idx}: Original={repr(original_message[idx])}, Extracted={repr(extracted_message[idx])}")
                mismatches += 1
                if mismatches >= 10:
                    break
        assert False, "Verification failed!"
    else:
        print("Verification successful! Steganography works perfectly!")
        
    # 6. Calculate performance metrics
    stego_img = cv2.imread(stego_path)
    psnr_val = calculate_psnr(cover_img, stego_img)
    ssim_val = calculate_ssim(cover_img, stego_img)
    bpp = total_embedded / (h * w)
    
    print("\n--- Performance Metrics ---")
    print(f"Embedding Capacity (bits): {total_embedded:,} bits")
    print(f"Embedding Rate (bpp):      {bpp:.4f} bits/pixel")
    print(f"PSNR (dB):                 {psnr_val:.4f} dB")
    print(f"SSIM:                      {ssim_val:.4f}")
    
    # 7. Generate visualization plot
    print("\nGenerating visualization plots...")
    # Convert BGR to RGB for matplotlib
    cover_rgb = cv2.cvtColor(cover_img, cv2.COLOR_BGR2RGB)
    stego_rgb = cv2.cvtColor(stego_img, cv2.COLOR_BGR2RGB)
    
    # Compute visual difference (amplified)
    diff = np.abs(cover_rgb.astype(np.float64) - stego_rgb.astype(np.float64))
    diff_amplified = np.clip(diff * 10.0, 0, 255).astype(np.uint8)
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    axes[0].imshow(cover_rgb)
    axes[0].set_title(f"Cover Image\n({w}x{h})")
    axes[0].axis('off')
    
    axes[1].imshow(stego_rgb)
    axes[1].set_title(f"Stego Image\nPSNR = {psnr_val:.2f} dB | SSIM = {ssim_val:.4f}")
    axes[1].axis('off')
    
    # Show difference image. If it's completely black, they are identical.
    axes[2].imshow(diff_amplified)
    axes[2].set_title("Difference (Residual x10)\n(Amplified to show changes)")
    axes[2].axis('off')
    
    # Add text banner with metrics
    fig.suptitle(f"Color Steganography (RGB Model + Edge Detection)\nCapacity: {total_embedded:,} bits ({bpp:.2f} bpp) | Success: {messages_match}", fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig("simulation_result.png", dpi=150)
    print("Visualization plot saved as simulation_result.png")
    
if __name__ == "__main__":
    main()
