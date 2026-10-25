set_bit_in__bitmap_and_heap — core/source/util/bitmap/bitmap.c

Sets or clears a single bit in a hierarchical bitmap-and-heap data structure. The bitmap portion stores one bit per slot; the heap portion is a multi-level summary where each byte in level _k_ summarizes 8 bytes in level _k-1_ (a bit in the heap is set if any of the corresponding 8 bytes/bits below are non-zero). The function writes the bit into the bitmap portion and then propagates the change upward through the heap levels.

Pre-conditions:
1. p_bitmap must be a non-null pointer to the first byte of a contiguous bitmap-and-heap buffer (allocated via the BITMAP_AND_HEAP macro).
2. p_end_of__heap must point to the last byte of the same buffer (i.e., &p_bitmap[total_size - 1]).
3. size_of__bitmap_but_NOT__including_heap is the size of the bitmap portion in BYTES (not bits). It must be a multiple of 8 so that heap level boundaries are byte-aligned.
4. index_of__bit must be a valid bit index into the bitmap portion: 0 <= index_of__bit < (size_of__bitmap_but_NOT__including_heap * 8). The debug check only verifies index_of__bit < size_of__bitmap_but_NOT__including_heap (too permissive — it compares a bit index against a byte count; consistent with is_bit_set_in__bitmap and set_bit_in__bitmap, but technically incorrect).
5. state_of__bit is a bool: true sets the bit, false clears it.

Post-conditions:
1. The bitmap byte at p_bitmap[index_of__bit >> 3] is updated so that bit (index_of__bit & 7) reflects state_of__bit.
2. The corresponding bits in each heap level are updated to reflect whether the summarized group now contains at least one set bit.
3. p_end_of__heap and p_bitmap are not otherwise modified.
4. The function returns void.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation does NOT fulfill its semantic intent. The function is supposed to set a bit in the bitmap and then propagate the change through the hierarchical heap summary. However, the heap-level write/read operations are fundamentally broken:

1. **Wrong write target (heap level 1 and all propagated levels):** The code writes to p_end_of__heap[-index_of__heap_modification], which accesses a byte at offset (total_size - 1 - index_of__heap_modification) from the start of the array. But the heap is laid out forward (bitmap first, then heap level 1, level 2, …), as confirmed by get_index_of__first_set_bit_from__bitmap_and_heap which accesses the heap via p_heap = &p_bitmap_and_heap[size_of__bitmap_but_NOT__including_heap]. The correct heap byte is at p_bitmap[index_of__heap_modification] (offset from the start), not at p_end_of__heap[-index_of__heap_modification] (offset from the end). These are different memory locations in general.

2. **Wrong read source (heap level 1 and all propagated levels):** The code reads from p_bitmap[index_of__heap_modification >> 3], which divides the byte offset by 8, landing in a completely different region of the array. The read-modify-write must read from the same location it writes to.

3. **Wrong bit position (heap level 1 and all propagated levels):** The code uses index_of__heap_modification & MASK(3) as the bit position within the heap byte. Since index_of__heap_modification = (index_of__bit >> 6) + size_of__bitmap_but_NOT__including_heap, and size_of__bitmap_but_NOT__including_heap is a multiple of 8, this evaluates to (index_of__bit >> 6) & 7 — i.e., bits 6–8 of index_of__bit. The correct bit position is (index_of__bit >> 3) & MASK(3) — bits 3–5 — which identifies which of the 8 bitmap bytes (within the 64-bit group covered by this heap byte) was modified.

4. **Wrong next-level index computation:** index__next = index_of__heap_modification + (index_of__heap_modification >> 3) does not correctly compute the byte offset of the corresponding byte in the next heap level. It adds the current offset divided by 8 to the current offset, which produces an incorrect address that does not correspond to any meaningful position in the hierarchical structure.

5. **Incorrect propagation break condition:** The condition (p_end_of__heap[-index__next] > 0) && (p_end_of__heap[-index_of__heap_modification]) checks whether both the next-level and current-level bytes are non-zero. This does not correctly determine when propagation should stop. The correct logic should detect whether the current level byte transitioned state (e.g., from 0 to non-zero when setting a bit, indicating the parent bit needs to be set, or from non-zero to 0 when clearing a bit).

Implementation Correctness:
- Type compatibility: Parameter types match the function signature. Index__u32 is used for index_of__heap_modification and index__next, which is compatible. No truncation issues.
- Undefined behavior: The wrong write target (p_end_of__heap[-index_of__heap_modification]) can access memory before the start of the buffer when index_of__heap_modification is large, causing undefined behavior. The wrong read source (p_bitmap[index_of__heap_modification >> 3]) can also access out-of-bounds memory. The wrong bit position can set/clear the wrong bit in the heap, corrupting the summary structure.
- Validation: The debug bounds check is too permissive (compares bit index against byte count), but this is consistent with the codebase pattern. The real issue is the incorrect heap manipulation logic.

Side Effects:
The function mutates the buffer pointed to by p_bitmap (the bitmap portion and the intended heap portion). Due to the bugs, it writes to incorrect memory locations, potentially corrupting the bitmap, the heap, or memory outside the buffer. When called via the SET_BIT_IN__BITMAP_AND_HEAP macro, p_end_of__heap is &bitmap[sizeof(bitmap)-1], so the backward indexing p_end_of__heap[-n] can write to any byte in the buffer, including the bitmap portion itself, causing data corruption.
