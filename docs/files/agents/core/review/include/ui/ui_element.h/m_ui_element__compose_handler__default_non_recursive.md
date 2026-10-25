m_ui_element__compose_handler__default_non_recursive — core/source/ui/ui_element.c, lines 495-539

## Semantic

Composes a single UI element's tile span into the graphics window's UI tile map and triggers platform-level composition. This is the non-recursive portion of the default compose handler — it handles only the current element, not its children or siblings. The recursive variant (`m_ui_element__compose_handler__default`) calls this function first, then recursively composes the child if one exists.

## Pre-conditions

1. `p_ui_element` must be non-null.
2. `p_game` must be non-null (used to retrieve the UI manager and hitbox manager).
3. `p_graphics_window` must be non-null (used to retrieve the UI tile map and other graphics resources).
4. The UI element should be using a UI tile span (not a sprite), as indicated by the `UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN` flag being clear. This is normally guaranteed because the compose handler is set via `set_ui_element__compose_handler` or `set_ui_tile_span_of__ui_element`, both of which call `set_ui_element_as__using_ui_tile_span` (clearing the sprite flag).
5. The UI element should have an associated `Hitbox_AABB` allocated in the hitbox AABB manager, so that `get_ui_tile_span_of__ui_element` can compute the span's dimensions and position indices.

## Post-conditions

1. The `UI_MANAGER_FLAG__IS_DIRTY` flag is set on the UI manager associated with the graphics window, signaling that a composition is needed.
2. The UI element's tile span data (corners, edges, fill) is written into the graphics window's `UI_Tile_Map__Wrapper` via `generate_ui_span_in__ui_tile_map`.
3. The platform-specific composition function `PLATFORM_compose_ui_span_in__gfx_window` is invoked with the computed tile span dimensions and position indices.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills the semantic intent. The function:
- Marks the UI manager as dirty (signaling pending composition).
- Retrieves the hitbox AABB manager to look up the element's hitbox.
- Calls `get_ui_tile_span_of__ui_element` to obtain the `UI_Tile_Span` pointer and compute the span's width, height, and tile-map indices from the element's hitbox position and the graphics window's origin.
- Generates the tile span into the UI tile map via `generate_ui_span_in__ui_tile_map`.
- Invokes the platform-specific composition function.

The computation of `index_x__u32` and `index_y__u32` in `get_ui_tile_span_of__ui_element` correctly translates the hitbox position relative to the graphics window's position and center, then offsets by half the span width/height to center the span. The delegation to `generate_ui_span_in__ui_tile_map` and `PLATFORM_compose_ui_span_in__gfx_window` is correct.

## Implementation Correctness

1. **Missing null check on `p_const_ui_tile_span`**: `get_ui_tile_span_of__ui_element` can return `0` (null) when the UI element is using a sprite (`is_ui_element__using_sprite` returns true) or when the element lacks a hitbox (`p_hitbox_aabb` is null). This null pointer is then passed directly to `generate_ui_span_in__ui_tile_map`, which dereferences it (`p_ui_tile_span->size_of__ui_tile_in__8x8_tiles__u8` at the loop condition on line 168 of `ui_tile_map.c`). This constitutes a potential null pointer dereference.

   However, in normal usage, the compose handler is only set via `set_ui_element__compose_handler` or `set_ui_tile_span_of__ui_element`, both of which clear the sprite flag via `set_ui_element_as__using_ui_tile_span`. Additionally, the caller `f_compose_ui_element_callback__ui_manager` in `ui_manager.c` (line 953) checks `does_ui_element_have__compose_handler` before invoking the handler, which verifies `is_ui_element__using_ui_tile_span(p_ui_element)`. This prevents the sprite case. The hitbox case (element has no hitbox) is not explicitly guarded, but in practice, UI elements with tile spans are expected to have hitboxes allocated before composition. A defensive null check on `p_const_ui_tile_span` before calling `generate_ui_span_in__ui_tile_map` would improve robustness.

2. **Missing null check on `p_hitbox_aabb_manager`**: Unlike the sibling function `m_ui_element__dispose_handler__default` (line 83) which checks `if (p_hitbox_aabb_manager)` before using it, this function does not. The `get_pV_hitbox_manager_from__graphics_window` function can return null if the hitbox manager instance is not found (via `dehash_identitier_u32_in__contigious_array` returning null). If null is returned, it is passed to `get_ui_tile_span_of__ui_element`, which passes it to `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager`. Following the pattern in `m_ui_element__dispose_handler__default`, a null check would be appropriate here.

3. **`PLATFORM_compose_ui_span_in__gfx_window` is always called**: Even when the tile span is null (and width/height are 0), the platform function is still invoked with zero dimensions. This may be intentional (to ensure the platform knows composition occurred), but the behavior when receiving zero dimensions is platform-dependent and undocumented.

4. **Type compatibility**: All parameter types match their target function signatures exactly. `Quantity__u32` (typedef for `uint32_t`) is used for width/height, and `Index__u32` (also `uint32_t`) is used for indices. The cast `(Hitbox_AABB_Manager*)` on the return of `get_pV_hitbox_manager_from__graphics_window` (which returns `void*`) is consistent with the pattern used throughout the file (e.g., in `allocate_hitbox_for__ui_element`, `set_position_3i32_of__ui_element`, etc.). No implicit conversions or truncation issues.

## Side Effects

1. **Mutates the UI manager**: Sets the `UI_MANAGER_FLAG__IS_DIRTY` flag on the `UI_Manager` associated with the graphics window.
2. **Mutates the UI tile map**: Writes `UI_Tile_Raw` values into the `UI_Tile_Map__Wrapper`'s `p_ui_tile_data` buffer, overwriting existing tile data in the span's region.
3. **Invokes platform-specific composition**: Calls `PLATFORM_compose_ui_span_in__gfx_window`, which may have additional side effects such as updating a framebuffer, OAM, or other platform-specific rendering state. These are outside the scope of this function's direct observable effects.
