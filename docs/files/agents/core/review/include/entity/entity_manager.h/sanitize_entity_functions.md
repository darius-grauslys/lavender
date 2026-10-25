sanitize_entity_functions — core/source/entity/entity_manager.c

Copies non-NULL function pointers from the entity kind's registered Entity_Functions table (in the Entity_Manager) into the Entity's own entity_functions struct, leaving entity-level handlers untouched where the registered table has a NULL slot.

Pre-conditions:
1. p_entity_manager must be non-null. Not validated by this function; callers (allocate_entity_with__this_uuid_in__entity_manager at lines 146-148, allocate_entity_in__entity_manager at lines 190-192) check it upstream before invoking.
2. p_entity must be non-null. Not validated by this function; callers check allocation success before invoking.
3. p_entity->entity_data.the_kind_of__entity must be a valid index into p_entity_manager->entity_functions, i.e. < Entity_Kind__Unknown (entity_functions has Entity_Kind__Unknown slots). NOT validated by this function — a missing debug-bounds check; the inline set_entity_functions at entity_manager.h:84-90 performs this check but this function does not.
4. The Entity_Functions struct must consist solely of function-pointer members with size and alignment equal to void* and no internal padding. This holds for the struct layouts in this codebase (six function-pointer fields of uniform type and alignment).

Post-conditions:
1. For every pointer-sized slot where the kind's registered table entry is non-NULL, p_entity->entity_functions now holds that handler.
2. Slots with a NULL entry in the kind's table retain their prior value (e.g. the dispose/serialize/deserialize handlers installed by f_entity_initializer__default at entity_manager.c:27-40).
3. The kind's registered table (p_entity_manager->entity_functions[the_kind]) is read-only and is not modified.
4. p_entity->entity_data and p_entity->_serialization_header are not modified.

Correctness Verdict: Correct

The core algorithm is sound: it iterates over exactly sizeof(Entity_Functions) / sizeof(void*) pointer-sized slots (which equals the number of function-pointer fields, since the struct has no padding) and copies each non-NULL entry from the kind's table into the entity. The skip-on-NULL preserves entity-level defaults established by the initializer.

Semantic Alignment:
The implementation fulfills the semantic intent as documented in the header comment (entity_manager.h:24-27): "Ensure that the entity has the proper functions for it's type." The loop walks every slot of the registered kind's table and installs each non-NULL handler onto the entity, propagating the kind's registered handlers while leaving slots absent (NULL) from the table as-is. No field is omitted or reordered; because the function operates slot-by-slot via void** indexing rather than by named member, the physical field order is irrelevant, so it is agnostic to the differing field orders between the default and extended Entity_Functions definitions.

Implementation Correctness:
- Type compatibility: The struct is cast to void** and each slot is read/written as a void*. All Entity_Functions members are function pointers; on the target platforms all function-pointer types share the same size as void* (no implicit truncation). The mixed m_Entity_Handler, m_Entity_Serialization_Handler, and m_Entity_Deserialization_Handler types are all function pointers of void* width, so the uniform void* treatment is safe on these platforms.
- Undefined behavior: The array access entity_functions[the_kind_of__entity] has no bounds check; an out-of-range kind would read out of bounds (UB). This is a validation gap — the inline set_entity_functions validates the kind in debug builds, but sanitize_entity_functions does not. The void** indexing is a common C aliasing idiom; void* may alias any pointer type, so this is safe in practice though it relies on implementation-defined behavior (function pointers being void*-sized and the struct having no padding). The struct contains only function-pointer members with uniform alignment, so no padding is present and sizeof(Entity_Functions) / sizeof(void*) correctly yields the slot count.
- Validation: No validation of p_entity_manager, p_entity, or the the_kind_of__entity bounds is performed within this function. This is inconsistent with register_entity_into__entity_manager (entity_manager.c:73-81) and the inline set_entity_functions (entity_manager.h:84-90), which both debug-check the kind bounds. In the current call sites p_entity_manager is validated upstream and the entity kind is caller-supplied and assumed valid, so the function is correct within its operational envelope — but the missing bounds check is a robustness gap.

Side Effects:
Mutates p_entity->entity_functions in place — for each slot where the kind's registered table has a non-NULL handler, the corresponding slot is overwritten with that handler; slots with a NULL kind-table entry are left unchanged. No other state is touched: the kind's registered table, p_entity->entity_data, and p_entity->_serialization_header are all read-only. No allocation, global/state mutation, or I/O occurs.
