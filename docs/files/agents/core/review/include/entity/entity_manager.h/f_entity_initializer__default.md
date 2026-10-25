f_entity_initializer__default — core/source/entity/entity_manager.c

Resets an allocated Entity to its initial conditions by zeroing all bytes after the Serialization_Header and installing default dispose/serialize/deserialize handlers.

Pre-conditions:
1. p_entity must be a non-null pointer to a valid, writable Entity object.
2. p_game and p_world may be NULL; they conform to the f_Entity_Initializer signature but are not dereferenced by this function.

Post-conditions:
1. The Serialization_Header (the first sizeof(Serialization_Header) bytes of Entity) is preserved unchanged.
2. entity_data and entity_functions are zeroed, so all Entity_Functions pointer slots are set to NULL.
3. entity_functions.m_entity_dispose_handler, m_entity_serialize_handler, and m_entity_deserialize_handler are assigned to their respective __default handlers.
4. entity_functions.m_entity_update_handler, m_entity_enable_handler, and m_entity_disable_handler remain NULL, to be populated later by sanitize_entity_functions() / initialize_entity().

Correctness Verdict: Correct

Semantic Alignment:
This is a Lavender-style initialization (reset to initial conditions / pool cleanup), NOT RAII — it does not acquire resources. It zeroes the entity body and installs the minimal set of base handlers, matching the intent documented in the source comment. Of the 6 fields in Entity_Functions, 3 are intentionally assigned (dispose, serialize, deserialize) and 3 are intentionally left NULL (update, enable, disable); no reordering occurs and assignments match the struct declaration order. The omitted handlers are completed later by sanitize_entity_functions(), which is by design.

Implementation Correctness:
Type compatibility — each __default handler function pointer is assigned to a field whose typedef exactly matches the function's signature (m_entity_dispose_handler__default -> m_Entity_Handler; m_entity_serialization_handler__default -> m_Entity_Serialization_Handler; m_entity_deserialization_handler__default -> m_Entity_Deserialization_Handler). No implicit conversions or truncation.
No undefined behavior — the memset destination ((u8*)p_entity + sizeof(Serialization_Header)) is within the Entity object, and the byte count (sizeof(Entity) - sizeof(Serialization_Header)) does not exceed the remaining bytes. No null dereference occurs because the callers guarantee a non-null p_entity. No broken pointer arithmetic or out-of-bounds access.
Validation — no validation is needed; this is a low-level initializer acting on a raw struct. The callers (allocate_entity_with__this_uuid_in__entity_manager and allocate_entity_in__entity_manager) verify p_entity is non-null before invoking the initializer, consistent with the codebase convention.

Side Effects:
Mutates the Entity pointed to by p_entity: zeroes entity_data and entity_functions, then sets three handler pointers. p_game and p_world are not dereferenced or otherwise observed.
