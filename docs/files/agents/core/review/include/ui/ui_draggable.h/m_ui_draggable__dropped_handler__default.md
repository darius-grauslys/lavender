# m_ui_draggable__dropped_handler__default

**File of origin:** `core/source/ui/ui_draggable.c`

## Semantic

Handles the drop event for a draggable UI element by clearing its focused state and, if the element has a parent, snapping its position back to the parent's position.

## Pre-conditions

1. `p_this_draggable` must be non-null and point to a valid `UI_Element`.
2. `p_game` must be non-null and point to a valid `Game`.
3. `p_graphics_window` must be non-null and point to a valid `Graphics_Window`.
4. The graphics window must have an associated hitbox AABB manager (returned by `get_pV_hitbox_manager_from__graphics_window`).
5. If `p_this_draggable->p_parent` is non-null, the parent must have a valid hitbox AABB registered in the hitbox manager (so that `get_position_3i32_from__p_ui_element` can retrieve its position).

## Post-conditions

1. `p_this_draggable` has its `UI_FLAGS__BIT_IS_FOCUSED` flag cleared (element is no longer focused).
2. If `p_this_draggable->p_parent` was null, the function returns early without modifying the element's position.
3. If `p_this_draggable->p_parent` was non-null, `p_this_draggable`'s position is set to the same position as its parent element.
4. **BUG:** The `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` flags are NOT cleared. The element remains in a "being dragged" and "being held" state after being dropped, which is semantically incorrect. The dedicated `set_ui_element_as__dropped` function (which clears both flags) is never called.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The implementation partially fulfills the semantic intent of a "dropped handler." A dropped handler should transition the element out of its dragged/held state and restore it to a resting state. The function does clear the focused flag and snaps the position back to the parent, which aligns with the intent. However, it fails to clear the `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` flags. The codebase provides `set_ui_element_as__dropped()` specifically for this purpose (clearing both flags), and the sibling function `m_ui_draggable__dragged_handler__default` sets both `UI_FLAGS__BIT_IS_FOCUSED` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` when dragging begins. The dropped handler should symmetrically call `set_ui_element_as__dropped()` to clear the drag-related state. Without this call, the element's flags remain inconsistent after a drop, potentially causing incorrect behavior in subsequent input processing (e.g., the element may still be treated as being dragged).

## Implementation Correctness

- **Type compatibility:** All parameter types match their target function signatures exactly. No implicit conversions or truncation occur. The `void*` return from `get_pV_hitbox_manager_from__graphics_window` is explicitly cast to `Hitbox_AABB_Manager*`.
- **Undefined behavior:** No null pointer dereference, out-of-bounds access, or type punning. The function checks `p_this_draggable->p_parent` for null before dereferencing it. The early return when parent is null is appropriate.
- **Validation:** The function does not validate `p_game` or `p_graphics_window` for null, but this is consistent with the codebase convention (e.g., `set_position_3i32_of__ui_element` follows the same pattern). The null check on `p_parent` is appropriate for the function's role.

## Side Effects

1. Modifies `p_this_draggable->ui_flags` by clearing the `UI_FLAGS__BIT_IS_FOCUSED` bit.
2. **Missing side effect:** Should also clear `UI_FLAGS__BIT_IS_BEING_HELD` and `UI_FLAGS__BIT_IS_BEING_DRAGGED` (via `set_ui_element_as__dropped`), but does not.
3. If `p_this_draggable->p_parent` is non-null, mutates the position of `p_this_draggable`'s associated hitbox AABB (via `set_position_3i32_of__ui_element`, which calls `set_hitbox_aabb__position_with__3i32` and may trigger the element's transformed handler).
