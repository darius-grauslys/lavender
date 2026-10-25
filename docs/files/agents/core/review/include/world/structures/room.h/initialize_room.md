initialize_room — core/include/world/structures/room.h (defined in .c), lines ?-?

Resets a Room struct to its initial (deallocated) state for pool reuse.

Pre-conditions:
1. p_room must be a non-null pointer to a writable Room object.
2. p_room points to a valid, allocated Room struct (typically from the Structure_Manager's rooms pool).
3. The Room struct must have Serialization_Header as its first member (which it does in defines.h).

Post-conditions:
1. p_room is zeroed out via memset, clearing all fields including:
   - _serialization_header (size_of__struct and uuid)
   - bounding_box_of__room (Hitbox_AABB)
   - entrances__3i32F4 array (ROOM_ENTRANCE_MAX_QUANTITY_OF entries)
   - the_type_of__room
   - quantity_of__room_entrances
   - room_flags
2. The serialization header is set to IDENTIFIER__UNKNOWN__u32 with size_of__struct = sizeof(Room), marking the room as deallocated/available for pool reuse.
3. The room is ready to be returned to a free pool or reused.

Correctness Verdict: Incorrect

Semantic Alignment:
This function follows the Lavender-specific semantics where "initialization" means cleaning up a struct to its initial conditions (pool cleanup / reset), NOT RAII-style resource acquisition. This is consistent with the pattern established by initialize_hitbox_aabb in core/source/collisions/core/aabb/hitbox_aabb.c, which performs the same memset + initialize_serialization_header_for__deallocated_struct pattern.

However, the function is DECLARED in room.h but has NO IMPLEMENTATION. There is no room.c file in core/source/world/ — the function is never defined. This means:
- Any call site referencing initialize_room will cause a linker error.
- The function's behavior is entirely undefined at runtime.
- The Structure_Manager (which maintains a pool of Room objects in rooms[ROOM_MAX_QUANTITY_OF]) cannot properly initialize or reset rooms without this implementation.

The expected implementation should follow the initialize_hitbox_aabb pattern:
```c
void initialize_room(Room *p_room) {
#ifndef NDEBUG
    if (!p_room) {
        debug_error("initialize_room, p_room == 0.");
        return;
    }
#endif
    memset(p_room, 0, sizeof(Room));
    initialize_serialization_header_for__deallocated_struct(
        &p_room->_serialization_header,
        sizeof(Room));
}
```

This would correctly:
- Validate the pointer in debug builds
- Zero all struct fields (including the embedded Hitbox_AABB bounding_box_of__room)
- Mark the serialization header as deallocated via IDENTIFIER__UNKNOWN__u32

Without this implementation, the function is non-functional.

Implementation Correctness:
Type compatibility: N/A — no implementation exists to verify.
Undefined behavior: N/A — no implementation exists to verify.
Validation: N/A — no implementation exists to verify.
Critical issue: The function is declared but never defined. No room.c file exists in core/source/world/. The function must be implemented (following the initialize_hitbox_aabb pattern) for the Room pool management system to function.

Side Effects:
Based on the expected implementation: Mutates p_room by zeroing all fields and setting the serialization header to a deallocated state. No other observable side effects. The function does not allocate or deallocate any resources (Lavender-style initialization, not RAII).
