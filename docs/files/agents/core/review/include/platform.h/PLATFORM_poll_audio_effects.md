PLATFORM_poll_audio_effects — core/include/platform.h (declared line 55)

Platform-abstracted: the core header declares the signature with no implementation in core/source (consistent with the documented design that PLATFORM_* functions are backend-supplied). The only functional implementation is the NDS backend (`nds/source/audio/nds_audio.c:244`); the SDL (`sdl/source/TMP.c:37`), no_gui (`no_gui/source/NOT_IMPL.c:68`), and test (`tests/core/source/PLATFORM.c:310`) backends ship empty not-implemented stubs.

## Semantic

Polls the per-frame audio lifecycle of every effect in the platform audio context's fixed-size effect pool: decrements each effect's duration timer, and on timer completion either releases the platform sound handle and marks the effect inactive (if `AUDIO_FLAG__RELEASE_ON_COMPLETE` is set) or resets the timer to loop (otherwise, with sound re-trigger unimplemented — see TODO). Called once per frame from `manage_game__post_render` (game.c:748). This is the sole time audio is ticked.

## Pre-conditions

1. `p_PLATFORM_audio_context` must be non-null and point to a valid, initialized `PLATFORM_Audio_Context`. The NDS implementation dereferences it on every iteration with no null-guard (caller responsibility per Lavender convention). Note: `get_p_PLATFORM_audio_context_from__game` (game.h:259) returns `p_game->p_PLATFORM_audio_context`, which may be null if audio was never wired up (per `manage_game__post_render.md` review); this is left unguarded and is a latent concern if the backend does not tolerate null.
2. On the NDS backend, the context's `audio_effects[]` array (size `NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS` = 16, nds_defines.h:263/269) and `maxmod_sfx_handles[]` array (matching size) must exist and be properly initialized. For any effect with `AUDIO_FLAG__RELEASE_ON_COMPLETE` set and an elapsed timer, `p_audio_instance_handle` must point to a valid, in-range `mm_sfxhand` slot within `maxmod_sfx_handles` (otherwise `mmEffectRelease` receives an invalid handle).
3. The caller is expected to invoke this once per frame from the game's post-render phase (manage_game__post_render, game.c:748). Not a hard requirement but part of the calling convention; less frequent invocation would delay timer-driven completion/release.

## Post-conditions

1. Each `Audio_Effect` in the context's pool has its `timer_for__audio` polled (decremented by one step if `remaining__u32` > 0; clamped at 0; stays at 0 once elapsed due to short-circuit in `is_timer_u32__elapsed`).
2. For any effect whose timer elapsed (`poll_timer_u32` returned true):
   - If `AUDIO_FLAG__RELEASE_ON_COMPLETE` is set: `mmEffectRelease()` is called on the effect's handle, and `AUDIO_FLAG__IS_ACTIVE` is cleared in `audio_flags__u8` via `set_audio_as__inactive`. **See critical bug note below.**
   - If not set: the timer is reset to `start__u32` (loop path; the sound is NOT re-triggered via `mmEffect` — the `// TODO: support looping` comment confirms this is incomplete).
3. `the_kind_of__audio_effect` and `p_audio_instance_handle` (the pointer value) are not modified by this function.
4. No return value is provided (void).
5. On stub backends (SDL, no_gui, test): no effects are modified — intentional no-op.

## Correctness Verdict

**Incorrect**

## Semantic Alignment

The NDS implementation fulfills the broad semantic intent of per-frame timer polling with completion/release handling: it scans the fixed pool, decrements each timer, and on completion either releases the effect or resets the timer for looping. However, the implementation contains a critical bug that causes repeated, unintended release of already-released effects, violating the intended "release once on completion" semantics. The stub backends (SDL, no_gui, test) are intentional no-ops, consistent with the documented platform-abstracted design.

**Critical bug — repeated double-release of already-released handles:**

`PLATFORM_poll_audio_effects` has no `is_audio__active` guard — it processes ALL 16 pool slots every frame regardless of active state. After an effect with `RELEASE_ON_COMPLETE` (set by `play_audio_effect_and__forget`) is released (timer elapses, `mmEffectRelease` called, `IS_ACTIVE` cleared), three facts combine to cause a recurring double-release:

1. `RELEASE_ON_COMPLETE` is **never cleared** after release. `NDS_release_p_audio_effect` (nds_audio.c:30-35) calls `mmEffectRelease` and `set_audio_as__inactive` (which only clears `IS_ACTIVE`), but never calls `set_audio_as__not_releasing_on_completion`. Confirmed: `set_audio_as__not_releasing_on_completion` (audio_effect.h:72) is defined but **never called** in any audio code path (only in the unit test `test_suite_audio_audio_effect.c:237`).

2. After release, `timer_for__audio.remaining__u32` stays at 0. `poll_timer_u32` returns true whenever `remaining == 0` (via `is_timer_u32__elapsed` short-circuit, which does not decrement), so it returns true on every subsequent frame for the released slot.

3. Since `RELEASE_ON_COMPLETE` is still set, `is_audio__released_on_completion` returns true again, and `NDS_release_p_audio_effect` is called once more — calling `mmEffectRelease` on an already-released handle. The handle value is never zeroed or invalidated after release, so the stale handle is re-passed every frame.

This manifests in **any game session where at least one sound effect plays** (any effect created via `play_audio_effect_and__forget`, which OR's in `RELEASE_ON_COMPLETE` at audio_effect.c:33). The released slot is not re-allocated until a new sound plays and claims it via `PLATFORM_allocate_audio_effect`, so the double-release recurs every frame in between. The root cause is the missing `is_audio__active` check at the top of the loop (skip inactive slots), which would both prevent the double-release and avoid unnecessary timer polling of inactive slots.

The "looping" path (else branch, reset timer without re-triggering `mmEffect`) is a known incompleteness (acknowledged by `// TODO: support looping`), not a bug per se — but it means effects without `RELEASE_ON_COMPLETE` do not actually loop audibly.

**Lavender-specific note (initialization != RAII):** This function is not an initialization function — it is a per-frame update/poll function. The release it performs is the destruction/cleanup side of the audio effect lifecycle (returning slots to the pool), which is the inverse of RAII and consistent with Lavender's pool-based model. The double-release bug undermines this cleanup-by-pool-recycling design.

## Implementation Correctness

- **Types:** Loop index `Index__u8` vs loop bound `NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS` (16) — no overflow (16 fits in u8). `Audio_Effect *` from `NDS_get_p_audio_effect_by__index_in__audio_context` correctly indexes `audio_effects[index]` within [0,16) — in bounds. Parameter `PLATFORM_Audio_Context *` matches the declaration exactly. The cast of `p_audio_instance_handle` (void *) to `mm_sfxhand*` before `mmEffectRelease` is the intended opaque-handle usage (the handle was set to `&maxmod_sfx_handles[index]` during `PLATFORM_initialize_audio`, a genuine `mm_sfxhand`). No implicit conversions or truncation.
- **Undefined behavior:** The double-release of `mmEffectRelease` on an already-released handle (see Semantic Alignment) constitutes undefined behavior — the maxmod API is called on a channel handle whose channel has already been freed, and the handle value is never zeroed. This is a use-after-free / double-free pattern. Additionally, `p_PLATFORM_audio_context` may be null (if audio was never wired up) and the NDS implementation dereferences it without a guard — though per the Lavender convention, pointer validity is the caller's responsibility.
- **Validation:** No null-check on `p_PLATFORM_audio_context` (accepted per Lavender low-level-backend convention; caller must pass a valid context). No `is_audio__active` check to skip inactive slots — this is the root cause of the double-release bug. No validation of `p_audio_instance_handle` before passing to `mmEffectRelease`. Loop bounds match array dimensions exactly (no off-by-one, no OOB).
- **Loop correctness:** The loop `for (Index__u8 i = 0; i < NDS_MAX_QUANTITY_OF__AUDIO_EFFECTS; i++)` covers exactly the 16-element `audio_effects[]` array — all slots are visited, none are skipped, none are accessed out of bounds.

## Side Effects

1. NDS backend: decrements each effect's `timer_for__audio.remaining__u32` by one step (if > 0); leaves it at 0 once elapsed.
2. NDS backend: for any elapsed effect with `RELEASE_ON_COMPLETE` set, calls `mmEffectRelease()` on the effect's active channel handle and clears `AUDIO_FLAG__IS_ACTIVE` — but re-enters this path every subsequent frame (see bug note in Semantic Alignment).
3. NDS backend: for any elapsed effect without `RELEASE_ON_COMPLETE`, resets `timer_for__audio.remaining__u32` to `start__u32` (loop path; sound not re-triggered via `mmEffect`).
4. Stub backends (SDL, no_gui, test): no side effects — intentional no-op.
5. Does not modify `the_kind_of__audio_effect`, `p_audio_instance_handle` (the pointer value), or `audio_flags__u8` beyond clearing `IS_ACTIVE` on the release path.
