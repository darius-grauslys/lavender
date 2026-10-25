PLATFORM_render_gfx_window — core/include/platform.h, line 264 (implementation: sdl/source/rendering/sdl_gfx_window.c, line 128)

Renders the graphics window's composed buffer to the display via the active graphics backend (e.g. OpenGL).

Pre-conditions:
1. p_game must be a non-null pointer to a Game object whose gfx context has been initialized with a backend (the f_SDL_render_gfx_window function pointer must be set; see sdl_gfx_context.c:114).
2. p_gfx_window must be a non-null pointer to a Graphics_Window object whose PLATFORM_Graphics_Window backing store is allocated and whose texture is valid.
3. The graphics backend (SDL/OpenGL) must be initialized and an active rendering context must be current.
4. No initialization/RAII is performed — this is a render dispatch, not resource setup.

Post-conditions:
1. The graphics window's texture is drawn as a quad into the current framebuffer using the graphics_window shader, positioned according to the window's position and the active viewport.
2. If the window is disabled (GRAPHICS_WINDOW__FLAG__IS_ENABLED unset), the function returns early with no rendering done.
3. If the shader lookup fails, the window is marked disabled and no draw occurs.
4. Returns void.

Correctness Verdict: Correct

Semantic Alignment:
The function fulfills its semantic intent of rendering a graphics window to the display. The implementation forms a correct dispatch chain: PLATFORM_render_gfx_window (sdl_gfx_window.c:128) delegates to SDL_render_gfx_window (sdl_gfx_window.c:80), which fetches the backend function pointer (f_SDL_render_gfx_window, typed as f_SDL_Render_Gfx_Window in sdl_defines.h:128) from the SDL_gfx_sub_context__wrapper and dispatches it. During gfx context initialization (sdl_gfx_context.c:114), this pointer is set to GL_render_gfx_window, which performs the actual OpenGL draw call (glDrawElements at gl_gfx_window.c:468). The dispatch correctly forwards (p_game, p_gfx_window) at every level.

Implementation Correctness:
Type compatibility: The function signature `void PLATFORM_render_gfx_window(Game *p_game, Graphics_Window *p_gfx_window)` matches exactly at every dispatch level — the typedef f_SDL_Render_Gfx_Window (sdl_defines.h:128-130) and the Graphics_Window struct member f_PLATFORM_render_gfx_window (defines.h:2478-2492) both use the identical (Game*, Graphics_Window*) signature. No implicit conversions or truncation occur.
Undefined behavior: None in the SDL dispatch path. SDL_render_gfx_window dereferences the gfx context chain (get_p_gfx_context_from__game -> p_PLATFORM_gfx_context -> SDL_gfx_sub_context__wrapper) — these are assumed valid per pre-conditions. The GL backend's GL_render_gfx_window guards against a null shader (gl_gfx_window.c:393) and null-disabled window (gl_gfx_window.c:380) before issuing GL calls.
Validation: SDL_render_gfx_window validates the function pointer in debug builds (#ifndef NDEBUG, sdl_gfx_window.c:91-97) and calls debug_abort if null. This is appropriate for catching uninitialized backends. GL_render_gfx_window validates both window-enabled state and shader presence before drawing.

Note on no-gui build: The stub in no_gui/source/NOT_IMPL.c:50 declares `PLATFORM_render_gfx_window(Gfx_Context *p_gfx_context, Graphics_Window *p_gfx_window)` — a signature mismatch with the platform.h declaration (which takes `Game *p_game`). NOT_IMPL.c does not include platform.h, so the compiler does not catch this. Since both parameters are pointers and the stub is a no-op that ignores its arguments, the ABI is coincidentally compatible and no runtime fault occurs — but the mismatch is a latent type-safety bug that should be corrected to match the declared interface.

Side Effects:
Side effects depend on the active backend:
- SDL/OpenGL backend (GL_render_gfx_window): issues OpenGL draw calls (glDrawElements) that modify GPU state — the bound shader, active texture unit, vertex array, and framebuffer contents are mutated. The window may be marked disabled if its shader is unavailable. GPU state (current shader, texture, vertex buffer) is altered as a side effect of the draw.
- No-gui stub: no side effects (no-op).
