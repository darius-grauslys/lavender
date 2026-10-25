# Function Review: poll_for_collision_node_update

## 1. Header
- **Function name**: `poll_for_collision_node_update`
- **File of origin**: `core/source/world/world.c`

## 2. Semantic
Checks whether an entity (identified by `uuid_u32_of__entry`) has moved across global space (chunk) boundaries between its old and new positions. If so, removes the entry from the old global space's collision node and adds it to the new global space's collision node.

## 3. Pre-conditions
1. `p_game` must be non-null (not validated within the function; consistent with codebase conventions).
2. `uuid_u32_of__entry` must be a valid identifier (not `IDENTIFIER__UNKNOWN__u32`). Not validated within this function; `add_entry_to__collision_node` validates it in debug builds, but `remove_entry_from__collision_node` does not.
3. If `position_old__3i32F4` and `position_new__3i32F4` map to different chunk vectors, the old and new global spaces must exist in the global space manager. The function checks for the existence of both and returns false if either is missing.

## 4. Post-conditions
1. If the old and new chunk vectors are equal (entity did not cross a chunk boundary), the function is a no-op and returns `true`.
2. If the chunk vectors differ and both old and new global spaces exist, the entry is removed from the old collision node and added to the new collision node. Returns `true`.
3. If the chunk vectors differ but either the old or new global space does not exist, an error is logged and the function returns `false`.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The implementation generally fulfills the semantic intent of migrating a collision node entry when an entity crosses chunk boundaries. However, there is a critical ordering bug that causes a state inconsistency:

**Critical Bug — State Inconsistency on New Global Space Failure:**

The function removes the entry from the old collision node **before** checking whether the new global space exists:

```c
remove_entry_from__collision_node(
        get_p_collision_node_pool_from__world(
            get_p_world_from__game(p_game)), 
        get_p_collision_node_from__global_space(
            p_global_space__old), 
        uuid_u32_of__entry);

Global_Space *p_global_space__new =
    get_p_global_space_from__global_space_manager(
            get_p_global_space_manager_from__game(
                p_game), 
            gsv__current__3i32);
if (!p_global_space__new) {
    debug_error("poll_for_collision_node_update, p_global_space__new == 0.");
    return false;
}
```

`remove_entry_from__collision_node` calls `release_collision_node_entry_from__collision_node_pool`, which returns the entry struct to the pool's free list. If the new global space does not exist, the function returns `false`, but the entry has already been removed from the old collision node and released to the pool. The entity identified by `uuid_u32_of__entry` is now orphaned — it is no longer present in any collision node, making it invisible to the collision detection system.

**The fix** is to check that the new global space exists **before** removing the entry from the old collision node. If the new global space is missing, the function should return `false` without modifying any state.

## 7. Implementation Correctness
- **Type compatibility**: All parameter types match their target field/function types. No implicit conversions or truncation.
- **Undefined behavior**: No broken pointer arithmetic, no null dereference (null checks are performed on `p_global_space__old` and `p_global_space__new`), no type punning, no out-of-bounds access.
- **Validation**: Validation of global space existence is appropriate for the function's role. However, the ordering of the remove-then-check sequence creates the state inconsistency described above.
- **Unused parameter**: The `gsv__3i32` parameter in `add_entry_to__collision_node` is passed but never referenced in the function body. This is a minor code smell but does not affect correctness.

## 8. Side Effects
- **Mutating**: The function mutates the collision node linked lists of global spaces. When the entity crosses a chunk boundary, it removes a `Collision_Node_Entry` from the old global space's collision node (releasing it back to the pool) and allocates a new `Collision_Node_Entry` in the new global space's collision node.
- When the entity does not cross a chunk boundary or when a global space is missing, no mutation occurs (in the failure case, the mutation has already happened — see the critical bug above).
