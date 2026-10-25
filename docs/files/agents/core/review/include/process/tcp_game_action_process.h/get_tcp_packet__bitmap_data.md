get_tcp_packet__bitmap_data — core/source/process/tcp_game_action_process.c

Finds the index of the first unset (0) bit in a bitmap, where each bit represents a TCP packet that has not yet been received/sent. The bitmap uses one bit per packet; a set bit (1) means the packet is accounted for, an unset bit (0) means it is not.

Pre-conditions:
1. p_bitmap must be a non-null pointer to a writable u8 array.
2. p_bitmap must have at least TCP_PAYLOAD_BYTE(quantity_of__tcp_packets__anticipated) bytes allocated (i.e., ceil(quantity_of__tcp_packets__anticipated / 8) bytes).
3. quantity_of__tcp_packets__anticipated is a Quantity__u16 (uint16_t) representing the number of bits/packets tracked in the bitmap.

Post-conditions:
1. Returns an Index__u32 (uint32_t) representing the bit index of the first unset bit in the bitmap.
2. If all bits are set (all packets accounted for), the function is expected to return a value >= quantity_of__tcp_packets__anticipated, which callers use to detect completion.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to scan the bitmap for the first 0 bit and return its global bit index. The logic is correct in normal cases: it skips fully-consumed bytes (0xff) and then finds the first unset bit within the remaining byte, combining the byte offset and bit offset via (byte_index << 3) + bit_index. However, the implementation fails to handle the case where all bytes are 0xff (all packets accounted for). In that scenario, the first loop exits with index_of__bitmap_byte equal to TCP_PAYLOAD_BYTE(quantity_of__tcp_packets__anticipated), which is one past the last valid byte index. The second loop then dereferences p_bitmap[index_of__bitmap_byte], reading memory out of bounds. This is undefined behavior and a clear bug.

Implementation Correctness:
Type compatibility — parameter types match usage correctly. p_bitmap is u8*, indexed by Index__u32 (uint32_t); quantity_of__tcp_packets__anticipated is Quantity__u16 (uint16_t). BIT(n) expands to (1U) << (n), which is unsigned int; the bitwise AND with u8 values promotes correctly. The shift (index_of__bitmap_byte << 3) is safe for uint32_t. No truncation or implicit conversion issues.

Undefined behavior — When all bytes in the bitmap are 0xff, the first loop exits with index_of__bitmap_byte == TCP_PAYLOAD_BYTE(quantity_of__tcp_packets__anticipated), which is out of bounds. The second loop then reads p_bitmap[index_of__bitmap_byte], causing an out-of-bounds read. This occurs precisely when all packets are accounted for, which is a normal and expected condition (the callers check for this to detect completion).

Validation — No input validation (null check, bounds check) is performed. This is acceptable for a low-level internal helper only if callers guarantee valid inputs. However, even with valid inputs (non-null p_bitmap, correctly sized array), the function still exhibits undefined behavior when all bits are set.

Side Effects:
No side effects. The function does not modify p_bitmap or any other memory. It only reads from p_bitmap and returns a computed index.