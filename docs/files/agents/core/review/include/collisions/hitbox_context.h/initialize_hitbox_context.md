initialize_hitbox_context — core/source/collisions/hitbox_context.c

Lavender-style initialization (pool reset/cleanup), not RAII. Cleans the hitbox_manager_instances array to a deallocated state and then registers all built-in hitbox manager types.

Pre-conditions:
1. p_hitbox_context must be a non-null pointer to a writable Hitbox_Context.
2. The hitbox_manager_instances array (MAX_QUANTITY_OF__HITBOX_MANAGERS entries) must be accessible for writing.
3. All registration records and invocation tables must be zeroed or cleared so that register_hitbox_managers can populate them cleanly.

Post-conditions:
1. Every entry in hitbox_manager_instances has its _serialization_header.uuid set to IDENTIFIER__UNKNOWN__u32 (deallocated state).
2. All hitbox manager types are registered in the invocation table and registration records via register_hitbox_managers.

Correctness Verdict: Correct

Semantic Alignment: The function correctly performs pool cleanup by initializing the contiguous array of Hitbox_Manager_Instance structs to a deallocated state, then delegates to register_hitbox_managers to populate type-specific allocation/deallocation/property-access function pointers. The semantic intent of "initialization" in Lavender (resetting to initial conditions for pool reuse) is fulfilled — this is not resource acquisition (RAII).

Implementation Correctness:
Type compatibility — the cast from Hitbox_Manager_Instance[] to Serialization_Header* is valid because _serialization_header is the first member of Hitbox_Manager_Instance. MAX_QUANTITY_OF__HITBOX_MANAGERS and sizeof(Hitbox_Manager_Instance) are passed correctly.
Undefined behavior — none. The cast is standard-layout compatible. initialize_serialization_header__contiguous_array writes to each element.
Validation — no validation is needed; this is a low-level initialization function. The caller must ensure p_hitbox_context is valid.

Side Effects:
Mutates every entry in p_hitbox_context->hitbox_manager_instances (sets uuid to IDENTIFIER__UNKNOWN__u32). Mutates p_hitbox_context->hitbox_manager_instance__invocation_table and p_hitbox_context->hitbox_manager_registration_records via register_hitbox_managers.
