add_entrance_to__room — core/include/world/structures/room.h (defined in .c), lines ?-?

Adds a positional entrance to a Room struct.

Pre-conditions:
1. p_room must be a non-null pointer to a writable Room object.
2. position__3i32F4 is any valid Vector__3i32F4; no range constraint is specified.
3. The Room must have been previously initialized (e.g., via initialize_room) so that quantity_of__room_entrances and entrances__3i32F4 are in a known state.
4. quantity_of__room_entrances must be less than ROOM_ENTRANCE_MAX_QUANTITY_OF (4) to avoid overflow; the function should handle this gracefully.

Post-conditions:
1. If quantity_of__room_entrances < ROOM_ENTRANCE_MAX_QUANTITY_OF, position__3i32F4 is stored in entrances__3i32F4[quantity_of__room_entrances] and quantity_of__room_entrances is incremented by 1.
2. If quantity_of__room_entrances >= ROOM_ENTRANCE_MAX_QUANTITY_OF, the entrance is not added and quantity_of__room_entrances remains unchanged (no-op).
3. p_room is mutated; no other objects are affected.

Correctness Verdict: Cannot be determined — no implementation found.

Semantic Alignment:
The function's intent, based on its name and the Room struct definition, is to append a new entrance position to the room's entrances array. The Room struct contains:
- entrances__3i32F4[ROOM_ENTRANCE_MAX_QUANTITY_OF] — a fixed-size array of Vector__3i32F4 with capacity 4.
- quantity_of__room_entrances — a Quantity__u8 tracking the number of currently stored entrances.

The expected implementation should write position__3i32F4 to entrances__3i32F4[quantity_of__room_entrances] and then increment quantity_of__room_entrances, provided the count has not exceeded ROOM_ENTRANCE_MAX_QUANTITY_OF.

However, no implementation of this function exists in any .c file within the codebase. The function is declared in core/include/world/structures/room.h but has no corresponding definition. This means the function cannot be compiled and linked — any call to it would result in a linker error. The same is true for initialize_room and get_closest_entrance_to__room, which are also declared but unimplemented.

Implementation Correctness:
No implementation exists to evaluate. If implemented as described above, the function would need to:
- Check for null p_room (or leave validation to the caller, consistent with the codebase pattern where inline helpers do not validate).
- Check bounds: if quantity_of__room_entrances >= ROOM_ENTRANCE_MAX_QUANTITY_OF, do not write (to avoid out-of-bounds access).
- Assign position__3i32F4 to entrances__3i32F4[quantity_of__room_entrances].
- Increment quantity_of__room_entrances.

Type compatibility: The parameter type Vector__3i32F4 matches the array element type Vector__3i32F4 exactly. No implicit conversions or truncation would occur.

Undefined behavior: A naive implementation without bounds checking would cause an out-of-bounds write when quantity_of__room_entrances reaches ROOM_ENTRANCE_MAX_QUANTITY_OF. This is a potential bug that the implementation must guard against.

Side Effects:
Mutates p_room: writes to entrances__3i32F4 array and increments quantity_of__room_entrances. No other observable side effects.
