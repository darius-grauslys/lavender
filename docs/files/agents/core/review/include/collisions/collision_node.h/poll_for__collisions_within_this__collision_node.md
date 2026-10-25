poll_for__collisions_within_this__collision_node — core/source/collisions/collision_node.c (lines 151-194)

## 1. Header

- **Function name:** `poll_for__collisions_within_this__collision_node`
- **File of origin:** `core/source/collisions/collision_node.c`

## 2. Semantic

Iterates backward through the singly-linked list of collision node entries (tail to head via `p_previous_entry`). For each entry, resolves the stored hitbox UUID against the `Hitbox_AABB_Manager` obtained from the game's hitbox context. If the resolved hitbox is non-null, is not the querying `p_hitbox_aabb` itself, and is colliding with `p_hitbox_aabb`, invokes the provided collision-handler callback for the pair.

## 3. Pre-conditions

1. `p_collision_node` must not be NULL. Guarded with an early return at line 159.
2. `p_game` must not be NULL. It is dereferenced indirectly through `get_p_hitbox_context_from__game` (line 166) and `get_p_world_from__game` (line 167) without an explicit null check.
3. `p_hitbox_aabb` should not be NULL. It is forwarded directly to `is_hitbox_aabb__colliding` (line 181) and onward to `is_this_hitbox_aabb__overlapping_this_hitbox_aabb`, which dereferences it, without a null check.
4. `f_hitbox_collision_handler` should not be NULL. It is invoked as a function pointer (line 184) without a null check when a collision is detected.
5. The world identified by `GET_UUID_P(get_p_world_from__game(p_game))` must have a registered hitbox manager in the game's hitbox context. If not, `get_pV_hitbox_manager_from__hitbox_context` may trigger a null dereference (see Implementation Correctness, item 2).
6. `p_collision_node->p_linked_list__collision_node_entries__tail` may be NULL (empty list); the `while` loop at line 169 handles this gracefully by skipping the loop body entirely.
7. `p_world` is forwarded to the handler; for semantic consistency it should be the same world obtainable from `p_game`. This is not verified by the function.

## 4. Post-conditions

1. The function returns void (no return value).
2. The collision node and its entries are not modified. Traversal uses read-only advancement of the `p_previous_entry` pointer.
3. No direct mutations are performed on `p_game`, `p_world`, or `p_hitbox_aabb` by this function.
4. For each colliding "other" hitbox, `f_hitbox_collision_handler` is invoked exactly once with `(p_game, p_world, p_hitbox_aabb, p_hitbox_aabb__other)`.
5. Entries whose UUID resolves to NULL (stale/deallocated hitbox), to `p_hitbox_aabb` itself, or to a non-colliding hitbox are silently skipped without handler invocation.

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The implementation fulfills the semantic intent declared by the function name. The backward traversal (tail → head via `p_previous_entry`) is consistent with the singly-linked list structure established by `add_entry_to__collision_node`, which prepends new entries and chains them backward; the head entry's `p_previous_entry` is NULL, which correctly terminates the `while` loop.

The self-exclusion check (`p_hitbox_aabb__other != p_hitbox_aabb` at line 179) is correct and necessary: a collision node may contain an entry whose UUID refers to the querying hitbox itself, and reporting self-collision would be semantically wrong.

The null guard (`p_hitbox_aabb__other && ...` at line 178) correctly short-circuits entries whose UUID does not resolve to a live hitbox (e.g., a deallocated or never-allocated slot), preventing a null dereference in `is_hitbox_aabb__colliding`. The short-circuit ordering — null check, then identity check, then collision test — is the correct order for safety.

No fields of `Collision_Node_Entry` are omitted or accessed beyond `uuid_of__hitbox__u32` and `p_previous_entry`, both of which are the only members of the struct (see `defines.h:509-512`). The computation and dispatch logic match the function's descriptive name with no semantic drift.

## 7. Implementation Correctness

- **Type compatibility:** All parameter types match their usage targets exactly. `p_hitbox_aabb_manager` is a `void *` returned by `get_pV_hitbox_manager_from__hitbox_context` and explicitly cast to `Hitbox_AABB_Manager*`, consistent with the codebase-wide pattern. `p_hitbox_aabb__other` is `Hitbox_AABB *`, matching the `f_Hitbox_AABB_Collision_Handler`'s expected parameter type. `uuid_of__hitbox__u32` is `Identifier__u32`, matching the second parameter of `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`. No implicit conversions or truncation risks.

- **Undefined behavior — `get_pV_hitbox_manager_from__hitbox_context` (line 164-167):** This inline function dereferences `->pVM_hitbox_manager` on the result of `get_p_hitbox_manager_instance_using__uuid_from__hitbox_context` without a null check. The documentation states this lookup "Reports no error upon failure to find" and may return NULL. If the world has no registered hitbox manager, this constitutes a null pointer dereference. This is a systemic pattern repeated at dozens of call sites (client.c, entity.c, world.c, ui_element.c, etc.), so it is a codebase-wide validation gap rather than a unique defect. Technically UB, but only in the error path where pre-condition 5 is violated.

- **Undefined behavior — `p_hitbox_aabb` not null-checked (line 181):** If `p_hitbox_aabb` is NULL, `is_hitbox_aabb__colliding(NULL, p_hitbox_aabb__other)` propagates into `is_this_hitbox_aabb__overlapping_this_hitbox_aabb`, which calls `initialize_vector_3i32F4_as__aa_bb(&aa__one_moving, NULL, ...)` and dereferences NULL. The author's comment acknowledges this: "we may need to try and look for errors, but this is probably safe for now."

- **Undefined behavior — `f_hitbox_collision_handler` not null-checked (line 184):** A NULL function pointer invocation is UB. No guard protects the `f_hitbox_collision_handler(...)` call.

- **Undefined behavior — `p_game` not null-checked (lines 166-167):** `p_game` is dereferenced indirectly via `get_p_hitbox_context_from__game` (`&p_game->hitbox_context`) and `get_p_world_from__game` (`p_game->pM_world`) without a null check. Again, the author's comment covers this deferred validation.

- **Off-by-one / loop logic:** No issues. The `while (p_collision_node_entry)` loop correctly terminates when `p_previous_entry` is NULL. The advancement `p_collision_node_entry = p_collision_node_entry->p_previous_entry` (line 191-192) correctly follows the singly-linked list. There is no off-by-one in entry counting or traversal.

- **Boolean use of `Direction__u8`:** `is_hitbox_aabb__colliding` returns `Direction__u8` (a `uint8_t`), which is used in a boolean context within the `&&` chain (line 181). `DIRECTION__NONE` is defined as `0` (see `defines.h:159`), so a non-colliding result evaluates to false, while any non-zero collision direction evaluates to true. This is an idiomatic and valid enum-as-boolean usage consistent with the codebase.

- **Redundant check analysis:** The condition `p_hitbox_aabb__other && p_hitbox_aabb__other != p_hitbox_aabb` is NOT redundant — the first operand checks for a NULL lookup result, the second checks for object identity (self-exclusion). Both are required.

## 8. Side Effects

- **No direct mutations:** The function does not modify `p_collision_node`, any `Collision_Node_Entry`, `p_game`, `p_world`, or `p_hitbox_aabb`. Traversal is read-only.
- **Indirect effects:** The function's sole observable effect is delegating to `f_hitbox_collision_handler` for each detected collision. The handler may mutate arbitrary game state, entities, or hitboxes. Per the review scope (callee sites are out of scope), only the delegation itself is described: the function invokes the callback once per colliding "other" hitbox with `(p_game, p_world, p_hitbox_aabb, p_hitbox_aabb__other)`.
- **No allocation, deallocation, or I/O** is performed by this function.
