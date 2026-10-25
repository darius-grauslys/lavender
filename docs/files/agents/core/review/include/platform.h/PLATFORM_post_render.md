PLATFORM_post_render — core/include/platform.h (line 191)

Presents the completed frame to the display at the end of each render tick. The backend composes/swaps windows — i.e. flushes accumulated frame state to the screen. Called from game.c:753 inside `manage_game__post_render`, after `PLATFORM_poll_audio_effects` and before `loop_timer_u32(&p_game->tick__timer_u32)`.

Per agents/platform_api.md:334: "Backend composes and swaps windows." Per agents/core/modules/rendering.md:7/14: the retained-model pipeline builds scene state (windows, sprites, tile maps) during compose/render; this function is the final backend flush/swap. Per agents/ARCHITECTURE.md:106: "backend composes+swaps windows."

Primary/reference implementations (multiple per-backend):
- SDL (desktop, actively built): sdl/source/sdl_game.c:62
- NDS (handheld): nds/source/nds_game.c:17
- no_gui stub: no_gui/source/NOT_IMPL.c:9 (empty)
- Test stubs: tests/core/source/PLATFORM.c:185 and tests/templates/source/PLATFORM.c:185 (empty)

Pre-conditions:
1. `game` (or `p_game`) must be a non-null pointer to a valid, initialized Game. All implementations dereference it.
2. The backend graphics context must have been set up prior to the first call. SDL: `p_game->gfx_context.p_PLATFORM_gfx_context` must be non-null and point to a fully initialized `PLATFORM_Gfx_Context` (set in `PLATFORM_initialize_game` → `p_game->gfx_context.p_PLATFORM_gfx_context = &__SDL_Gfx_Context`; `p_SDL_window` created during `SDL_initialize_gfx_context`). NDS: the equivalent pointer must be set (`nds_main.c:22`, `PLATFORM_main`).
3. For SDL specifically: the OpenGL context and the `SDL_Window` (`p_SDL_window`) must be created and valid; rendering into the backbuffer for the current frame must already be complete.
4. For NDS specifically: the camera (`p_game->world.camera`) and the platform gfx context's background table (`backgrounds__main` with valid `background_index_from__hardware` indices) must be initialized. (See Implementation Correctness re: member-name drift.)
5. For the no_gui/test stubs: no conditions — the function body is empty, so any pointer value is harmlessly accepted.

Post-conditions:
1. SDL: The OpenGL back buffer is swapped to the front buffer via `SDL_GL_SwapWindow`, presenting the rendered frame to the display/window. No other Game state is mutated.
2. NDS: The three background layer scroll registers are updated from the active camera position (`bgSetScroll`), `bgUpdate()` flushes the changes, and `oamUpdate(&oamMain)` / `oamUpdate(&oamSub)` flush sprite OAM for both screens. No Game struct fields are mutated; only hardware display registers are written.
3. Stubs (no_gui, tests): No observable effect; no state is mutated.
4. The `tick__timer_u32` is NOT advanced here — that happens in the caller (`loop_timer_u32` at game.c:754), after `PLATFORM_post_render` returns.

Correctness Verdict: Correct

Semantic Alignment:
The SDL implementation exactly fulfills the semantic intent: `get_p_PLATFORM_gfx_context_from__game(p_game)->p_SDL_window` retrieves the SDL window handle, and `SDL_GL_SwapWindow` performs the back buffer → front buffer swap, which is precisely the "backend frame swap" described in the documentation. No compose/swap step is omitted.

The NDS implementation also fulfills the semantic intent for that platform: NDS hardware renders directly to the display (no double-buffered swap), so the equivalent of "presenting the frame" is updating background scroll registers and flushing OAM via `bgUpdate` / `oamUpdate`. The function updates all three relevant background layers (ground, wall upper, wall lower) driven by the camera, then flushes.

Lavender-specific note (Initialization ≠ RAII): The function name contains no "init"/"initialize"/"reset", so it is not a Lavender-style pool-cleanup function. However, the graphics context it depends on is established during `PLATFORM_initialize_game`, which IS Lavender-style initialization (setting `p_game->gfx_context.p_PLATFORM_gfx_context = &context` — a pointer assignment, not RAII resource acquisition). `PLATFORM_post_render` itself is a per-frame presentation shim, not an initialization function; it performs no allocation or resource setup.

Implementation Correctness:
- Type compatibility (SDL): `get_p_PLATFORM_gfx_context_from__game` returns `PLATFORM_Gfx_Context *` (game.h:270, reads `p_game->gfx_context.p_PLATFORM_gfx_context`). The `->p_SDL_window` member is declared `SDL_Window *` (sdl/include/sdl_defines.h:278). `SDL_GL_SwapWindow` expects `SDL_Window *`. Exact type match end-to-end — no implicit conversions, no truncation.
- Undefined behavior (SDL): No null-check on `game` or the returned gfx context. If `game` is null, `get_p_PLATFORM_gfx_context_from__game` dereferences null (UB). If the gfx context pointer is null (game uninitialized), `->p_SDL_window` is a null dereference (UB). This matches the Lavender convention for low-level platform shims — `PLATFORM_pre_render` (sdl_game.c:55), `PLATFORM_close_game` (sdl_game.c:49), and `get_p_PLATFORM_gfx_context_from__game` itself all rely on the caller guaranteeing a valid, initialized `Game *`. The sole caller, `manage_game__post_render` (game.c:741), is only entered after `PLATFORM_initialize_game` has run, so the invariant holds in the normal game loop. No defensive validation is warranted for this role.
- Undefined behavior (NDS): Member-name drift — the NDS source references `p_game->world.camera` and `p_game->p_PLATFORM_gfx_context`, but the current `Game_t` struct (core/include/defines.h:2546) defines `World *pM_world` and `Gfx_Context gfx_context;` (with `p_PLATFORM_gfx_context` nested as `gfx_context.p_PLATFORM_gfx_context`). These member names do not exist on the current struct, indicating the NDK tree is out of sync with the core Game struct refactor. This is a pre-existing, codebase-wide issue in the NDS sources (also seen in nds/source/scene/scene__game.c:96 and nds/source/nds_main.c:22), not a defect introduced by this function in isolation. Were the NDS toolchain present, these references would fail to compile. The no_gui and test stubs have empty bodies and introduce no UB.
- Validation: Appropriate for the role — a low-level platform shim called once per frame from the engine's post-render phase with an already-initialized Game. Caller responsibility; consistent with sibling functions.

Side Effects:
1. SDL: Swaps the OpenGL back buffer to the front buffer (window-system buffer swap), mutating display/window-system state external to the Game struct. The Game object itself is not mutated.
2. NDS: Writes to hardware display registers (background scroll, OAM) via `bgSetScroll`, `bgUpdate`, `oamUpdate(&oamMain)`, `oamUpdate(&oamSub)`. No Game struct fields are modified.
3. Stubs (no_gui, tests): No side effects — empty function body.
