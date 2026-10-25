PLATFORM_compose_ui_span_in__gfx_window — core/include/platform.h

Renders a rectangular span of UI tiles (previously generated into the gfx window's in-memory ui_tile_map) onto the gfx window's framebuffer at the tile-grid position (index_x__u32, index_y__u32), covering width_of__ui_tile_span x height_of__ui_tile_span tiles.

This is a platform-dependent contract: the declaration lives in core/include/platform.h; the implementation is supplied by a backend. The SDL backend (sdl/source/rendering/sdl_gfx_window.c) is a thin wrapper that delegates via a function pointer to the OpenGL backend GL_compose_ui_span_in__gfx_window (sdl/source/rendering/opengl/gl_gfx_window.c), which is the only complete implementation. The test backends (tests/core/source/PLATFORM.c, tests/templates/source/PLATFORM.c) are intentional empty no-ops (test doubles), not real implementations. (This is why a source lookup restricted to core finds no implementation.)

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game with a gfx context available (get_p_PLATFORM_gfx_context_from__game(p_game) must succeed).
2. p_gfx_window must be a non-null pointer to a valid, enabled Graphics_Window (the implementation early-returns if the window is not enabled).
3. The caller must have already generated the desired span into p_gfx_window->ui_tile_map__wrapper.p_ui_tile_data (via generate_ui_span_in__ui_tile_map / get_ui_tile_span_of__ui_element) using the same width, height, index_x__u32, and index_y__u32 values. The function reads this buffer; it does not regenerate the span.
4. The gfx window must have an associated framebuffer (p_PLATFORM_gfx_window->p_SDL_graphics_window__data) bound to its framebuffer slot, plus a UI tilesheet texture and a passthrough shader available on the platform gfx context. If any is missing the implementation disables the window and returns.
5. width_of__ui_tile_span and height_of__ui_tile_span are logical span dimensions in tiles (>= 0; 0 renders nothing).
6. index_x__u32 and index_y__u32 are tile-grid coordinates of the span's top-left corner; they need not be < the map dimensions (out-of-range tiles are skipped at runtime).
7. Not an "init"/"reset" function (it is a compose/render step, not Lavender-style pool cleanup), so the Initialization!=RAII guidance does not apply.

Post-conditions:
1. The sub-region [index_x__u32 .. index_x__u32+width_of__ui_tile_span) x [index_y__u32 .. index_y__u32+height_of__ui_tile_span) of p_gfx_window's framebuffer has the span composited from the tile map, reading each UI_Tile_Raw at (x + (width_of__ui_tile_map-1-y)*width_of__ui_tile_map), skipping empty (0) tiles, and rendering one tile-pixel square per tile.
2. The GPU framebuffer/texture/shader/viewport state that this function pushes is restored before return (framebuffer and viewport stacks are popped; the previously active shader/texture may be left as-is by the backend).
3. Returns void; no value is returned.
4. On the active path (size_of__ui_tile_in__8x8_tiles__u8 == 1, square tile maps), generation and render index the same cells, so the rendered region exactly matches the span written by generate_ui_span_in__ui_tile_map.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent on the active/exercised code path. The header contract is sound and the calling site in ui_element.c (m_ui_element__compose_handler__default, core/source/ui/ui_element.c:512-537) feeds identical width/height/index_x/index_y to both generate_ui_span_in__ui_tile_map (which populates the tile map) and PLATFORM_compose_ui_span_in__gfx_window (which renders it), so the two halves are meant to be mirrors; they agree for the only configuration actually produced today (size == 1, square 8x8/16x16/32x32 tile maps).
Known latent misalignment (NOT on any current call path): the OpenGL backend iterates index_y/index_x by height/width alone, omitting the size_of__ui_tile_in__8x8_tiles__u8 multiplier that generate_ui_span_in__ui_tile_map applies (ui_tile_map.c:168/184). Because initialize_ui_tile_span__with_ui_tile_size has no call sites and the default constructors set size == 1, every span currently has size 1 and the mismatch is dormant. If a size>1 span were ever produced, the renderer would draw only the top-left width x height block instead of the full width*size x height*size block.

Implementation Correctness:
- Type compatibility: parameter types match their use exactly (Game*, Graphics_Window*, Quantity__u32 for dimensions, Index__u32 for positions; both typedef uint32_t). The SDL wrapper forwards them unchanged to the GL backend; no implicit conversions or truncation at the contract boundary.
- Undefined behavior: no pointer arithmetic, no null dereference on a valid call (p_GAME/p_gfx_window preconditions + the enable/resource guards), no type punning, no out-of-bounds access on the active path. The x/y bounds checks (gl_gfx_window.c:339-340) and the empty-tile skip (348-349) prevent out-of-bounds reads in the render loop.
- Validation: appropriate as-is. Null/enabled/resource-missing validation belongs in this platform function (the GL impl does it) rather than pushed entirely to callers; it disables a broken window rather than crashing. Struct initialization is not performed here (non-init function).
- Latent robustness issues to watch (all dormant on the active path):
  (a) Index__u8 loop variables index_of__y_tile / index_of__x_tile (gl_gfx_window.c:329,335) with uint32 bounds (index_x__u32 + width_of__ui_tile_span). If the sum exceeded 255 the comparison would truncate; today max index (~32) + max span (~32) stays well under 256, so no current overflow. Changing tile maps or span sizes could re-expose this.
  (b) Row index uses width_of__ui_tile_map - 1 - index_of__y_tile (gl_gfx_window.c:345-347), whereas generate_ui_span_in__ui_tile_map writes row height_of__ui_tile_map - 1 - index_of__y_tile (ui_tile_map.c:172-176). These coincide only for square maps (the configured SMALL/MEDIUM/LARGE defaults are square: 8x8, 16x16, 32x32). The call that would set a non-square utilized size (set_ui_tile_map__wrapper__utilized_size in core/source/rendering/graphics_window.c:240) is inside a commented-out block, so non-square maps are not currently produced; the discrepancy is latent.
  (c) Missing size_of__ui_tile_in__8x8_tiles__u8 multiplier (described above) is dormant only because no span uses size > 1.

Side Effects:
Mutates the gfx window's GPU framebuffer (its back/render target) by rendering the UI tile span as textured quad(s) into per-tile viewports. It also mutates backend GPU state during execution — binding the window's framebuffer (push), binding the UI tilesheet texture and passthrough shader, using the unit-square vertex object, and pushing/popping the viewport stack — and restores the framebuffer/viewport stack before returning. Additionally, as an error-recovery side effect, it may call set_graphics_window_as__disabled(p_gfx_window) when the window is not enabled or when a required resource (framebuffer/shader/tilesheet) is missing. It does not mutate the tile-map data itself (read-only) and does not mutate the Game struct.
