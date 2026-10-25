set_room_as__allocated — core/include/world/structures/room.h

Sets the IS_ALLOCATED bit flag on a Room's room_flags field.

Pre-conditions:
1. p_room must be a non-null pointer to a writable Room object.
2. p_room->room_flags must be a valid Room_Flags__u8 value (uint8_t).

Post-conditions:
1. p_room->room_flags has the ROOM_FLAG__IS_ALLOCATED bit (BIT(0)) set to 1.
2. All other bits in p_room->room_flags remain unchanged.
3. The function returns void; no return value.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly sets the ROOM_FLAG__IS_ALLOCATED bit in the room_flags field of the Room struct. The bit-flag manipulation (p_room->room_flags |= ROOM_FLAG__IS_ALLOCATED) is the standard and correct way to set a single bit in a flags field. This matches the semantic intent of marking a room as allocated. The companion function set_room_as__deallocated uses the inverse operation (p_room->room_flags &= ~ROOM_FLAG__IS_ALLOCATED), confirming the intended pattern. This is not an RAII-style initialization — it is a Lavender-style flag-setting operation that marks a room as allocated within a pool, consistent with the engine's pool-based resource management.

Implementation Correctness:
Type compatibility — p_room is a Room* and room_flags is a Room_Flags__u8 (uint8_t); ROOM_FLAG__IS_ALLOCATED is defined as BIT(0), which is ((1U) << 0) = 1, a value compatible with uint8_t. No implicit conversions or truncation occur.
No undefined behavior — no pointer arithmetic, no null dereference (the function dereferences p_room but the caller is responsible for ensuring it is non-null, consistent with all inline accessors in this header), no type punning, no out-of-bounds access.
No validation is needed — this is a low-level inline flag setter. The caller is responsible for ensuring p_room is valid, which is consistent with the codebase pattern for all inline Room accessors.

Side Effects:
Mutates p_room->room_flags by setting the ROOM_FLAG__IS_ALLOCATED bit. No other memory or I/O side effects.
