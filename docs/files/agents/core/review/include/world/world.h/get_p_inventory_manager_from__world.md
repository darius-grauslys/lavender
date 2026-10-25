get_p_inventory_manager_from__world — core/include/world/world.h

Returns a pointer to the inventory_manager sub-object embedded within the World struct.

Pre-conditions:
1. p_world must be a non-null pointer to a valid, initialized World struct. Passing NULL results in undefined behavior (null pointer dereference).
2. p_world must point to writable memory, since the returned pointer allows mutation of the Inventory_Manager.

Post-conditions:
1. Returns a non-null pointer of type Inventory_Manager * pointing to the inventory_manager field embedded within the World struct.
2. The World struct itself is not modified; the returned pointer aliases the internal inventory_manager member.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly returns the address of the inventory_manager member of the World struct. The World struct (defined in core/include/defines.h) contains the field `Inventory_Manager inventory_manager;` as an embedded value (not a pointer), so `&p_world->inventory_manager` yields a valid `Inventory_Manager *`. The implementation matches the semantic intent exactly.

Implementation Correctness:
Type compatibility — the return type `Inventory_Manager *` matches the type of `&p_world->inventory_manager` exactly. No implicit conversions or truncation occur.
Undefined behavior — the only risk is a null pointer dereference if p_world is NULL. This is consistent with the majority of accessor functions in the same header (e.g., get_p_camera_from__world, get_p_item_manager_from__world, get_p_tile_logic_context_from__world), which also do not perform null checks. Only get_p_entity_manager_from__world performs a debug-only null check. Validation is the caller's responsibility for this low-level accessor.
No pointer arithmetic, no type punning, no out-of-bounds access.

Side Effects:
No side effects — the function does not modify any state. It only computes and returns the address of an embedded struct member.

Lavender-Specific Semantics:
This function is an accessor (getter), not an initialization function. The name does not contain "init", "initialize", or "reset", so the Lavender initialization semantics (cleaning up a struct to initial conditions for pool reuse) do not apply here.
