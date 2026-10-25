PLATFORM_close_game — core/include/platform.h, line 187

Implemented per-backend: SDL ( sdl/source/sdl_game.c:49-53 ), no_gui ( no_gui/source/no_gui_game.c:19 ), test stub ( tests/core/source/PLATFORM.c:299 ). Not defined on the NDS backend (per agents/platform_api.md).

Tears down platform-level resources acquired during `PLATFORM_initialize_game`: disposes the graphics context (which destroys the window and frees the GL sub-context) and shuts down SDL subsystems. Called from `main.c:11` after the game loop exits. This is a platform-dependent function — the header (platform.h lines 13-19) explicitly states it is "NOT implemented in core."

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid `Game` object. The SDL implementation dereferences it immediately via `get_p_PLATFORM_gfx_context_from__game(p_game)` (which reads `p_game->gfx_context.p_PLATFORM_gfx_context` at game.h:271) and never checks for null; a null pointer is undefined behavior.
2. `p_game->gfx_context.p_PLATFORM_gfx_context` must be a valid, initialized `PLATFORM_Gfx_Context *` that was set up by `PLATFORM_initialize_game` (sdl_game.c:34-35 sets it to `&__SDL_Gfx_Context`). A null gfx context pointer would cause `SDL_dispose_gfx_context` to dereference null (see sdl_gfx_context.c:236-239) — undefined behavior.
3. SDL backend only: the SDL gfx context must have been initialized (window created, GL sub-context allocated) by `SDL_initialize_gfx_context` so that `SDL_dispose_gfx_context` can safely destroy the window and free the sub-context.
4. No validation is performed (consistent with the Lavender convention for low-level platform shims — see PLATFORM_initialize_game, PLATFORM_pre_render, PLATFORM_post_render reviews). The caller (`main`) is responsible for passing a valid, initialized `Game` instance.

Post-conditions:
1. SDL backend: the SDL window is destroyed and the GL graphics sub-context is freed (`SDL_dispose_gfx_context` at sdl_gfx_context.c:233-261); all SDL subsystems previously initialized are shut down (`SDL_Quit()`). The `__SDL_Gfx_Context` static global is zeroed (sdl_gfx_context.c:262+). The `Game` struct fields are left as-is (the pointers still point at the now-disposed statics, but since the program is exiting, this is not a live hazard).
2. no_gui backend: no state changes (empty body, no resources were acquired).
3. Test stub: no state changes (empty body).
4. Returns `void` (no return value / status code).

Correctness Verdict: Correct

Semantic Alignment:
The SDL implementation exactly fulfills the semantic intent: `SDL_dispose_gfx_context` tears down the graphics subsystem (destroy window, free GL sub-context), and `SDL_Quit()` shuts down all initialized SDL subsystems (timer, video, audio, events). This matches the documented behavior in agents/platform_api.md:322 ("disposes gfx context, SDL_Quit"). The no_gui and test stubs are correctly empty — no_gui acquires no graphics resources, so there is nothing to close. No semantic drift is observed.

Lavender-specific note (Initialization ≠ RAII):
This function performs RAII-style platform resource teardown (destroying the SDL window, freeing the GL context, calling `SDL_Quit`), NOT Lavender-style struct initialization or pool cleanup. This is legitimate and expected at the platform-abstraction layer, mirroring the `PLATFORM_initialize_game` review's conclusion that the "initialization ≠ RAII" principle governs core-engine struct lifecycle, not platform resource setup/teardown. The header `platform.h` (lines 13-19) explicitly states these `PLATFORM_*` functions are "NOT implemented in core." The core-engine struct reset (memset to 0 + sub-manager cleanup) happens in the caller `initialize_game`, not here. `PLATFORM_close_game` operates purely at the platform resource level, which is the correct boundary for RAII-style setup/teardown.

Implementation Correctness:
- Type compatibility: `get_p_PLATFORM_gfx_context_from__game` returns `PLATFORM_Gfx_Context *` (game.h:270, reading `p_game->gfx_context.p_PLATFORM_gfx_context`); `SDL_dispose_gfx_context` is declared `void SDL_dispose_gfx_context(PLATFORM_Gfx_Context *)` (sdl_gfx_context.h:14-15). Exact type match end-to-end — no implicit conversions or truncation. The `Game *` parameter matches the declaration `void PLATFORM_close_game(Game *)` (platform.h:187) exactly.
- Undefined behavior: No pointer arithmetic, no type punning, no out-of-bounds access. No null-checks on `p_game` or the returned gfx context — if `p_game` is null, `get_p_PLATFORM_gfx_context_from__game` dereferences null (UB); if `p_game->gfx_context.p_PLATFORM_gfx_context` is null, `SDL_dispose_gfx_context` dereferences null at sdl_gfx_context.c:236-239 (UB). These are documented pre-condition violations, not internal defects, and match the Lavender convention for low-level platform shims (consistent with sibling functions PLATFORM_pre_render, PLATFORM_post_render, PLATFORM_initialize_game). The sole caller `main` (main.c:11) passes a valid `Game *` that was initialized by `PLATFORM_initialize_game`, so the invariant holds in the normal game loop.
- SDL return values: `SDL_Quit()` returns void (no error to check) and `SDL_dispose_gfx_context` returns void. `SDL_DestroyWindow` (called inside `SDL_dispose_gfx_context`) is an SDL C API that does not require a return-value check at this level. No defensive error handling is appropriate for this role, consistent with the platform-backend convention.
- Validation: No parameter validation is performed — appropriate for a low-level platform-backend function per the Lavender convention. The caller is responsible for passing a valid, initialized `Game` instance.

Side Effects:
- SDL backend: disposes the graphics context (`SDL_dispose_gfx_context`, which destroys the SDL window via `SDL_DestroyWindow` and frees the OpenGL graphics sub-context via `free`); zeroes the `__SDL_Gfx_Context` static global. Then shuts down all SDL subsystems (`SDL_Quit`), which is a global teardown affecting all initialized SDL subsystems (timer, video, audio, events) — this is SDL's intended behavior, not a leak or unexpected side effect. The function does not re-initialize or otherwise mutate the `Game` struct; the pointer fields remain pointing at the now-disposed statics (acceptable since the program is exiting).
- no_gui backend: no side effects (empty body, consistent with no_gui acquiring no platform resources).
- Test stub: no side effects (empty body).
- All side effects are direct consequences of this function (it is the top of the platform teardown chain, called from `main.c:11`); no callee-site tracing is needed.
