get_ui_tile_span_of__ui_element — core/source/ui/ui_element.c

Computes the tile-span dimensions (width/height in 8x8-pixel tiles) and tile-map indices (x/y) for a UI element based on its hitbox AABB dimensions and position relative to a graphics window. Returns a pointer to the UI element's ui_tile_span member on success, or null if the element is using a sprite or has no associated hitbox.

Pre-conditions:
1. p_hitbox_aabb_manager must be a non-null pointer to a valid Hitbox_AABB_Manager (the callee get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager checks this in debug builds).
2. p_graphics_window must be a non-null pointer to a valid Graphics_Window with initialized position_of__gfx_window, width_of__graphics_window__u32, and height_of__graphics_window__u32 fields.
3. p_ui_element must be a non-null pointer to a valid UI_Element.
4. p_width_in__tiles, p_height_in__tiles, p_index_x__u32, and p_index_y__u32 must each be non-null pointers to writable memory (they are dereferenced unconditionally at function entry).
5. If the UI element is using a sprite (UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN flag set), the function returns null and all output parameters remain 0.
6. If the UI element's UUID does not correspond to an allocated hitbox in the manager, the function returns null and all output parameters remain 0.

Post-conditions:
1. All four output parameters are initialized to 0 at function entry, regardless of the exit path.
2. If the element is using a sprite or has no hitbox, the function returns null (0) and all output parameters remain 0.
3. If successful, p_width_in__tiles holds the hitbox width divided by 8 (UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT = 3), and p_height_in__tiles holds the hitbox height divided by 8.
4. If successful, p_index_x__u32 holds the tile-map X index computed as: ((hitbox_x - window_x + window_width/2) >> 3) - (width_in_tiles >> 1), centering the tile span on the hitbox position relative to the window center.
5. If successful, p_index_y__u32 holds the tile-map Y index computed analogously for the Y axis.
6. The function returns a pointer to p_ui_element->ui_tile_span (a const UI_Tile_Span *).

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent: it derives tile-span geometry (dimensions and map indices) from the UI element's hitbox AABB and the graphics window's position and dimensions. The width and height are correctly converted from pixels to 8x8 tiles via right-shift by UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT (3). The tile index computation correctly translates the hitbox position into window-relative tile coordinates and then centers the span by subtracting half the span's tile dimensions. The early-return for sprite-based elements is correct: sprite-based UI elements do not have a tile span, so returning null is appropriate. The null return for missing hitboxes is also correct, as the function cannot compute tile geometry without a hitbox.

Implementation Correctness:
Type compatibility: The width/height computations assign u32 (p_hitbox_aabb->width__quantity_u32 >> 3) to Quantity__u32 * — correct. The index computations assign u32 results to Index__u32 * — correct. The return value is UI_Tile_Span * implicitly converted to const UI_Tile_Span * — correct.

Potential signed/unsigned mixing: In the index computation, get_x_i32_from__hitbox_aabb returns Signed_Index__i32 (i32), while p_graphics_window->width_of__graphics_window__u32 is u32. The expression i32 - i32 + u32 causes the i32 subexpression to be implicitly converted to u32 per C integer promotion rules. If the intermediate result (hitbox_x - window_x) is negative and its magnitude exceeds window_width/2, the conversion to u32 would wrap around, producing an incorrect tile index. This is a latent risk but is consistent with the codebase's low-level style where callers are expected to ensure coordinates are within valid ranges. No explicit cast or abs() is used, which is a minor concern but not a defect for the intended use case.

Undefined behavior: No pointer arithmetic, no null dereference (assuming pre-conditions are met), no type punning, no out-of-bounds array access. The function reads struct fields directly and through helper functions that internally check for null in debug builds.

Validation: No input validation is present, which is appropriate for this low-level computation function. The caller (m_ui_element__compose_handler__default_non_recursive) is responsible for ensuring valid inputs. The debug-mode null checks in get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager provide a safety net in debug builds.

Side Effects:
No side effects. The function is a pure query: it reads from the hitbox AABB (via the hitbox manager), reads from the UI element, and writes to the four output parameters. It does not mutate any persistent state. The only observable effects are the writes to the output parameters and the return of a pointer to the UI element's ui_tile_span member.
