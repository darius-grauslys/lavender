allocate_entity_into__world — core/include/world/world.h

Convenience wrapper that allocates a new entity into the world's entity manager and assigns it a position via its hitbox.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game.
2. p_game->pM_world must be non-null (world must be allocated).
3. the_kind_of_entity must be a valid Entity_Kind value (not Entity_Kind__Unknown).
4. position__3i32F4 is any valid Vector__3i32F4; no range constraint is required by the declaration itself.

Post-conditions:
1. A new Entity is allocated in the world's Entity_Manager via allocate_entity_in__entity_manager.
2. If allocation succeeds, the entity's position is set via its Hitbox_AABB (allocated and positioned using position__3i32F4).
3. Returns a pointer to the newly allocated Entity, or NULL (0) if the entity pool is exhausted.
4. The returned entity is enabled by default (set_entity_as__enabled is called in allocate_entity_in__entity_manager).

Correctness Verdict: Incorrect

Semantic Alignment:
The function declaration is semantically sound — it provides a high-level convenience API for spawning an entity at a given position in the world. However, the implementation is entirely missing from world.c (and all other source files). The declaration states the function "delegates to world.c," but no definition exists anywhere in the codebase. This means any call site will produce a linker error. The function signature correctly mirrors the parameter types used by the underlying allocate_entity_in__entity_manager (Game*, Entity_Kind) and adds a position parameter (Vector__3i32F4) that would be used to initialize the entity's hitbox position. The semantic intent is correct, but the implementation gap makes it non-functional.

Implementation Correctness:
Type compatibility — the parameter types match the codebase conventions exactly: Game* matches get_p_world_from__game/get_p_entity_manager_from__game usage; enum Entity_Kind matches the kind parameter in allocate_entity_in__entity_manager; Vector__3i32F4 matches the position type used throughout the hitbox and world systems. No implicit conversions or truncation in the declaration.
Undefined behavior — no concerns in the declaration itself. However, the missing implementation means there is no runtime behavior to evaluate.
Validation — the declaration does not specify any validation, which is consistent with the pattern in allocate_entity_in__entity_manager (which checks for null p_entity_manager internally). The caller is responsible for ensuring p_game and p_game->pM_world are valid.

Side Effects:
The function would have the following side effects if implemented:
1. Mutates the world's Entity_Manager by allocating a new entity slot (advances p_ptr_entity__next_in_ptr_array).
2. Calls the entity initializer (f_entity_initializer) which zeroes the entity data and sets default handlers.
3. Calls sanitize_entity_functions to copy registered function pointers for the entity kind.
4. Sets the entity as enabled (modifies entity_flags).
5. Mutates the world's Hitbox_AABB_Manager by allocating a hitbox for the entity.
6. Sets the hitbox position to position__3i32F4 (marks hitbox as dirty).
