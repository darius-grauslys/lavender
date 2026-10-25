**Function name:** `PLATFORM_pre_render`
**File of origin:** `core/include/platform.h` (declaration, line 189)

## Semantic

Performs pre-render platform setup at the start of each frame: pumps input events and clears the framebuffer/backbuffer. Called once per frame as the first phase of the render loop, before `manage_game__post_render`, dispatched from `game.c:738` via `manage_game__pre_render`. Documented in `agents/platform_api.md:328` ("Backend pumps input events and clears the screen") and `agents/ARCHITECTURE.md:87` ("backend pumps events, clears screen").

Per `core/include/platform.h:17-19`, this header declares signatures *not* implemented in core; implementations are platform-dependent (provided by a backend such as SDL or nds). Reference implementations:
- SDL (desktop, actively built): `sdl/source/sdl_game.c:55` — `SDL_PumpEvents()` + `SDL_poll_event(p_game)` + `SDL_clear_screen(get_p_PLATFORM_gfx_context_from__game(p_game))`.
- NDS (handheld): `nds/source/nds_game.c:13` — `swiWaitForVBlank()`.
- no_gui stub: `no_gui/source/NOT_IMPL.c:8` (empty body).
- Test stubs: `tests/core/source/PLATFORM.c:184` and `tests/templates/source/PLATFORM.c:184` (empty body).

## Pre-conditions

1. `p_game` (a.k.a. `game`) must be a non-null pointer to a valid `Game`. The SDL implementation dereferences it via `get_p_PLATFORM_gfx_context_from__game(p_game)` (which reads `p_game->gfx_context.p_PLATFORM_gfx_context`) and passes it to `SDL_poll_event`.
2. SDL backend specifically: the platform graphics context must be set up prior to the first call. `p_game->gfx_context.p_PLATFORM_gfx_context` must be non-null and point to a fully initialized `PLATFORM_Gfx_Context`, and the `SDL_Gfx_Sub_Context__wrapper.f_SDL_clear_screen` function pointer must be non-null — both established during `PLATFORM_initialize_game` → `SDL_initialize_gfx_context` (sdl_game.c:39). SDL itself must have been initialized (`SDL_Init` with VIDEO|EVENTS).
3. NDS backend: `p_game` is unused in the body, so no Game precondition is required; VBlank/interrupt hardware is assumed present (provided by the libnds runtime, `<nds.h>` included at nds_game.c:8).
4. no_gui/test stubs: no conditions — the bodies are empty, so any pointer value is harmlessly accepted.

## Post-conditions

1. SDL: the SDL event queue is pumped (`SDL_PumpEvents`) and at most one pending event is consumed/dispatched (`SDL_poll_event` → `SDL_PollEvent`). The framebuffer/backbuffer is cleared via the backend's `f_SDL_clear_screen` hook. The Game struct itself is not directly mutated by this function (event handlers invoked via `SDL_poll_event` may, but tracing callee-side effects is out of scope).
2. NDS: the CPU blocks until the next vertical blank (`swiWaitForVBlank`), synchronizing to the display refresh (a per-frame barrier). No Game state is read or written (`p_game` is unused).
3. Stubs (no_gui, tests): no observable effect; no state is mutated.
4. The per-frame `tick__timer_u32` is NOT advanced here — that happens in the caller (`loop_timer_u32` at game.c:754, after `PLATFORM_post_render`); the timer is reset between phases in `manage_game__post_render` (game.c:745), not here.

## Correctness Verdict

Correct

## Semantic Alignment

The SDL implementation exactly fulfills the documented semantic intent: it pumps SDL input events, polls/dispatches one, and clears the screen — precisely "backend pumps input events and clears the screen" (`platform_api.md:328`, `ARCHITECTURE.md:87`). The NDS implementation fulfills the per-frame sync intent for that platform: `swiWaitForVBlank` is the NDS-correct equivalent of a pre-render barrier (wait for the previous frame's display refresh before rendering the next). The no_gui/test stubs are intentionally no-ops for non-rendered builds.

Lavender-specific note (Initialization ≠ RAII): The function name contains no "init"/"initialize"/"reset", so it is **not** a Lavender-style pool-cleanup function. It is a per-frame platform shim and performs no allocation or resource setup (not RAII). The graphics context it depends on is established during `PLATFORM_initialize_game`, which *is* Lavender-style initialization (a pointer assignment `p_game->gfx_context.p_PLATFORM_gfx_context = &__SDL_Gfx_Context`, not resource acquisition).

## Implementation Correctness

- Type compatibility (SDL): `p_game` is declared `Game *` and matches the declaration `void PLATFORM_pre_render(Game *)`. `get_p_PLATFORM_gfx_context_from__game(Game *p_game)` returns `PLATFORM_Gfx_Context *` (game.h:270, reading `p_game->gfx_context.p_PLATFORM_gfx_context`). `SDL_clear_screen` is declared `void SDL_clear_screen(PLATFORM_Gfx_Context *)` (sdl_gfx_context.c:268). Exact type match end-to-end — no implicit conversions or truncation. `SDL_poll_event` (sdl_event.c:12) returns void and `SDL_PumpEvents()` is the SDL2 C API (included via `<SDL2/SDL_events.h>` at sdl_game.c:4/17), both correctly invoked.
- Undefined behavior (SDL): No null-checks on `p_game` or the returned gfx context. If `p_game` is null, `get_p_PLATFORM_gfx_context_from__game` dereferences null (UB). If `p_game->gfx_context.p_PLATFORM_gfx_context` is null, the `->` chain and `SDL_clear_screen` are UB; if the `f_SDL_clear_screen` function pointer is null (gfx sub-context uninitialized), the indirect call inside `SDL_clear_screen` (sdl_gfx_context.c:272) is a null function-pointer call (UB). This matches the Lavender convention for low-level platform shims — `PLATFORM_post_render` (sdl_game.c:62), `PLATFORM_close_game` (sdl_game.c:49), and `get_p_PLATFORM_gfx_context_from__game` itself all rely on the caller guaranteeing a valid, initialized `Game *`. The sole caller, `manage_game__pre_render` (game.c:737), is only entered after `PLATFORM_initialize_game` has run, so the invariant holds in the normal game loop. No defensive validation is warranted for this role.
- Undefined behavior (NDS): `p_game` is unused in the body, so there is no null-dereference risk from the Game pointer; no struct member access occurs (unlike `PLATFORM_post_render`, which has NDS member-name drift against the current `Game_t` — this function is not affected). `swiWaitForVBlank()` is a valid libnds call (declared via `<nds.h>`). No UB.
- Undefined behavior (stubs): empty bodies introduce no UB.
- Validation: Appropriate for the role — a low-level platform shim called once per frame from the pre-render phase with an already-initialized Game. Caller responsibility; consistent with sibling functions.
- Minor note (not a defect): the SDL body calls `SDL_PumpEvents()` immediately before `SDL_poll_event`, whose internal `SDL_PollEvent` pumps the event queue anyway. This is harmless redundancy, not a correctness bug.

## Side Effects

1. SDL: Mutates SDL's internal event-queue state — `SDL_PumpEvents` advances/pumps the queue, and `SDL_poll_event` consumes at most one pending event and dispatches it to its registered handler (which may, in turn, mutate Game or gfx-context state, but tracing callees is out of scope). `SDL_clear_screen` clears the framebuffer/backbuffer. The Game struct is not directly mutated by `PLATFORM_pre_render` itself.
2. NDS: Blocks the CPU until the next vertical blank (frame sync) — a hardware wait, not a sleep. No Game or memory state is mutated (`p_game` is unused).
3. Stubs (no_gui, tests): No side effects — empty function body.
