initialize_hitbox_manager_instance_as__deallocated — core/source/collisions/hitbox_manager_instance.c

Resets a Hitbox_Manager_Instance to a deallocated, pool-returnable state (Lavender-style initialization, not RAII).

Pre-conditions:
1. p_hitbox_manager_instance must be a non-null pointer to a writable Hitbox_Manager_Instance object.

Post-conditions:
1. All bytes of the struct are zeroed via memset (pVM_hitbox_manager set to NULL, type_of__hitbox_manager set to 0).
2. _serialization_header.uuid is set to IDENTIFIER__UNKNOWN__u32 (0xFFFFFFFF), marking the struct as deallocated.
3. _serialization_header.size_of__struct is set to sizeof(Hitbox_Manager_Instance).

Correctness Verdict: Correct

Semantic Alignment:
This is Lavender-style initialization (pool cleanup, not RAII). The memset zeroes all fields, and the serialization header is explicitly set to the deallocated marker (IDENTIFIER__UNKNOWN__u32). All struct fields end up in a known default state. The function correctly distinguishes from initialize_hitbox_manager_instance_as__allocated by leaving the uuid as IDENTIFIER__UNKNOWN__u32 so is_p_hitbox_manager_instance__valid returns false.

Implementation Correctness:
Type compatibility — sizeof(Hitbox_Manager_Instance) (size_t, 64-bit) is implicitly narrowed to Quantity__u32 (uint32_t). For this small struct the value is well within uint32 range, so no truncation occurs in practice; this is a codebase-wide convention.
No undefined behavior — memset on a valid pointer is safe; initialize_serialization_header_for__deallocated_struct receives a valid pointer to the header field; no null dereference, no out-of-bounds access, no type punning.
No validation is needed — this is a low-level initialization function; the caller is responsible for ensuring p_hitbox_manager_instance is valid.

Side Effects:
Mutates the Hitbox_Manager_Instance struct in-place: zeroes all bytes via memset, then overwrites _serialization_header.uuid to IDENTIFIER__UNKNOWN__u32 and _serialization_header.size_of__struct to sizeof(Hitbox_Manager_Instance).
