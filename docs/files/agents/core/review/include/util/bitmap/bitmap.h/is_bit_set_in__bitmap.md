is_bit_set_in__bitmap — core/include/util/bitmap/bitmap.h

Queries whether a specific bit is set in a bitmap array.

Pre-conditions:
1. p_bitmap must be a non-null pointer to a u8 array that has been allocated with at least (size_of__bitmap >> 3) bytes (i.e., enough bytes to cover all bits).
2. size_of__bitmap is the total number of bits represented by the bitmap, not the number of bytes.
3. index_of__bit must be less than size_of__bitmap; otherwise the behavior is undefined in release builds and returns false in debug builds.
4. No null-check is performed on p_bitmap; it is the caller's responsibility to ensure validity.

Post-conditions:
1. Returns true if the bit at position index_of__bit within p_bitmap is set (1); returns false if it is clear (0) or if the index is out of bounds (debug builds only).
2. The bitmap array is not modified; this is a read-only query.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent, as indicated by its name, is to determine whether a specific bit in a bitmap array is set. The implementation correctly:
  - Extracts the byte index via (index_of__bit >> 3), which divides the bit index by 8 to select the correct byte.
  - Extracts the bit position within that byte via (index_of__bit & MASK(3)), which isolates the lower 3 bits (range 0–7).
  - Constructs a single-bit mask via BIT(index_of__bit & MASK(3)) and ANDs it with the selected byte to test whether that specific bit is set.
  - Returns a boolean indicating the result.
The computation matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — BIT(n) expands to ((1U) << (n)), which yields an unsigned int (u32). p_bitmap[...] yields a u8, which is promoted to int (or unsigned int) during the bitwise AND. The resulting integer is implicitly converted to bool for the return value: zero becomes false, any non-zero becomes true. This conversion is well-defined in C and produces the correct boolean result. No truncation or data loss occurs because only a single bit position (0–7) is ever tested.
Undefined behavior — No pointer arithmetic beyond array indexing, no null dereference (caller's responsibility), no type punning, no out-of-bounds access (guarded by the debug-only bounds check; in release builds the caller must ensure validity). The bit position passed to BIT() is always in the range [0, 7] due to the & MASK(3) operation, so no invalid shift occurs on any platform.
Validation — The debug-only bounds check (index_of__bit >= size_of__bitmap) is appropriate for this low-level utility function. In release builds (NDEBUG defined), validation is omitted for performance, consistent with the pattern used by sibling functions such as set_bit_in__bitmap. This is an acceptable design choice; the caller is responsible for providing a valid index.

Side Effects:
No side effects — the function only reads from p_bitmap and returns a boolean. The bitmap array is not modified in any way.
