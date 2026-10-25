manage_game__post_render — core/source/game.c, lines 741-755

Per-frame post-render phase that polls input, resets the game tick timer, polls the process manager, polls audio effects, presents the frame via the platform backend, and advances the loop tick timer.

Pre-conditions:
1. `p_game` must be a non-null pointer to a valid, writable `Game` struct (defined at `core/include/defines.h:2595`). No in-function null check is performed, so validity is the caller's responsibility.
2. The `Game` struct must have been initialized via `initialize_game()` (`game.c:91`), which `memset`s the struct to zero and then sets up embedded managers (gfx context, scene manager, process manager, sort list manager, etc.). This is Lavender-style initialization (cleaning up to initial conditions, not RAII resource acquisition).
3. The embedded sub-objects accessed by the called functions must be valid: the `Input` (or local-client input when `max_quantity_of__clients` is nonzero), the `Process_Manager`, the `PLATFORM_Audio_Context` (passed to `PLATFORM_poll_audio_effects`), and the gfx context used by `PLATFORM_post_render`.
4. `p_game->tick__timer_u32` must be a valid `Timer__u32` (set up by `initialize_game`'s zero-init, which leaves `start__u32` at 0 so the timer is inert until configured by caller code).

Post-conditions:
1. Input is polled: `poll_input` has read the latest input device state into the active `Input` struct (either `&p_game->input` or the local client's input).
2. The game tick timer accumulators are reset: `reset__game_tick_timer` aligns `tick_accumilator__u32F20` down and zeroes `time_elapsed__u32F20`.
3. The process manager is polled: `poll_process_manager` has advanced/retired any runnable processes.
4. Audio effects are polled via `PLATFORM_poll_audio_effects` (backend state mutated).
5. The frame is presented via `PLATFORM_post_render` (backbuffer swap / flush).
6. `p_game->tick__timer_u32.remaining__u32` is decremented by `loop_timer_u32` (wrapping back to `start__u32` when it reaches 0).

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully realizes the documented per-frame post-render phase. The `agents/core/modules/engine.md` checkpoint states that `manage_game__post_render` runs "poll_input → reset_tick_timer → process cleanup pass → PLATFORM_poll_audio_effects → PLATFORM_post_render → loop tick timer." The function body executes exactly this sequence: `poll_input` → `reset__game_tick_timer` → `poll_process_manager` → `PLATFORM_poll_audio_effects` → `PLATFORM_post_render` → `loop_timer_u32(&p_game->tick__timer_u32)`. The ordering is intentional and correct: input is sampled before timer/reset state is disturbed, process cleanup occurs before the frame is presented, and the loop timer is advanced last. The commented-out `PLATFORM_update_ui(p_game);` gated behind a `#warning TODO: resolve update_ui` is a known incompleteness but does not constitute a semantic bug in the implemented code; the UI-update step is simply absent from this phase and presumably handled elsewhere.

Implementation Correctness:
Type compatibility — every argument matches its target parameter type exactly:
- `poll_input(Game*, Input*)`: `p_game` is `Game*`; `get_p_input_from__game` returns `Input*`. Exact match.
- `reset__game_tick_timer(Game*)`: `p_game` is `Game*`. Exact match.
- `poll_process_manager(Process_Manager*, Game*)`: `get_p_process_manager_from__game` returns `Process_Manager*`; `p_game` is `Game*`. Exact match.
- `PLATFORM_poll_audio_effects(PLATFORM_Audio_Context*)`: `get_p_PLATFORM_audio_context_from__game` returns `PLATFORM_Audio_Context*`. Exact match.
- `PLATFORM_post_render(Game*)`: `p_game` is `Game*`. Exact match.
- `loop_timer_u32(Timer__u32*)`: `&p_game->tick__timer_u32` is `Timer__u32*`. Exact match.
No implicit conversions or truncation are present.

Undefined behavior — none in the implemented code:
- All pointers ultimately derive from `p_game` (required valid by pre-condition) and its embedded members (set up by `initialize_game`).
- `get_p_input_from__game` performs a null-safe branch on `max_quantity_of__clients` and returns one of two valid `&`-of-member pointers; no stray dereference.
- `get_p_PLATFORM_audio_context_from__game` returns the raw pointer (`p_game->p_PLATFORM_audio_context`), which may be null if audio was never wired up; this is passed to `PLATFORM_poll_audio_effects` and left unguarded — a latent concern if the backend does not tolerate null, but it is outside this function's scope and the Lavender convention is that platform pointers are bound during `PLATFORM_initialize_game` before this frame loop runs.
- No pointer arithmetic, no type punning, no array/heap access, no out-of-bounds access anywhere in the body.

Validation — appropriate for a low-level per-frame coordinator. The function mirrors `manage_game__pre_render` (`game.c:737`) in performing no null check on `p_game`; validity is the caller's (scene-loop owner's) contract. The accessor inlines do their own safe branching for the input selection. No additional defensive checks are warranted given the function's role.

Side Effects:
Mutates `p_game` and its embedded sub-objects:
- `poll_input` writes latest input state into the active `Input` struct.
- `reset__game_tick_timer` mutates `p_game->tick_accumilator__u32F20` and `p_game->time_elapsed__u32F20`.
- `poll_process_manager` mutates the `Process_Manager` (advancing/retiring processes) and may recurse into `Game`-owned services (out of scope to trace here, but the immediate effect is process-manager state change).
- `PLATFORM_poll_audio_effects` mutates backend audio state.
- `PLATFORM_post_render` presents the backbuffer (backend frame swap / flush).
- `loop_timer_u32` mutates `p_game->tick__timer_u32.remaining__u32` (decrements, wrapping to `start__u32` at zero).
The compile-time `#warning TODO: resolve update_ui` and commented-out `PLATFORM_update_ui` line is a source-level directive (emits a compiler warning); it has no runtime effect.
