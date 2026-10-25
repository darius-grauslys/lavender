set_room_as__deallocated — core/include/world/structures/room.h, lines 70-74

Clears the ROOM_FLAG__IS_ALLOCATED bit from the room's flags, marking the room as deallocated.

Pre-conditions:
1. p_room must be a non-null pointer to a writable Room object.

Post-conditions:
1. p_room->room_flags has the ROOM_FLAG__IS_ALLOCATED bit cleared (set to 0). All other bits remain unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The function performs a bitwise AND with the complement of ROOM_FLAG__IS_ALLOCATED, which is the standard idiom for clearing a single flag bit. This fulfills the semantic intent of marking the room as deallocated. The operation is consistent with the companion function set_room_as__allocated, which sets the same bit. This is Lavender-style initialization (pool cleanup / state reset), not RAII — the function does not release any resources, it only clears a flag indicating the room is no longer in use.

Implementation Correctness:
Type compatibility — p_room is Room *, and room_flags is Room_Flags__u8 (uint8_t). ROOM_FLAG__IS_ALLOCATED is defined as BIT(0), which is 1, an integer literal compatible with uint8_t arithmetic. The ~ operator on a uint8_t promotes the operand to int, but the result is implicitly converted back to uint8_t when assigned, which is well-defined for flag manipulation. No truncation or implicit conversion concerns.
No undefined behavior — no pointer arithmetic, no null dereference (caller must ensure non-null), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level flag manipulation. The caller is responsible for ensuring p_room is valid.

Side Effects:
Mutates p_room->room_flags by clearing the ROOM_FLAG__IS_ALLOCATED bit. No other side effects.
