set_bit_in__bitmap — core/include/util/bitmap/bitmap.h, lines 48-68

Sets or clears a single bit at a given index within a bitmap (array of u8).

Pre-conditions:
1. p_bitmap must be a non-null pointer to a writable u8 array.
2. size_of__bitmap must be the number of bits the bitmap is intended to represent (not the byte count).
3. index_of__bit must be less than size_of__bitmap; otherwise the function returns early (debug mode only).
4. state_of__bit is a boolean indicating whether the bit should be set (true) or cleared (false).

Post-conditions:
1. The byte at index (index_of__bit >> 3) in p_bitmap is modified.
2. If state_of__bit is true, the bit at position (index_of__bit & MASK(3)) within that byte is set to 1.
3. If state_of__bit is false, the bit at position (index_of__bit & MASK(3)) within that byte is set to 0.
4. All other bits in the bitmap are unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly computes the byte index via (index_of__bit >> 3) and the bit position within that byte via (index_of__bit & MASK(3)). When setting, it uses BIT(bit_position) | byte to set the target bit. When clearing, it uses (~BIT(bit_position)) & byte to clear the target bit. Both operations preserve all other bits in the byte. The computation matches the semantic intent of setting or clearing a specific bit in a bitmap.

Implementation Correctness:
Type compatibility — index_of__bit >> 3 produces a value used to index a u8 array, which is acceptable (the result is implicitly converted to the array index type, which is fine for reasonable indices). BIT(index_of__bit & MASK(3)) uses the BIT macro which expands to ((1U) << (n)), producing an unsigned int; this is then used in bitwise operations with u8 values, which is safe due to integer promotion. No truncation issues arise because the result is assigned back to a u8 after the bitwise operation completes.
Undefined behavior — no null dereference (p_bitmap is assumed valid by the caller; debug check only guards index bounds), no out-of-bounds access when index_of__bit < size_of__bitmap, no type punning. The debug bounds check prevents out-of-bounds access in debug builds. In release builds (NDEBUG defined), the caller is responsible for ensuring the index is valid.
Validation — the debug-only bounds check is appropriate for a low-level inline utility function. It guards against programmer error during development without imposing runtime overhead in production.

Side Effects:
Mutates the byte at p_bitmap[index_of__bit >> 3]. Specifically, it either sets or clears the bit at position (index_of__bit & MASK(3)) within that byte, leaving all other bits in the bitmap unchanged.
