m_entity_enable_handler__default — core/source/entity/entity.c

Enables an entity by activating its associated Hitbox_AABB in the game's hitbox context. (NOTE: the function name and its unit test expect the `ENTITY_FLAG__IS_ENABLED` flag to be set on the entity, but the implementation does not — see Semantic Alignment.)

Pre-conditions:
1. p_this_entity must be a non-null pointer to a valid, initialized Entity.
2. p_game must be a non-null pointer to a Game whose hitbox_context is initialized.
3. p_world must be a non-null pointer to a World whose Serialization_Header.uuid is valid.
4. The hitbox context in p_game must have a hitbox manager allocated for the UUID of p_world.
5. The hitbox AABB manager for p_world must contain a Hitbox_AABB entry for p_this_entity.
6. CRITICAL: The function dereferences p_game unconditionally via get_p_hitbox_context_from__game(p_game) (expanded as &p_game->hitbox_context) and dereferences p_world unconditionally via GET_UUID_P(p_world) (expanded as ((Serialization_Header*)p_world)->uuid). Passing NULL for either is undefined behavior. The unit test does exactly this — see Post-conditions.

Post-conditions:
1. If a Hitbox_AABB is found for p_this_entity in the manager, set_hitbox_aabb_as__active is called on it, setting the hitbox's active flag.
2. The ENTITY_FLAG__IS_ENABLED flag on p_this_entity->entity_data.entity_flags is NOT set. This is a bug — the unit test expects it to be set.
3. In debug builds (NDEBUG undefined), if get_pV_hitbox_manager_from__hitbox_context returns NULL, debug_error is called and the function returns early.
4. In release builds (NDEBUG defined), the null check is compiled out; if the manager lookup fails (returning an invalid Hitbox_Manager_Instance with a possibly null pVM_hitbox_manager), the code proceeds to dereference it — undefined behavior.
5. In debug builds, if p_hitbox_aabb is NULL, no hitbox mutation occurs.
6. The function returns void.
7. The unit test at test_suite_entity_entity.c:153-164 calls m_entity_enable_handler__default(&entity, NULL, NULL) and then asserts is_entity__enabled(&entity) is true. Because (a) p_game and p_world are NULL (dereferenced unconditionally — UB/crash) and (b) the function never sets ENTITY_FLAG__IS_ENABLED, this test cannot pass as written.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's name ("m_entity_enable_handler") and the accompanying unit test (test_suite_entity_entity.c:150: "Verifies that m_entity_enable_handler__default sets the ENTITY_FLAG__IS_ENABLED flag, causing is_entity__enabled to return true") establish the semantic intent: enabling an entity means setting the ENTITY_FLAG__IS_ENABLED bit on p_this_entity->entity_data.entity_flags, using the existing set_entity_as__enabled inline helper (entity.h:65-69).

The implementation does NOT set ENTITY_FLAG__IS_ENABLED at all. Instead, it retrieves the entity's Hitbox_AABB from the game's hitbox context (keyed by the world's UUID) and calls set_hitbox_aabb_as__active on it. This is the same hitbox-activation logic used by m_entity_dispose_handler__default (entity.c:42-59, which releases the hitbox) and m_entity_disable_handler__default (entity.c:95-113, which disables the hitbox). The enable handler's hitbox logic does not fulfill the entity-enable semantic.

The discrepancy is a critical semantic drift: the function name and test specify one behavior (set the enabled flag), but the code implements a different behavior (activate the hitbox). The #warning at line 70 ("replace with opaque hitbox pointer for default handler") suggests the hitbox-handling path is a placeholder, but even as a placeholder it should still set ENTITY_FLAG__IS_ENABLED to satisfy the documented contract.

Implementation Correctness:
Type compatibility — get_p_hitbox_context_from__game returns Hitbox_Context* via &p_game->hitbox_context (type-safe). get_pV_hitbox_manager_from__hitbox_context returns void*, which is explicitly cast to Hitbox_AABB_Manager*. This cast is unchecked: the hitbox context can hold managers of different types, and there is no runtime verification that pVM_hitbox_manager actually points to a Hitbox_AABB_Manager. If a different manager type is stored, accessing it as Hitbox_AABB_Manager* is undefined behavior. GET_UUID_P(p_world) casts p_world to Serialization_Header* and reads ->uuid (u32), which is type-safe only if p_world's actual type has a Serialization_Header as its first member with a compatible layout.

Undefined behavior — NULL dereference: p_game is dereferenced unconditionally before any null check (get_p_hitbox_context_from__game expands to &p_game->hitbox_context). p_world is dereferenced unconditionally (GET_UUID_P(p_world) expands to ((Serialization_Header*)p_world)->uuid). The unit test passes NULL for both. Additionally, get_p_hitbox_manager_instance_using__uuid_from__hitbox_context returns an invalid Hitbox_Manager_Instance when failing to find, and the code accesses ->pVM_hitbox_manager on that possibly-invalid instance without checking.

Debug/release divergence — The null check on p_hitbox_aabb_manager (lines 75-79) is guarded by #ifndef NDEBUG, so it is a no-op in release builds. In release, a failed manager lookup leads to a null/invalid pointer being used as Hitbox_AABB_Manager*.

Copy-paste error — Line 77 logs "m_entity_dispose_handler__default, p_hitbox_aabb_manager == 0." The correct function name is m_entity_enable_handler__default. (The same copy-paste error exists in m_entity_disable_handler__default at line 102.)

Ignored return value — set_hitbox_aabb_as__active returns bool (indicating whether the bit was set), but the return value is discarded. Similarly, set_hitbox_aabb_as__disabled in the disable handler ignores its return.

Validation — The function performs no parameter validation. p_this_entity is never checked for null. p_game and p_world are dereferenced before any validation is possible. The only guard is the debug-only manager null check. Validation of p_game and p_world is arguably the caller's responsibility for a low-level handler, but the unconditional dereference without any guard means even a debug check cannot prevent the crash.

Side Effects:
1. May mutate a Hitbox_AABB's active flag via set_hitbox_aabb_as__active, if a hitbox AABB is found for the entity. This is a mutation of the hitbox manager's managed data, not the entity itself.
2. Does NOT mutate p_this_entity's entity_flags (does not set ENTITY_FLAG__IS_ENABLED).
3. Does NOT mutate p_game or p_world.
4. In debug builds, may call debug_error when the hitbox manager lookup fails.
5. No heap allocation or deallocation occurs in this function.
