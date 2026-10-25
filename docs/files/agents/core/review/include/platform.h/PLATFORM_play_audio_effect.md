PLATFORM_play_audio_effect — core/include/platform.h

Triggers the platform's audio engine to begin playback of the audio effect identified by `p_audio_effect`, mapping the effect's kind to a concrete platform sound and starting it via the platform audio API.

Pre-conditions:
1. `p_PLATFORM_audio_context` is non-null and points to a valid, initialized platform audio context (on NDS, contains the pseudo-randomizer and the fixed-capacity sound-handle pool).
2. `p_audio_effect` is non-null and points to a valid, allocated `Audio_Effect` struct obtained from `PLATFORM_allocate_audio_effect` and configured via `set_audio_effect` or `initialize_audio_effect`.
3. `p_audio_effect->the_kind_of__audio_effect` is a recognized `enum Audio_Effect_Kind` value (unsupported kinds cause a debug-error early return on the NDS backend).
4. `p_audio_effect->p_audio_instance_handle` is a valid platform-typed pointer set during initialization (on NDS, points to a `mm_sfxhand` slot within the context's handle pool).
5. `p_audio_effect->audio_flags__u8` has the `AUDIO_FLAG__IS_ACTIVE` bit set (set by `PLATFORM_allocate_audio_effect`); this function does not (re)set it.

Post-conditions:
1. On backends with real implementations (NDS), the platform audio engine has begun playing the sound corresponding to the effect's kind, and the resulting platform sound handle is stored in `p_audio_effect->p_audio_instance_handle`.
2. The `IS_ACTIVE` flag is left set (set during allocation and never cleared by this function).
3. `p_audio_effect->timer_for__audio` is not modified by this function; it was already set by the caller and is decremented by `PLATFORM_poll_audio_effects`.
4. `p_audio_effect->the_kind_of__audio_effect` and `audio_flags__u8` are not modified.
5. On stub backends (SDL no-gui, no_gui, test), no audio playback occurs — the function is an intentional no-op.
6. No return value is provided; playback failure (unsupported kind or platform-level failure such as `mmEffect` returning 0) is not reported to the caller.

Correctness Verdict: Correct

Semantic Alignment:
The implemented behavior matches the semantic intent on the real backend (NDS). The NDS implementation (`nds/source/audio/nds_audio.c:94`) reads `p_audio_effect->the_kind_of__audio_effect`, applies per-kind pseudo-random variation via `p_PLATFORM_audio_context->randomizer`, maps the kind to a concrete `mm_word` sound constant, and calls `mmEffect(sound)` to start playback, storing the resulting handle in `p_audio_effect->p_audio_instance_handle`. This faithfully fulfills "start playing the specified audio effect." The stub backends (SDL `sdl/source/TMP.c:33`, no_gui `no_gui/source/NOT_IMPL.c:64`, test `tests/core/source/PLATFORM.c:306`) are intentionally empty no-ops, documented as unimplemented — a valid pattern for backends where audio is not yet wired up. Note: the review file's "no implementation found" refers to there being no implementation in `core/source`; implementations do exist in the backend directories, which is the documented design (the header states these signatures are platform-dependent and implemented by a backend).

Implementation Correctness:
- Type compatibility — both parameters (`PLATFORM_Audio_Context *`, `Audio_Effect *`) match the caller's arguments exactly with no implicit conversions in the interface.
- Undefined behavior — no null dereference occurs in the core code path because the sole caller, `play_audio_effect_and__forget` (`core/source/audio/audio_effect.c:35`), performs `if (!p_audio_effect) return 0` after allocation before reaching this call. The NDS implementation dereferences both pointers without its own guard, but this is consistent with Lavender's documented convention that pointer validity is the caller's responsibility (the same pattern is used by `set_audio_effect`, an `inline` function in `core/include/audio/audio_effect.h`, and is explicitly accepted there). The cast of `p_audio_effect->p_audio_instance_handle` (a `void *`) to `mm_sfxhand*` is the intended opaque-handle usage, not type punning: the handle was set to `&p_PLATFORM_audio_context->maxmod_sfx_handles[index]` during `PLATFORM_initialize_audio` (`nds/source/audio/nds_audio.c:59`), which is a genuine `mm_sfxhand`. The switch over `the_kind_of__audio_effect` includes a `default` case that logs a debug error and returns early, so the `sound` variable is always assigned before use — no uninitialized reads or out-of-bounds access.
- Validation — no validation is performed inside the function body. The caller validates allocation success. Enum and flag values are supplied directly by the caller without range checks, consistent with the Lavender pattern where the caller is responsible for supplying valid enum/flag values (as documented in the `play_audio_effect_and__forget` review).

Side Effects:
1. On the NDS backend: writes the platform sound handle into `p_audio_effect->p_audio_instance_handle` and triggers platform audio playback via `mmEffect()`.
2. On stub backends (SDL, no_gui, test): no side effects (intentional no-op).
3. Does not modify `the_kind_of__audio_effect`, `audio_flags__u8`, or `timer_for__audio` — only the instance handle is written on backends with a real implementation.
