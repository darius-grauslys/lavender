get_closest_entrance_to__room — core/include/world/structures/room.h (declared; implementation not found in any .c file)

Finds the entrance in the given Room that is closest (by Manhattan/hamming distance) to the provided position vector, returning that entrance's position. Returns VECTOR__3i32F4__OUT_OF_BOUNDS if the room has no entrances or on failure.

Pre-conditions:
1. p_room must be a non-null pointer to a valid, allocated Room struct.
2. position__3i32F4 is a Vector__3i32F4 representing the query position; any valid value is accepted (including out-of-bounds sentinel values, though semantically a real position is expected).

Post-conditions:
1. Returns a Vector__3i32F4 — the position of the closest entrance to position__3i32F4 among the room's entrances (p_room->entrances__3i32F4[0..quantity_of__room_entrances-1]).
2. Returns VECTOR__3i32F4__OUT_OF_BOUNDS if p_room->quantity_of__room_entrances is 0 (no entrances to compare).
3. The Room struct itself is not mutated; this is a read-only query.

Correctness Verdict: Incorrect

Semantic Alignment:
The function is declared but has NO implementation anywhere in the codebase (no room.c exists in core/source/). The header declares the function with the documentation comment "Returns VECTOR__3i32F4__OUT_OF_BOUNDS on failure," but no definition is provided. This means any caller of this function will encounter a linker error. The semantic intent — finding the closest entrance by distance — is clear from the name and documentation, but the implementation is entirely absent.

Implementation Correctness:
Since no implementation exists, there are no type compatibility, undefined behavior, or validation concerns to evaluate at the implementation level. However, the declaration itself is sound:
- Parameter types match the Room struct fields (Room * and Vector__3i32F4).
- Return type Vector__3i32F4 matches the type of entrances stored in the Room struct.
- The documented failure return value (VECTOR__3i32F4__OUT_OF_BOUNDS) is consistent with the type system and the is_vectors_3i32F4__out_of_bounds helper.

Side Effects:
No side effects — the function is a read-only query. It does not mutate the Room struct or any other state. (This is based on the declared signature and documentation; no implementation exists to verify.)