get_p_entity_manager_from__game — core/include/game.h

Retrieves the `Entity_Manager` associated with the game's active `World`.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid `Game` struct.
2. `p_game->pM_world` must be non-null (the game must have an active world).
3. The `World` pointed to by `p_game->pM_world` must contain a valid `entity_manager` field (always true for any properly constructed `World`).

Post-conditions:
1. Returns a pointer to the `Entity_Manager` held within the game's active `World`.
2. The returned pointer is `&p_game->pM_world->entity_manager`, valid for the lifetime of the `World`.

Correctness Verdict: Correct

Semantic Alignment:
The function delegates to `get_p_entity_manager_from__world` after obtaining the world via `get_p_world_from__game`. This matches the semantic intent of retrieving the entity manager from the game through its world abstraction. The implementation correctly chains the two accessors without reordering or omitting any logic.

Implementation Correctness:
Type compatibility — `get_p_world_from__game` returns `World *`, and `get_p_entity_manager_from__world` accepts `World *`; the types match exactly. The return type `Entity_Manager *` is consistent across all functions in the chain. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. Inside `get_p_entity_manager_from__world`, a debug-mode null check on `p_world` is performed (returns 0 if null under `!NDEBUG`); in release builds (`NDEBUG` defined), the null check is compiled out, so a null `p_game` or null `pM_world` would be undefined behavior — this is the caller's responsibility.
Validation — the debug-mode null guard in the callee provides safety during development; no additional validation is needed in this accessor since it is a thin delegation wrapper.

Side Effects: No side effects.
