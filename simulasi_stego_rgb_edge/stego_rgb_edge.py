import numpy as np
import cv2

# Table 5: Edge interval scale table
# Format: list of tuples (lower_limit, upper_limit, num_bits)
TABLE_EDGE = [
    (0, 31, 5),
    (32, 63, 5),
    (64, 95, 5),
    (96, 127, 5),
    (128, 255, 7)
]

# Table 6: Modified interval scale table (non-edge)
TABLE_NON_EDGE = [
    (0, 15, 4),
    (16, 31, 4),
    (32, 63, 5),
    (64, 95, 5),
    (96, 127, 5),
    (128, 191, 6),
    (192, 255, 6)
]

def lookup_table(val_abs, is_edge):
    """
    Looks up the interval parameters for a given absolute difference value.
    Returns: (num_bits, lower_limit)
    """
    table = TABLE_EDGE if is_edge else TABLE_NON_EDGE
    for low, high, bits in table:
        if low <= val_abs <= high:
            return bits, low
    # Fallback to the last entry
    return table[-1][2], table[-1][0]

def compute_log_image(g_channel, ksize=5, sigma=0.5):
    """
    Computes the Laplacian of Gaussian (LoG) image on the green channel.
    Returns a uint8 image containing the absolute value of the Laplacian.
    """
    blur = cv2.GaussianBlur(g_channel, (ksize, ksize), sigma)
    laplacian = cv2.Laplacian(blur, cv2.CV_64F)
    log_image = np.uint8(np.abs(laplacian))
    return log_image

def is_edge_block(log_block, threshold=64, min_edge_pixels=950):
    """
    Determines if a block is an edge block based on the number of edge pixels.
    Note: The benchmark pixel P_0 (index 0) is excluded from the count.
    """
    # Flatten the block to 1D and exclude the first pixel
    flat = log_block.flatten()
    pixels_to_check = flat[1:]
    
    # Count pixels with value > threshold
    edge_pixels = np.sum(pixels_to_check > threshold)
    return edge_pixels >= min_edge_pixels

def distribute_change(p_other, p_g, m, d_val):
    """
    Distributes the difference change m between the G channel and the other channel (R or B).
    Based on equations (21) and (23).
    """
    is_odd = (d_val % 2 != 0)
    
    # Calculate ceil and floor for 0.6m and 0.4m
    c_r = int(np.ceil(m * 0.6))
    f_g = int(np.floor(m * 0.4))
    f_r = int(np.floor(m * 0.6))
    c_g = int(np.ceil(m * 0.4))
    
    if is_odd:
        p_other_new = p_other - c_r
        p_g_new = p_g + f_g
    else:
        p_other_new = p_other - f_r
        p_g_new = p_g + c_g
        
    return p_other_new, p_g_new

def adjust_overflow(pr, pg, pb):
    """
    Adjusts the R, G, B values if they fall outside [0, 255] by shifting all channels together.
    Based on the paper's Step 10.
    """
    # Repeat a few times to resolve secondary overflows (if any)
    for _ in range(3):
        # R overflow/underflow
        if pr > 255:
            diff = pr - 255
            pr, pg, pb = 255, pg - diff, pb - diff
        elif pr < 0:
            diff = -pr
            pr, pg, pb = 0, pg + diff, pb + diff
            
        # G overflow/underflow
        if pg > 255:
            diff = pg - 255
            pr, pg, pb = pr - diff, 255, pb - diff
        elif pg < 0:
            diff = -pg
            pr, pg, pb = pr + diff, 0, pb + diff
            
        # B overflow/underflow
        if pb > 255:
            diff = pb - 255
            pr, pg, pb = pr - diff, pg - diff, 255
        elif pb < 0:
            diff = -pb
            pr, pg, pb = pr + diff, pg + diff, 0
            
    # Final clip just in case of numeric precision errors
    pr = max(0, min(255, int(round(pr))))
    pg = max(0, min(255, int(round(pg))))
    pb = max(0, min(255, int(round(pb))))
    return pr, pg, pb

def encode_pixel(pr, pg, pb, bitstream, bit_pos, is_edge):
    """
    Embeds secret bits into a single pixel (pr, pg, pb).
    Returns: (stego_r, stego_g, stego_b, bits_consumed)
    """
    bits_consumed = 0
    
    # 1. R-G Group
    d1 = pg - pr
    n1, l1 = lookup_table(abs(d1), is_edge)
    
    # Read n1 bits from bitstream
    b1 = 0
    actual_n1 = min(n1, len(bitstream) - bit_pos)
    if actual_n1 > 0:
        for i in range(actual_n1):
            b1 = (b1 << 1) | bitstream[bit_pos + i]
        bits_consumed += actual_n1
        bit_pos += actual_n1
        
        # Pad with 0s if we ran out of bits
        if actual_n1 < n1:
            b1 = b1 << (n1 - actual_n1)
    else:
        # No bits to embed, return original pixel
        return pr, pg, pb, 0
        
    # Calculate new difference d'1
    d1_prime = (l1 + b1) if d1 >= 0 else -(l1 + b1)
    m1 = d1_prime - d1
    
    # Distribute change m1
    pr1, pg1 = distribute_change(pr, pg, m1, d1)
    
    # 2. G1-B Group
    d2 = pg1 - pb
    n2, l2 = lookup_table(abs(d2), is_edge)
    
    # Read n2 bits from bitstream
    b2 = 0
    actual_n2 = min(n2, len(bitstream) - bit_pos)
    if actual_n2 > 0:
        for i in range(actual_n2):
            b2 = (b2 << 1) | bitstream[bit_pos + i]
        bits_consumed += actual_n2
        bit_pos += actual_n2
        
        # Pad with 0s if we ran out of bits
        if actual_n2 < n2:
            b2 = b2 << (n2 - actual_n2)
    else:
        # If we run out of bits here, we pad with 0s and embed anyway
        # (This keeps the G1/B difference matching the block's edge status)
        b2 = 0
        
    # Calculate new difference d'2
    d2_prime = (l2 + b2) if d2 >= 0 else -(l2 + b2)
    m2 = d2_prime - d2
    
    # Distribute change m2
    pb1, pg2 = distribute_change(pb, pg1, m2, d2)
    
    # 3. Superposition
    pg_stego = int(round((pg1 + pg2) / 2.0))
    pr_stego = pr1 - (pg1 - pg_stego)
    pb_stego = pb1 - (pg2 - pg_stego)
    
    # 4. Overflow Adjustment
    pr_stego, pg_stego, pb_stego = adjust_overflow(pr_stego, pg_stego, pb_stego)
    
    return pr_stego, pg_stego, pb_stego, bits_consumed

def decode_pixel(pr, pg, pb, is_edge):
    """
    Extracts embedded bits from a single pixel (pr, pg, pb).
    Returns: (bits_list_1, bits_list_2)
    """
    # Calculate absolute differences
    d1_prime = abs(pg - pr)
    d2_prime = abs(pg - pb)
    
    # 1. R-G Group
    n1, l1 = lookup_table(d1_prime, is_edge)
    w1 = max(0, d1_prime - l1)
    # Limit w1 to max value representable by n1 bits to avoid overflow
    w1 = min(w1, (1 << n1) - 1)
    
    # Convert w1 to n1 bits
    bits1 = []
    for i in range(n1 - 1, -1, -1):
        bits1.append((w1 >> i) & 1)
        
    # 2. G-B Group
    n2, l2 = lookup_table(d2_prime, is_edge)
    w2 = max(0, d2_prime - l2)
    # Limit w2 to max value representable by n2 bits
    w2 = min(w2, (1 << n2) - 1)
    
    # Convert w2 to n2 bits
    bits2 = []
    for i in range(n2 - 1, -1, -1):
        bits2.append((w2 >> i) & 1)
        
    return bits1, bits2

def str_to_bits(s):
    """Converts a UTF-8 string to a list of bits (0 or 1)."""
    by = s.encode('utf-8')
    bits = []
    for b in by:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def bits_to_str(bits):
    """Converts a list of bits back to a UTF-8 string."""
    # Group bits into bytes
    by = bytearray()
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        if len(byte_bits) < 8:
            break
        val = 0
        for bit in byte_bits:
            val = (val << 1) | bit
        by.append(val)
    # Decode string, ignoring errors from padding
    return by.decode('utf-8', errors='ignore')

def encode_image(cover_path, payload_str, output_path, log_threshold=64, min_edge_pixels=950):
    """
    Encodes a payload string into the cover image.
    Saves the stego image to output_path.
    """
    img = cv2.imread(cover_path)
    if img is None:
        raise ValueError(f"Could not load image at {cover_path}")
        
    h, w, c = img.shape
    
    # Split into B, G, R (OpenCV default is BGR)
    b_chan = img[:, :, 0].astype(np.float64)
    g_chan = img[:, :, 1].astype(np.float64)
    r_chan = img[:, :, 2].astype(np.float64)
    
    # Compute LoG image on the ORIGINAL G channel
    log_image = compute_log_image(img[:, :, 1], ksize=5, sigma=0.5)
    
    # Convert payload to bits
    payload_bits = str_to_bits(payload_str)
    payload_len = len(payload_bits)
    
    # Prepend the 32-bit length header
    len_bits = []
    for i in range(31, -1, -1):
        len_bits.append((payload_len >> i) & 1)
        
    bitstream = len_bits + payload_bits
    bit_pos = 0
    
    # Output arrays
    stego_b = b_chan.copy()
    stego_g = g_chan.copy()
    stego_r = r_chan.copy()
    
    # Process 32x32 blocks
    blocks_y = h // 32
    blocks_x = w // 32
    
    total_embedded_bits = 0
    
    for by_idx in range(blocks_y):
        for bx_idx in range(blocks_x):
            y_start = by_idx * 32
            x_start = bx_idx * 32
            
            # Extract G block and LoG block
            g_block = g_chan[y_start:y_start+32, x_start:x_start+32]
            log_block = log_image[y_start:y_start+32, x_start:x_start+32]
            
            # Determine if this block is an edge block (using original channels)
            is_edge = is_edge_block(log_block, threshold=log_threshold, min_edge_pixels=min_edge_pixels)
            
            # Update the G benchmark pixel LSB
            p0_g = int(g_block[0, 0])
            if is_edge:
                p0_g_new = (p0_g & 0xFE) | 1
            else:
                p0_g_new = p0_g & 0xFE
            stego_g[y_start, x_start] = p0_g_new
            
            # Process remaining pixels in row-major order
            for i in range(1024):
                if i == 0:
                    continue  # skip benchmark pixel
                    
                ry = i // 32
                rx = i % 32
                
                curr_y = y_start + ry
                curr_x = x_start + rx
                
                if bit_pos >= len(bitstream):
                    # No more bits left, we can stop embedding
                    break
                    
                # Get current original pixel
                pr = r_chan[curr_y, curr_x]
                pg = g_chan[curr_y, curr_x]
                pb = b_chan[curr_y, curr_x]
                
                # Encode pixel
                pr_new, pg_new, pb_new, consumed = encode_pixel(
                    pr, pg, pb, bitstream, bit_pos, is_edge
                )
                
                stego_r[curr_y, curr_x] = pr_new
                stego_g[curr_y, curr_x] = pg_new
                stego_b[curr_y, curr_x] = pb_new
                
                bit_pos += consumed
                total_embedded_bits += consumed
                
            if bit_pos >= len(bitstream):
                # Embedded all bits
                break
        if bit_pos >= len(bitstream):
            break
            
    if bit_pos < len(bitstream):
        print(f"Warning: Payload too large for the image. Only embedded {bit_pos} / {len(bitstream)} bits.")
        
    # Reconstruct stego image
    stego_img = np.zeros((h, w, 3), dtype=np.uint8)
    stego_img[:, :, 0] = np.clip(stego_b, 0, 255).astype(np.uint8)
    stego_img[:, :, 1] = np.clip(stego_g, 0, 255).astype(np.uint8)
    stego_img[:, :, 2] = np.clip(stego_r, 0, 255).astype(np.uint8)
    
    cv2.imwrite(output_path, stego_img)
    return total_embedded_bits, len(bitstream)

def decode_image(stego_path, log_threshold=64):
    """
    Decodes the stego image at stego_path and extracts the hidden message.
    """
    img = cv2.imread(stego_path)
    if img is None:
        raise ValueError(f"Could not load image at {stego_path}")
        
    h, w, c = img.shape
    
    # Split into B, G, R channels
    b_chan = img[:, :, 0].astype(np.int32)
    g_chan = img[:, :, 1].astype(np.int32)
    r_chan = img[:, :, 2].astype(np.int32)
    
    # Process 32x32 blocks
    blocks_y = h // 32
    blocks_x = w // 32
    
    extracted_bits = []
    
    # Track decoding state
    payload_len = None
    
    for by_idx in range(blocks_y):
        for bx_idx in range(blocks_x):
            y_start = by_idx * 32
            x_start = bx_idx * 32
            
            # Read benchmark pixel LSB in G channel
            p0_g = g_chan[y_start, x_start]
            is_edge = (p0_g & 1) == 1
            
            # Process remaining pixels in row-major order
            for i in range(1024):
                if i == 0:
                    continue  # skip benchmark pixel
                    
                ry = i // 32
                rx = i % 32
                
                curr_y = y_start + ry
                curr_x = x_start + rx
                
                pr = r_chan[curr_y, curr_x]
                pg = g_chan[curr_y, curr_x]
                pb = b_chan[curr_y, curr_x]
                
                # Decode pixel
                bits1, bits2 = decode_pixel(pr, pg, pb, is_edge)
                
                extracted_bits.extend(bits1)
                extracted_bits.extend(bits2)
                
                # Check if we have extracted the 32-bit length header
                if payload_len is None and len(extracted_bits) >= 32:
                    len_bits = extracted_bits[:32]
                    payload_len = 0
                    for bit in len_bits:
                        payload_len = (payload_len << 1) | bit
                        
                # Check if we have extracted the entire payload
                if payload_len is not None and len(extracted_bits) >= 32 + payload_len:
                    # We have all bits! Cut off here.
                    actual_payload_bits = extracted_bits[32 : 32 + payload_len]
                    return bits_to_str(actual_payload_bits)
                    
    # If we get here, either we didn't find the length or the image didn't contain enough bits
    if payload_len is not None:
        print(f"Warning: Reached end of image before extracting full payload. Expected {payload_len} bits, got {len(extracted_bits) - 32} bits.")
        actual_payload_bits = extracted_bits[32:]
        return bits_to_str(actual_payload_bits)
        
    return ""
