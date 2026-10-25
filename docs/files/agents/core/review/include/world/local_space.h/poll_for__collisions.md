poll_for__collisions — core/source/world/local_space.c

Examines the local_space and all 8 neighbors (center, NE, N, NW, E, W, SE, S, SW), retrieving each neighbor's Collision_Node and delegating to poll_for__collisions_within_this__collision_node to detect AABB hitbox collisions.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game instance.
2. p_world must be a non-null pointer to a valid World instance.
3. p_local_space must be a non-null pointer to a valid Local_Space object.
4. f_hitbox_collision_handler must be a non-null function pointer.
5. p_hitbox_aabb must be a non-null pointer to the Hitbox_AABB being tested.
6. p_local_space must have its neighbor pointers (north, east, south, west) either pointing to valid Local_Space objects or NULL. This is a pre-condition that the caller must ensure.

Post-conditions:
1. The collision handler f_hitbox_collision_handler is invoked for every colliding Hitbox_AABB found in the center local_space and all 8 neighbors, excluding p_hitbox_aabb itself.
2. No return value; the function completes when all 9 collision nodes have been polled.

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation intent is to poll the center local_space and all 8 surrounding neighbors for collisions. The function correctly identifies all 9 positions (center, 4 cardinal, 4 diagonal). However, the implementation contains a critical bug in the diagonal neighbor accesses.

For diagonal neighbors (NE, NW, SE, SW), the function chains two pointer dereferences without null checks. For example, the NE neighbor is accessed as:
```c
p_local_space->p_local_space__north->p_local_space__east
```
If `p_local_space->p_local_space__north` is NULL (which is a valid state for edge/corner local spaces), then `->p_local_space__east` dereferences a null pointer, causing undefined behavior. The same issue applies to NW, SE, and SW diagonal accesses.

The cardinal direction accesses (N, E, S, W) are safe because they pass the neighbor pointer directly to `get_p_collision_node_from__local_space`, which handles null input by returning 0. The callee `poll_for__collisions_within_this__collision_node` also has a null check for the collision node.

This bug causes the semantic intent (polling all 8 neighbors) to fail at runtime when any cardinal neighbor pointer is NULL, as the diagonal neighbor in that direction cannot be safely accessed.

Implementation Correctness:
- Type compatibility: All parameter types match their target usages. No implicit conversions or truncation.
- Undefined behavior: The diagonal neighbor accesses (NE, NW, SE, SW) cause null pointer dereference when intermediate neighbor pointers (north or south) are NULL. This is undefined behavior. The cardinal direction accesses are safe.
- Validation: No validation is performed for null neighbor pointers in diagonal accesses. The caller cannot guarantee that cardinal neighbors are non-null, so this validation must be performed within the function. The cardinal direction accesses appropriately rely on get_p_collision_node_from__local_space and poll_for__collisions_within_this__collision_node to handle null collision nodes.

Side Effects:
The function has the side effect of invoking f_hitbox_collision_handler for each detected collision between p_hitbox_aabb and other hitboxes found in the polled collision nodes. No state is mutated on p_local_space or its neighbors directly. No side effects beyond the collision handler invocations.
