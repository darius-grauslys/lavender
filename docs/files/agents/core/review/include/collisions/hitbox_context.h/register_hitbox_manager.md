register_hitbox_manager — core/source/collisions/hitbox_context.c

Registers a hitbox manager type by storing its allocator, deallocator, and opaque property-access function pointers in the context's invocation table, and stashing component metadata in the registration record.

Pre-conditions:
1. p_hitbox_context must be a non-null pointer to a writable Hitbox_Context.
2. All function pointer parameters (f_hitbox_manager__allocator, f_hitbox_manager__deallocator, f_hitbox_manager__get_properties_of__hitbox) must be valid function pointers (non-null). The function does not validate this — null pointers are stored as-is.
3. the_type_of__hitbox_manager_to__register must be a valid Hitbox_Manager_Type value strictly less than Hitbox_Manager_Type__Unknown (validated in debug builds only).
4. All u8 component parameters (quantities, sizes, fractional precisions) may be any value in the u8 range; no range constraints are enforced.

Post-conditions:
1. hitbox_manager_registration_records[the_type] is populated with component metadata (sizes, quantities, fractional precisions).
2. hitbox_manager_instance__invocation_table[the_type] is populated with the three function pointers (allocator, deallocator, property accessor).

Correctness Verdict: Correct

Semantic Alignment: The function correctly stores all registration data in the appropriate arrays. No fields in either the registration record or invocation table are omitted — all 7 registration-record fields and all 3 invocation-table function pointers are assigned.

Implementation Correctness:
Type compatibility — every parameter type matches its target field type exactly. f_Hitbox_Manager__Allocator, f_Hitbox_Manager__Deallocator, and f_Hitbox_Manager__Opaque_Property_Access_Of__Hitbox function pointers are stored in identically-typed struct fields. u8 parameters are stored in u8 fields. Hitbox_Manager_Type is used as an array index, which is standard.
Undefined behavior — the debug-only bounds check prevents out-of-bounds array access in debug builds. In release builds (NDEBUG), if the_type is invalid (>= Hitbox_Manager_Type__Unknown), an out-of-bounds write would occur. This is acceptable because the function is internal and callers are expected to pass valid types; the debug guard serves as a programmer-error catch.
Validation — debug-only type validation is appropriate for an internal registration function. No null checks on function pointers are performed; this is the caller's responsibility.

Side Effects:
Mutates p_hitbox_context->hitbox_manager_registration_records[the_type]. Mutates p_hitbox_context->hitbox_manager_instance__invocation_table[the_type].
