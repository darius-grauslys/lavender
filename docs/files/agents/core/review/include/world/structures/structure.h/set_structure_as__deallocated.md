set_structure_as__deallocated — core/include/world/structures/structure.h, lines 64-70

Clears the STRUCTURE_FLAG__IS_ALLOCATED bit in the Structure's structure_flags, marking the Structure as deallocated.

Pre-conditions:
1. p_structure must be a non-null pointer to a valid, writable Structure object.
2. p_structure->structure_flags is any Structure_Flags__u8 value (no range constraint needed).

Post-conditions:
1. The STRUCTURE_FLAG__IS_ALLOCATED bit (BIT(0)) in p_structure->structure_flags is cleared; all other flag bits are preserved.
2. is_structure__allocated(p_structure) will return false after this call.

Correctness Verdict: Correct

Semantic Alignment:
The function's name and implementation are semantically aligned. It clears the allocation flag, which is the inverse of set_structure_as__allocated (which sets the same flag via |=). The bit-clearing idiom (flags &= ~BIT) is the standard and correct way to clear a single bit. This is consistent with the analogous set_room_as__deallocated function in room.h, which uses the same pattern with ROOM_FLAG__IS_ALLOCATED.

Lavender-specific semantics: This function is NOT an initialization/RAII function. It does not clean up or reset struct fields to initial conditions. It simply clears an allocation-tracking flag, which is consistent with Lavender's non-RAII approach where "initialization" refers to pool cleanup, not resource acquisition. Marking a structure as deallocated is a flag-clearing operation, not a resource release.

Implementation Correctness:
Type compatibility — structure_flags is Structure_Flags__u8 (uint8_t), and STRUCTURE_FLAG__IS_ALLOCATED is BIT(0) = (1U) << 0 = 1 (unsigned int). The expression ~STRUCTURE_FLAG__IS_ALLOCATED yields 0xFFFFFFFE (unsigned int). The compound assignment &= performs the bitwise AND and assigns back to the uint8_t field, with the result properly truncated to 8 bits. This is well-defined behavior in C; no implicit conversion issues or truncation concerns.
No undefined behavior — no pointer arithmetic, no null dereference (caller must provide valid pointer), no type punning, no out-of-bounds access. The only memory access is a single write to p_structure->structure_flags.
No validation is needed — this is a low-level inline flag manipulation. The caller is responsible for ensuring p_structure is a valid, non-null pointer. This matches the pattern used by all sibling flag functions in the codebase (set_structure_as__allocated, set_room_as__allocated, etc.).

Side Effects:
Mutates p_structure->structure_flags by clearing the STRUCTURE_FLAG__IS_ALLOCATED bit. No other fields are modified. No observable side effects beyond this single field write.
