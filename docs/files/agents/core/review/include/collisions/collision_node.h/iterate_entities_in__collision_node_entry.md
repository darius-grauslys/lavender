iterate_entities_in__collision_node_entry — core/source/collisions/collision_node.c, lines 196-229

Iterator that walks a collision node's singly-linked list of entries (tail to head via p_previous_entry), resolving each entry's stored hitbox UUID into the corresponding Entity through the Entity_Manager. On each call the cursor pointer (*p_ptr_collision_node__entry) is advanced to the next entry and the resolved Entity is written out through both *p_ptr_entity and the return value. Returns 0 when the cursor is null (end of iteration) or when the looked-up Entity is null. The sole call site (global_space.c:396) uses the return value as the while-loop condition.

Pre-conditions:
1. p_ptr_entity must be a non-null pointer to a writable Entity * location (debug-only check in NDEBUG builds).
2. p_entity_manager must be a non-null, initialized Entity_Manager (debug-only check in NDEBUG builds).
3. p_ptr_collision_node__entry must be a non-null pointer to a valid Collision_Node_Entry * cursor — this is NOT checked, even in debug builds; a null value would be dereferenced on line 211 and cause undefined behavior.
4. *p_ptr_collision_node__entry may be null, signalling end of iteration.

Post-conditions:
1. *p_ptr_collision_node__entry is advanced to p_collision_node_entry->p_previous_entry (or left unchanged-if-null when the cursor was already null, since the early return on line 213 prevents the assignment on line 223).
2. *p_ptr_entity is set to the Entity resolved from the current entry's uuid_of__hitbox__u32 via get_p_entity_by__uuid_from__entity_manager, or to 0 if the cursor was null or the entity was not found.
3. The return value equals *p_ptr_entity (both hold the resolved Entity * or 0).

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully realizes the iterator intent: it reads the current entry from the cursor, resolves the entity by UUID, advances the cursor to the previous entry, and exposes the result through both the output pointer and the return value. This matches the singly-linked-list walk pattern used by the sibling function iterate_collision_node__entry (collision_node.h:47) and by get_quantity_of__entries_in__collision_node (collision_node.c:132). No semantic drift is present.

However, there is an important API-design concern: the return value serves a dual purpose — it is both the resolved Entity output and the implicit "has more entries?" signal. Because get_p_entity_by__uuid_from__entity_manager (entity_manager.h:71) can return 0 when no entity exists for a given hitbox UUID, a single unresolvable entry causes the caller's while-loop (global_space.c:396) to terminate, silently skipping all subsequent entries. The function advances *p_ptr_collision_node__entry before returning, but the caller never gets a chance to observe the advanced cursor because the loop exits. This is not a bug in the function's own logic, but it is a subtle contract hazard that should be documented or addressed by splitting the "end of iteration" sentinel from the "entity not found" case.

Implementation Correctness:
Type compatibility — all parameter and local variable types match their targets exactly. Identifier__u32 (uint32_t) is passed to get_p_entity_by__uuid_from__entity_manager which expects Identifier__u32. Entity * and Collision_Node_Entry ** are used consistently. No implicit conversions or truncation.

Undefined behavior — no broken pointer arithmetic, no type punning, no out-of-bounds access. The cast inside get_p_entity_by__uuid_from__entity_manager ((Entity*)dehash_identitier_u32_in__contigious_array(...)) is an intentional overlay that relies on Entity beginning with a Serialization_Header (defines.h:1131), which is a valid design assumption in this engine.

Validation — null checks for p_ptr_entity and p_entity_manager are present but guarded by #ifndef NDEBUG, meaning they are absent in release builds. More critically, p_ptr_collision_node__entry is never checked for null despite being dereferenced unconditionally on line 211. In the current call site this parameter is always the address of a local variable (&p_collision_node_entry at global_space.c:398), so the risk is theoretical, but the omission is inconsistent with the checks applied to the other two pointer parameters and should be fixed by adding a null check (or at least a debug assert) consistent with the existing pattern.

Side Effects:
Mutates *p_ptr_collision_node__entry (advances the cursor to the previous linked-list entry) and *p_ptr_entity (writes the resolved Entity * or 0). No other externally observable side effects; the function does not modify the Collision_Node_Entry, the Entity_Manager, or any Entity data.
