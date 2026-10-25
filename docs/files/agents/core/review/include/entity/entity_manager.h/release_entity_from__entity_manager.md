release_entity_from__entity_manager — core/source/entity/entity_manager.c, lines 206-243

Disposes a live entity, resets it to deallocated/initial conditions (Lavender-style initialization, not RAII), and removes it from the manager's live pointer array via swap-with-tail removal.

Pre-conditions:
1. p_entity must be a non-null pointer to a live Entity currently registered in p_entity_manager (its pointer must appear in ptr_array_of__entities).
2. p_entity_manager must be a non-null pointer to a valid Entity_Manager.
3. p_game and p_world may be NULL only when the entity's m_entity_dispose_handler tolerates null arguments; the function itself never dereferences them directly — this follows the low-level internal API convention where validation is the caller's responsibility.
4. p_entity_manager->p_ptr_entity__next_in_ptr_array must point one past the last live entry and must satisfy > ptr_array_of__entities (guaranteed when p_entity is a registered live entry, so the decrement-and-dereference below is in bounds).
5. The entity must currently be allocated (live) in the manager; behavior is undefined if it was never registered.

Post-conditions:
1. If p_entity had a non-null m_entity_dispose_handler, it has been invoked with (p_entity, p_game, p_world) while the entity was still live (before reset).
2. p_entity has been "initialized" Lavender-style: zeroed via memset, with default dispose/enable/disable handlers assigned and Entity_Kind__None as its kind.
3. p_entity->_serialization_header is marked deallocated via initialize_serialization_header_for__deallocated_struct(sizeof(Entity)).
4. p_entity has been removed from ptr_array_of__entities: the slot that held it now holds the previous last live entry pointer, that previous last slot is zeroed (0), and p_ptr_entity__next_in_ptr_array has been decremented by one.
5. For any external observer, indices into ptr_array_of__entities are no longer stable for any slot after this call.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It correctly (a) calls the entity's dispose handler first, while the entity is still live, (b) resets the entity via Lavender-style initialization (pool cleanup, NOT RAII), (c) marks the serialization header as deallocated, and (d) removes the entity from the live pointer array with swap-with-tail removal. The reset is appropriate: initialize_entity is called with Entity_Kind__None, matching the intent to clear the entity back to initial conditions, and the resulting deallocated header correctly reflects that the entry is free. Note: the Entity_Kind argument is not actually consumed by initialize_entity (it memsets the struct regardless), but passing Entity_Kind__None is still semantically correct for a release.

Implementation Correctness:
- Type compatibility: all argument types match their targets exactly. m_entity_dispose_handler is m_Entity_Handler = void(*)(Entity*, Game*, World*) and is invoked with (Entity*, Game*, World*) with no implicit conversion. initialize_entity expects (Entity*, enum Entity_Kind) and is called with (p_entity, Entity_Kind__None). initialize_serialization_header_for__deallocated_struct expects (Serialization_Header*, size_t) and is called with (&p_entity->_serialization_header, sizeof(Entity)) — sizeof yields size_t, exact match. The pointer-array writes assign Entity* to Entity* slots, and the null-clear writes Entity* = 0 (valid null pointer constant). The loop counter Index__u32 is compared against MAX_QUANTITY_OF__ENTITIES consistently with the rest of the file.
- Undefined behavior: none. The swap-with-tail sequence decrements p_ptr_entity__next_in_ptr_array (an Entity**) and dereferences only that one past-the-end slot; because p_entity is a registered live entry, the array has at least one live entry, so the decremented pointer is a valid in-bounds slot. The loop bounds (0 .. MAX_QUANTITY_OF__ENTITIES) match the ptr_array_of__entities array dimension exactly, so no out-of-bounds access occurs. No null dereference of the manager, no type punning, no broken pointer arithmetic. The function does not itself check for NULL p_entity/p_entity_manager; this is the documented caller responsibility for this low-level internal API (consistent with get_p_entity_by__index_from__entity_manager, which likewise validates only in debug builds).
- Validation: appropriate for the function's role. It performs no redundant validation, delegating validity to the caller — consistent with the rest of the entity_manager internal API.

Side Effects:
Mutating; three observable effects:
1. Invokes p_entity's m_entity_dispose_handler (when non-null) with (p_entity, p_game, p_world), whose own behavior is an observable side effect of that handler.
2. Mutates p_entity: zeroed and reset to default/initial conditions by initialize_entity (Lavender-style reset), and its serialization header marked deallocated.
3. Mutates p_entity_manager: removes p_entity from ptr_array_of__entities by swap-with-tail — the freed slot receives the previous last live entry pointer, the previous last slot is set to 0, and p_ptr_entity__next_in_ptr_array is decremented.
