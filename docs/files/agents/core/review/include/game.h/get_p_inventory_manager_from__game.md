get_p_inventory_manager_from__game — core/include/game.h, lines 223-227

Forwards from the Game accessor to the World accessor to retrieve the Inventory_Manager.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game object.
2. p_game->pM_world must be a non-null pointer to an initialized World object (otherwise the chained get_p_world_from__game call will yield NULL and dereferencing it inside get_p_inventory_manager_from__world is undefined behavior).

Post-conditions:
1. Returns a pointer to the Game's Inventory_Manager (the inventory_manager field of the World reached via p_game->pM_world). The pointed-to object is not modified; no state in Game or World is mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of a forwarding accessor: it bridges from the Game layer to the Inventory_Manager held inside the associated World. The two-level delegation (get_p_world_from__game -> get_p_inventory_manager_from__world) correctly resolves the manager without reordering or omitting any step. There is no semantic drift; the function returns exactly the Inventory_Manager belonging to the Game's World.

Implementation Correctness:
Type compatibility — get_p_world_from__game returns World * and get_p_inventory_manager_from__world expects World * (defined in core/include/world/world.h:58); return type Inventory_Manager * matches the declared return type. No implicit conversions or truncation occur. p_game->pM_world is declared World * (core/include/defines.h:2551), so the field access in the chained callee is type-correct.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. Null dereference is possible only if the caller violates the stated pre-conditions (passes NULL p_game, or a Game whose pM_world is NULL); handling that is the caller's responsibility, consistent with the Lavender convention for low-level accessors.
Validation — no validation is included and none is needed for this thin accessor. The function is the lowest layer of the access path; guarding it here would be inconsistent with the surrounding accessors (e.g., get_p_world_from__game, get_p_item_manager_from__game) which also perform no null checks. The caller chain (set_p_inventory_manager, etc.) is responsible for ensuring p_game is valid.

Side Effects:
No side effects — the function performs no mutation of Game, World, or Inventory_Manager. The only observable effect is the returned pointer to the caller.
