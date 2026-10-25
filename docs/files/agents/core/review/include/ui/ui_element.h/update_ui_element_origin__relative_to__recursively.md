# update_ui_element_origin__relative_to__recursively

## File of origin
`core/source/ui/ui_element.c`

## Semantic
Recursively traverses a UI element tree (via child and next-sibling pointers) and applies a relative position delta to each element's hitbox. For each element, the new position is computed as `current_position - position__old + position__new`, effectively shifting every element by the delta `(new - old)`.

## Pre-conditions
1. `p_ui_element` must be non-null. Checked in debug builds (`#ifndef NDEBUG`); in release builds, the caller is responsible for ensuring non-null.
2. `p_game` must be a valid, initialized `Game` pointer. It is used to retrieve the hitbox context and hitbox AABB manager.
3. `p_ui_manager` must be a valid, initialized `UI_Manager` pointer. It is used to look up the hitbox AABB manager (via its UUID) and to mark the manager as dirty.
4. The UI element tree rooted at `p_ui_element` must be acyclic (no cycles in `p_child` or `p_next` pointers). Cycles would cause infinite recursion and stack overflow.
5. `position__old__3i32` represents the previous reference origin, and `position__new__3i32` represents the new reference origin. Both are passed by value and need no additional constraints.

## Post-conditions
1. Every UI element reachable from `p_ui_element` via child and next-sibling pointers that has an associated `Hitbox_AABB` has its hitbox position updated to `current_position + (position__new - position__old)`.
2. UI elements without an associated `Hitbox_AABB` are silently skipped (no position update, no error).
3. The `UI_Manager` is marked as dirty (`UI_MANAGER_FLAG__IS_DIRTY` is set) if at least one element in the tree has a valid hitbox AABB.
4. Each hitbox AABB that receives a position update is also marked as dirty via `set_hitbox_aabb_as__dirty`.
5. The function returns `void`; there is no return value.

## Correctness Verdict
Correct

## Semantic Alignment
The implementation correctly fulfills the semantic intent. The formula used in `update_ui_element_origin__relative_to` is:

```
position_final = add_vectors__3i32(
    subtract_vectors__3i32(current_position, position__old),
    position__new)
```

This simplifies to `current_position + (position__new - position__old)`, which is the correct computation for applying a relative offset to each element when the origin reference point moves from `position__old` to `position__new`.

The recursive traversal correctly visits the current element, then recurses into both the child subtree and the next-sibling subtree, ensuring all elements in the tree are updated.

## Implementation Correctness
- **Type compatibility**: All parameter types match their usage. `Vector__3i32` values are passed by value and used consistently with `add_vectors__3i32` and `subtract_vectors__3i32`, which both accept and return `Vector__3i32`. The `Game*` and `UI_Manager*` pointers are used correctly with the hitbox context and manager APIs.
- **Undefined behavior**: No null dereference occurs in the recursive calls because `does_ui_element_have__child` and `does_ui_element_have__next` both perform null-safe checks (`p_ui_element && p_ui_element->p_child`). The delegation to `update_ui_element_origin__relative_to` includes its own debug-only null check, and additionally checks for a null `p_hitbox_aabb` before dereferencing, returning early if no hitbox exists.
- **Validation**: The null check on `p_ui_element` is debug-only (`#ifndef NDEBUG`), consistent with the codebase pattern. In release builds, the caller is expected to provide a valid pointer. The null check on the hitbox AABB (`if (!p_hitbox_aabb) { return; }`) is appropriate — elements without hitboxes are valid and should be skipped rather than treated as errors.
- **Recursion safety**: The recursion terminates because `does_ui_element_have__child` and `does_ui_element_have__next` return false when the respective pointers are null, preventing further recursion down empty branches.

## Side Effects
- **Mutates hitbox positions**: Each UI element in the tree that has an associated `Hitbox_AABB` has its `position__3i32F4` field updated via `set_hitbox_aabb__position_with__3i32`.
- **Marks hitboxes as dirty**: Each updated `Hitbox_AABB` is marked dirty via `set_hitbox_aabb_as__dirty` (called inside `set_hitbox_aabb__position_with__3i32`).
- **Marks UI manager as dirty**: The `UI_Manager` is marked dirty via `set_ui_manager_as__dirty` in `update_ui_element_origin__relative_to`, but only if at least one element has a valid hitbox AABB (due to the early return when `p_hitbox_aabb` is null).
- No other observable side effects. The function does not allocate, deallocate, or modify any global state beyond the UI element hitbox positions and the UI manager dirty flag.
