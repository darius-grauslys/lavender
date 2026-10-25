PLATFORM_compose_world — core/include/platform.h (decl, line 248); impl reviewed: sdl/source/rendering/sdl_render_world.c (line 9)

Composes world tiles and local player data into a graphics window buffer via the platform-specific compose kernel.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game whose gfx_context and gfx_context.p_PLATFORM_gfx_context are valid (the platform gfx context must already be set up).
2. p_gfx_window must be a non-null pointer to an initialized Graphics_Window into which the world is composed.
3. On the SDL backend the delegate f_SDL_compose_world (SDL_Gfx_Sub_Context__Wrapper.f_SDL_compose_world, sdl_defines.h:266) must have been populated during gfx-context initialization; if it is NULL the function logs an error and returns without composing.

Post-conditions:
1. Returns void. When the delegate pointer is non-NULL, the graphics window buffer is composed (mutated) by the delegate.
2. If the delegate pointer is NULL, no composition occurs; a debug_error is emitted and the function returns early.

Correctness Verdict: Correct

Semantic Alignment:
The header doc comment (platform.h:244-247) specifies composing the window buffer "via tiles and local player world data" (feature LAVENDER_FEATURE__GFX_WINDOW__COMPOSE_WORLD). The SDL implementation is the platform-abstraction dispatch the contract requires: it resolves the registered f_SDL_compose_world delegate from the gfx context and invokes it with (p_game, p_graphics_window), which performs the actual tile/world composition. The implementation fulfills the semantic intent with no structural mismatch.

Implementation Correctness:
- Type compatibility: exact. The local f_SDL_Compose_World variable matches the field SDL_Gfx_Sub_Context__Wrapper.f_SDL_compose_world (sdl_defines.h:266) and the typedef (sdl_defines.h:184: void (*)(Game *, Graphics_Window *)). The call passes p_game (Game *) and p_graphics_window (Graphics_Window *) exactly. No implicit conversions or truncation.
- Undefined behavior: none in the reviewed path. The delegate is checked via `if (!f_SDL_compose_world)` before being invoked, so a NULL function pointer is never called. The field .f_SDL_compose_world is reached through a struct member (SDL_gfx_sub_context__wrapper), not a pointer, so no extra dereference occurs there.
  - Note: p_game is dereferenced unconditionally via get_p_gfx_context_from__game(p_game) -> &p_game->gfx_context (game.h:265); a NULL p_game would be UB. p_PLATFORM_gfx_context is also dereferenced (->SDL_gfx_sub_context__wrapper) without a null check. For a low-level PLATFORM_* dispatch function this is a precondition (gfx context initialized), consistent with the engine's convention that validation of p_game / gfx context is the caller's responsibility (see initialize_audio_effect review). No validation is required within this function for its role.
- Validation scope: the SDL signature (Game *, Graphics_Window *) matches the header (platform.h:248-250) and the test stub (tests/core/source/PLATFORM.c:282). Known discrepancy (out of scope, already documented in agents/platform_api.md:710-711): the no_gui stub in NOT_IMPL.c:11 has a different, expanded signature (adds Local_Space_Manager *, Texture *, Quantity__u32, f_Tile_Render_Kernel) — a backend-specific stub, not the SDL implementation under review.

Side Effects:
Invokes the registered f_SDL_compose_world delegate with (p_game, p_gfx_window), which composes world tiles + local player data into the graphics window buffer (the buffer is mutated). If the delegate pointer is NULL, the only observable effect is a debug_error log message and an early return (no composition). The function performs no other state mutation itself; the actual tile rendering is performed by the delegate (callee site, out of scope to trace).
