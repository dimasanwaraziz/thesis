import numpy as np
import cv2
from stego_rgb_edge import (
    compute_log_image, is_edge_block, lookup_table,
    distribute_change, adjust_overflow, encode_pixel, decode_pixel, str_to_bits
)

def test_debug():
    cover_path = "cover.png"
    img = cv2.imread(cover_path)
    h, w, c = img.shape
    b_chan = img[:, :, 0].astype(np.float64)
    g_chan = img[:, :, 1].astype(np.float64)
    r_chan = img[:, :, 2].astype(np.float64)
    
    log_image = compute_log_image(img[:, :, 1], ksize=5, sigma=0.5)
    
    # Generate the same payload as in the failed run
    import random
    import string
    random.seed(42)  # Use fixed seed if possible, but run_simulation didn't seed.
    # Wait, we can just generate a random string of 3,000,000 chars with a fixed seed.
    letters = string.ascii_letters + string.digits + " ,.!?\n"
    # To match the simulation:
    num_blocks = (h // 32) * (w // 32)
    available_pixels = num_blocks * 1023
    est_capacity_bits = available_pixels * 10
    est_capacity_chars = est_capacity_bits // 8
    payload_len = min(3000000, est_capacity_chars - 1000)
    
    payload_str = ''.join(random.choice(letters) for _ in range(payload_len))
    payload_bits = str_to_bits(payload_str)
    payload_len_bits = len(payload_bits)
    
    len_bits = []
    for i in range(31, -1, -1):
        len_bits.append((payload_len_bits >> i) & 1)
    bitstream = len_bits + payload_bits
    
    bit_pos = 0
    blocks_y = h // 32
    blocks_x = w // 32
    
    clipped_count = 0
    mismatch_count = 0
    
    for by_idx in range(blocks_y):
        for bx_idx in range(blocks_x):
            y_start = by_idx * 32
            x_start = bx_idx * 32
            
            g_block = g_chan[y_start:y_start+32, x_start:x_start+32]
            log_block = log_image[y_start:y_start+32, x_start:x_start+32]
            is_edge = is_edge_block(log_block, threshold=64, min_edge_pixels=950)
            
            # Simulation of encoding and decoding on the fly to detect first discrepancy
            for i in range(1024):
                if i == 0:
                    continue
                ry = i // 32
                rx = i % 32
                curr_y = y_start + ry
                curr_x = x_start + rx
                
                if bit_pos >= len(bitstream):
                    break
                    
                pr = r_chan[curr_y, curr_x]
                pg = g_chan[curr_y, curr_x]
                pb = b_chan[curr_y, curr_x]
                
                # Save bitstream segment for verification
                # We need to know how many bits will be consumed
                d1 = pg - pr
                n1, _ = lookup_table(abs(d1), is_edge)
                
                # Check actual bits to be encoded
                actual_n1 = min(n1, len(bitstream) - bit_pos)
                bits1_to_embed = bitstream[bit_pos : bit_pos + actual_n1]
                
                # Pad if needed
                if len(bits1_to_embed) < n1:
                    bits1_to_embed = bits1_to_embed + [0] * (n1 - len(bits1_to_embed))
                    
                # G1-B group estimate
                # To get exact G1, we simulate R-G encoding
                b1_val = 0
                for bit in bits1_to_embed:
                    b1_val = (b1_val << 1) | bit
                d1_prime = (lookup_table(abs(d1), is_edge)[1] + b1_val) if d1 >= 0 else -(lookup_table(abs(d1), is_edge)[1] + b1_val)
                m1 = d1_prime - d1
                pr1, pg1 = distribute_change(pr, pg, m1, d1)
                
                d2 = pg1 - pb
                n2, _ = lookup_table(abs(d2), is_edge)
                actual_n2 = min(n2, len(bitstream) - (bit_pos + actual_n1))
                bits2_to_embed = bitstream[bit_pos + actual_n1 : bit_pos + actual_n1 + actual_n2]
                if len(bits2_to_embed) < n2:
                    bits2_to_embed = bits2_to_embed + [0] * (n2 - len(bits2_to_embed))
                
                expected_bits = bits1_to_embed + bits2_to_embed
                
                # Run the actual encode
                pr_new, pg_new, pb_new, consumed = encode_pixel(
                    pr, pg, pb, bitstream, bit_pos, is_edge
                )
                
                # Run decode on the new values
                dec_bits1, dec_bits2 = decode_pixel(pr_new, pg_new, pb_new, is_edge)
                decoded_bits = dec_bits1 + dec_bits2
                
                # Compare expected vs decoded
                if expected_bits != decoded_bits:
                    mismatch_count += 1
                    print(f"\nDiscrepancy found at pixel ({curr_x}, {curr_y}) in block ({bx_idx}, {by_idx}), pixel index {i}:")
                    print(f"Original RGB: ({pr}, {pg}, {pb})")
                    print(f"Encoded RGB:  ({pr_new}, {pg_new}, {pb_new})")
                    print(f"Is Edge Block: {is_edge}")
                    print(f"Original diffs: d1={d1}, d2={d2}")
                    print(f"Expected bits:  {expected_bits}")
                    print(f"Decoded bits:   {decoded_bits}")
                    print(f"Bit Position in stream: {bit_pos}")
                    
                    # Check if clipping occurred
                    # Let's run stego through superposition without clipping to see what it would be
                    b2_val = 0
                    for bit in bits2_to_embed:
                        b2_val = (b2_val << 1) | bit
                    d2_prime = (lookup_table(abs(d2), is_edge)[1] + b2_val) if d2 >= 0 else -(lookup_table(abs(d2), is_edge)[1] + b2_val)
                    m2 = d2_prime - d2
                    pb1, pg2 = distribute_change(pb, pg1, m2, d2)
                    pg_stego = int(round((pg1 + pg2) / 2.0))
                    pr_stego = pr1 - (pg1 - pg_stego)
                    pb_stego = pb1 - (pg2 - pg_stego)
                    print(f"Before overflow adjustment: ({pr_stego}, {pg_stego}, {pb_stego})")
                    
                    # Return to stop at first error
                    return
                
                bit_pos += consumed
            if bit_pos >= len(bitstream):
                break
        if bit_pos >= len(bitstream):
            break
            
    print("No discrepancies found during pixel-by-pixel check.")

if __name__ == "__main__":
    test_debug()
