manage_game__pre_render — core/source/game.c, lines 737-739

Thin backend forwarder for the per-frame pre-render phase.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game object.
2. The Game's platform context must have been set up (via initialize_game / PLATFORM_initialize_game) so the backend's PLATFORM_pre_render can access its graphics/input sub-contexts.
3. A backend implementation of PLATFORM_pre_render (sdl/nds/no_gui) must be linked at compile time.
4. No other parameter constraints — p_game is the sole argument.

Post-conditions:
1. Return value: void (no return value).
2. p_game is forwarded unchanged to PLATFORM_pre_render; on the SDL backend this pumps SDL events and clears the framebuffer, and on the NDS backend this waits for VBlank.
3. After return, the framebuffer is in a cleared, ready state for the upcoming render pass (backend-dependent).

Correctness Verdict: Correct

Semantic Alignment:
The function's name and call-site (the first phase of the per-frame loop, immediately before manage_game__post_render) establish its intent: perform pre-render platform setup at the start of each frame. It forwards exactly one call — PLATFORM_pre_render(p_game) — passing the identical pointer it received. There is no semantic drift: it neither reads nor writes any Game field, performs no computation, and does no reordering. It is a thin passthrough that fulfills its intent of handing control to the backend's pre-render hook.

Implementation Correctness:
- Type compatibility — p_game is declared Game * and PLATFORM_pre_render (declared in platform.h:189) expects Game *. The types match exactly; no implicit conversion or truncation.
- Undefined behavior — None. There is no pointer arithmetic, no array/subscript access, no type punning. The function performs no dereference of its own; the only dereference occurs inside the backend callee, which is the backend's responsibility.
- Validation — Appropriate for a low-level per-frame coordinator. The function intentionally performs no null-check on p_game; this matches the convention followed by the sibling per-frame coordinator manage_game__post_render (game.c:741), which likewise assumes a valid p_game without defense. Validity of p_game is the caller's (the scene loop owner's) contract, as documented by ARCHITECTURE.md and enforced at the enter-handler call sites (e.g., scene__main.c:28). Adding a check here would be inconsistent with the surrounding per-frame functions and unnecessary given the caller owns the invariant.

Side Effects:
No direct side effects of its own — manage_game__pre_render does not read or write any Game fields. Its entire observable effect is the delegation to PLATFORM_pre_render(p_game), whose side effects are backend-specific: on SDL this pumps SDL events (SDL_PumpEvents/SDL_poll_event) and clears the screen (SDL_clear_screen); on NDS this blocks until VBlank (swiWaitForVBlank). Tracing callee internals beyond this is out of scope.
