# set_ui_element__size

**File of origin:** `core/source/ui/ui_element.c` (lines 285-312)

## Semantic

Sets the width and height of the `UI_Element`'s associated `Hitbox_AABB`, then invokes the element's transformed handler (if one is registered) so that the UI element can react to the size change.

## Pre-conditions

1. `p_game` must be a valid, non-null pointer to a `Game` instance.
2. `p_graphics_window` must be a valid, non-null pointer to a `Graphics_Window` that contains a `Hitbox_AABB_Manager`.
3. `p_ui_element` must be a valid, non-null pointer to a `UI_Element` that has been associated with a `Hitbox_AABB` (i.e., it has a valid UUID that maps to an entry in the hitbox manager).
4. `width` and `height` are `Quantity__u32` values representing the desired dimensions.

## Post-conditions

1. The `Hitbox_AABB` associated with `p_ui_element` has its `width__quantity_u32` and `height__quantity_u32` fields set to the provided `width` and `height` values, and is marked as dirty.
2. If `p_ui_element` has a registered `m_ui_transformed_handler`, that handler is invoked with the `UI_Element`, the `Hitbox_AABB`, the hitbox's current position, the `Game`, and the `Graphics_Window`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully carries out the stated semantic: it retrieves the hitbox manager from the graphics window, looks up the hitbox associated with the UI element, delegates to `set_size_of__hitbox_aabb` to mutate the width/height fields, and conditionally fires the transformed handler. The delegation to `set_size_of__hitbox_aabb` is the correct mechanism for mutating the hitbox dimensions, and the transformed handler invocation matches the pattern used by sibling functions (e.g., `set_ui_element__hitbox`, `set_ui_element__position`).

## Implementation Correctness

- **Type compatibility:** Parameter types match the target field types. `width` and `height` are `Quantity__u32`, and `set_size_of__hitbox_aabb` accepts `Quantity__u32` for both its width and height parameters. No implicit conversions or truncation occur.
- **Null handling:** The function does not explicitly validate that `p_hitbox_aabb` is non-null before passing it to `set_size_of__hitbox_aabb`. The lookup function `get_p_hitbox_aabb_of__ui_element` can return `NULL` if the UI element's UUID does not map to a registered hitbox. However, `set_size_of__hitbox_aabb` contains a debug-only null check (`#ifndef NDEBUG`) that logs an error and returns early. In release builds (`NDEBUG` defined), a null `p_hitbox_aabb` would be dereferenced, causing undefined behavior. This is inconsistent with `set_ui_element__hitbox` (lines 314-340), which explicitly checks `if (!p_hitbox_aabb)` and returns with a `debug_error` message. The same pattern of omitting the null check is also present in `set_ui_element__position` (around line 235), suggesting this may be an accepted pattern in this module, but it remains a latent risk.
- **No out-of-bounds access or pointer arithmetic issues** are present in this function.

## Side Effects

- **Mutates** the `Hitbox_AABB` associated with `p_ui_element`: sets its `width__quantity_u32`, `height__quantity_u32`, and marks it as dirty via `set_hitbox_aabb_as__dirty`.
- **Invokes** the `m_ui_transformed_handler` callback on `p_ui_element` if one is registered. The handler receives the UI element, hitbox, position, game, and graphics window, and may have its own side effects (out of scope for this review).
- No other global or static state is modified by this function directly.
