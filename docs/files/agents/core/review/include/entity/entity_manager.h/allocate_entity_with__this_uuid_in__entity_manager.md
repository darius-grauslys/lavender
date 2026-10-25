allocate_entity_with__this_uuid_in__entity_manager — core/source/entity/entity_manager.c, lines 113-160

Allocates a new entity within the entity_manager's fixed contiguous object pool, tagged with the caller-supplied UUID, run through the manager's f_entity_initializer callback, configured with the given kind, sanitized against the kind's registered function table, enabled, and appended to the live entity pointer array; returns nullptr (0) on failure.

Pre-conditions:
1. p_entity_manager must be a non-null pointer to an Entity_Manager that has been initialized via initialize_entity_manager (i.e., entities[] has been run through initialize_serialization_header__contiguous_array with sizeof(Entity), p_ptr_entity__next_in_ptr_array points within ptr_array_of__entities, and f_entity_initializer is set). The function itself guards the non-null / size_of__struct checks and returns 0 otherwise.
2. p_entity_manager->entities->_serialization_header.size_of__struct must be non-zero (true after initialize_entity_manager). Checked by the function.
3. kind_of_entity must be an in-range Entity_Kind value, i.e., 0 <= kind_of_entity < Entity_Kind__Unknown. sanitize_entity_functions indexes entity_functions[kind_of_entity] with no bounds guard, so an out-of-range kind is undefined behavior. This is the caller's responsibility (the sibling set_entity_functions validates this in debug builds, but sanitize_entity_functions does not).
4. p_game and p_world are forwarded to f_entity_initializer. They may be NULL when the registered initializer does not dereference them (the default initializer ignores them); for a custom initializer they must be valid per that initializer's contract. This is the caller's responsibility.
5. p_entity_manager->p_ptr_entity__next_in_ptr_array must point within ptr_array_of__entities such that there is room for one more entry; the function appends without a bounds check (kept in sync with allocation success by the manager's invariants).
6. uuid__u32 is any Identifier__u32. If it collides with an already-allocated entity, the underlying allocation primitive resolves the collision and the returned entity may carry a different (collision-resolved) UUID.

Post-conditions:
1. On failure (uninitialized manager, or no free slot in the entities pool), returns 0 (nullptr). No slot is consumed and p_ptr_entity__next_in_ptr_array is not advanced.
2. On success, returns a non-null Entity * that:
   a. has its _serialization_header marked allocated (uuid != IDENTIFIER__UNKNOWN__u32) and its uuid set to the resolved identifier;
   b. has entity_data.the_kind_of__entity == kind_of_entity (set after the initializer runs, so it overrides any initializer-set kind);
   c. has had f_entity_initializer applied — for the default initializer this zeroes entity_data/entity_functions beyond the serialization header and installs the dispose, serialize, and deserialize default handlers (Lavender-style initialization: resetting to initial conditions, NOT RAII resource acquisition);
   d. has had sanitize_entity_functions applied, copying any NULL function-pointer slots from the kind's registered entity_functions[kind] table;
   e. has the ENTITY_FLAG__IS_ENABLED bit set in entity_flags (via set_entity_as__enabled);
   f. is stored at *p_ptr_entity__next_in_ptr_array and the cursor is then incremented.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the documented semantic in the header comment ("Create a new entity instance within the entity_manager object pool. Return nullptr (0) if fails to get new entity."). It allocates from the contiguous pool, invokes the registered initializer (Lavender-style zero-and-set-default-handlers initialization, consistent with the engine's "initialization != RAII" convention), overwrites the kind, sanitizes functions, enables the entity, and appends it to the live pointer array. The two allocation failure paths (uninitialized manager, full pool) both return 0 before any mutation of the pointer array occurs.
The initializer is called before the kind is assigned so that the kind's function table (copied by sanitize_entity_functions) is applied last; this ordering is intentional and matches the documented intent. A "TODO: do better on this condition check" comment notes only that the readiness guard inspects the first entity slot's size_of__struct (which is sufficient since initialize_serialization_header__contiguous_array stamps every slot), not a correctness defect.

Implementation Correctness:
Type compatibility — every argument type matches its target exactly: entities[] is cast to Serialization_Header* (valid because Serialization_Header is the first member of Entity, so an Entity* is representable as a Serialization_Header* per C11 6.5.2.3), MAX_QUANTITY_OF__ENTITIES (128) converts to Quantity__u32/uint32_t without truncation, uuid__u32 (Identifier__u32) matches the Identifier__u32 parameter, and the (Entity*) result of allocate_serialization_header_with__this_uuid is a valid reinterpret of the Serialization_Header* (same initial-member aliasing). kind_of_entity (enum Entity_Kind) is assigned to the_kind_of__entity (Entity_Kind) exactly. The pointer-array append *p_ptr_entity__next_in_ptr_array = p_entity assigns Entity* to Entity* exactly.
Undefined behavior — no pointer arithmetic, no null dereference (p_entity is guaranteed non-null after the allocation-success check before being passed to the initializer, sanitize, set_entity_as__enabled, or the append), and no type punning beyond the permitted initial-member pointer aliasing. The only UB risk is an out-of-range kind_of_entity reaching sanitize_entity_functions' unbounded index into the fixed entity_functions[] table; this is the caller's responsibility rather than a defect of this function.
Validation — validation is appropriate to the function's role: it guards a non-null/initialized p_entity_manager and allocation success (caller-facing error returns with debug logging), consistent with Lavender's convention that low-level manager functions rely on callers for input validity. The kind range check is deliberately delegated (it is validated in debug builds by the sibling set_entity_functions), matching the project's established pattern.

Side Effects:
- Mutates the contiguous p_entity_manager->entities pool: the allocated slot has its _serialization_header initialized (uuid assigned, deallocated flag cleared to "allocated") via ALLOCATE_P.
- If f_entity_initializer is set, invokes it (Game*, World*, Entity*); the default initializer zeroes entity_data and entity_functions beyond the serialization header and installs the default dispose/serialize/deserialize handlers.
- Writes p_entity->entity_data.the_kind_of__entity = kind_of_entity.
- sanitize_entity_functions mutates p_entity->entity_functions in place, copying non-NULL function pointers from the registered entity_functions[kind] table into any NULL slots.
- set_entity_as__enabled sets the ENTITY_FLAG__IS_ENABLED bit in p_entity->entity_data.entity_flags.
- Appends p_entity to p_entity_manager->ptr_array_of__entities via *p_ptr_entity__next_in_ptr_array = p_entity and increments p_entity_manager->p_ptr_entity__next_in_ptr_array.
- On error paths, emits debug log messages via debug_error / debug_warning.
- Does not allocate heap memory (the pool is a fixed inline array) and does not modify p_game or p_world directly (they are only forwarded to the initializer, if any).
