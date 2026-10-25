is_room__allocated — core/include/world/structures/room.h

Checks whether the given Room's "is allocated" flag is set, indicating the room is currently allocated/in use.

Pre-conditions:
1. p_room must be a non-null pointer to a valid, initialized Room struct.
2. p_room->room_flags must contain meaningful flag state (i.e., the Room has been initialized via initialize_room or equivalent).

Post-conditions:
1. Returns `true` if the ROOM_FLAG__IS_ALLOCATED bit (BIT(0)) is set in p_room->room_flags.
2. Returns `false` if the ROOM_FLAG__IS_ALLOCATED bit is not set.
3. No mutation occurs; the Room struct is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to query the allocation state of a Room by checking a specific bit flag. The implementation correctly performs a bitwise AND between p_room->room_flags (of type Room_Flags__u8, i.e., uint8_t) and ROOM_FLAG__IS_ALLOCATED (defined as BIT(0), i.e., 1U). The result is implicitly converted to bool — zero becomes false, non-zero becomes true. Since only BIT(0) is checked, the result is either 0 or 1, making the conversion well-defined and correct. The function does not mutate any state, which aligns with its read-only query intent.

Implementation Correctness:
Type compatibility — p_room is of type Room * and room_flags is a member of Room, so the access is correct. ROOM_FLAG__IS_ALLOCATED is an unsigned int macro (1U), and room_flags is uint8_t; the bitwise AND promotes uint8_t to unsigned int, which is well-defined. The return type is bool, and the implicit integer-to-bool conversion is standard and correct for this use case.
Undefined behavior — none. No pointer arithmetic, no null dereference (pre-condition requires non-null p_room), no type punning, no out-of-bounds access.
Validation — no validation is needed within this function. It is a low-level inline query function; ensuring p_room is non-null is the caller's responsibility, consistent with the pattern used by other inline accessors in this header (e.g., get_width_of__room, get_height_of__room).

Side Effects:
No side effects. The function is a pure read-only query — it reads p_room->room_flags and returns a bool without modifying any state.
