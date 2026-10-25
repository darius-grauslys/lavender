# is_audio__active

## Header

- **Function name:** `is_audio__active`
- **File of origin:** `core/include/audio/audio_effect.h` (lines 36-39)

## Semantic

Returns whether the given `Audio_Effect` has the `AUDIO_FLAG__IS_ACTIVE` bit set in its `audio_flags__u8` field — i.e., whether the audio effect is currently active.

## Pre-conditions

1. `p_audio_effect` must be a valid, non-null pointer to a properly allocated `Audio_Effect` instance. (This is the caller's responsibility — the function does not validate the pointer.)
2. The caller must have permission to read the `Audio_Effect`'s `audio_flags__u8` field.
3. The `Audio_Effect` struct must already have been initialized (either via `initialize_audio_effect`, `set_audio_effect`, `play_audio_effect_and__forget`, or equivalent) so that its fields exist.

## Post-conditions

1. Returns `true` if `p_audio_effect->audio_flags__u8` has `BIT(0)` (i.e. `AUDIO_FLAG__IS_ACTIVE`) set.
2. Returns `false` if `p_audio_effect->audio_flags__u8` has `BIT(0)` clear.
3. No state is modified on `p_audio_effect` or any other object.
4. No global state is changed.

## Correctness Verdict

Correct

## Semantic Alignment

The function's name matches its intent — it reports whether an audio effect is active. The implementation checks exactly the `AUDIO_FLAG__IS_ACTIVE` flag bit, which is the canonical indicator of activity in this subsystem. The function is declared `static inline`, which is appropriate for a small, frequently-called getter that should be inlined. All other `is_audio__*` getter functions in the same header follow the same pattern, confirming consistent semantics.

## Implementation Correctness

- **Type compatibility:** `p_audio_effect` is `Audio_Effect *`, dereferenced to access `audio_flags__u8` which is `Audio_Flags__u8` (typedef'd as `u8`). `BIT(0)` is defined in `defines.h` as a `u8` bitmask. The `&` operator on two `u8` values yields `u8`, then an implicit `u8` → `bool` conversion (0 → `false`, non-zero → `true`) is applied by the return type. All types are compatible with no truncation or loss of information.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (caller's responsibility), no type punning, no out-of-bounds access. The access is a single field read on a struct pointer — no UB.
- **Validation:** No validation is performed. This is a `static inline` getter — validation belongs in the caller. The function is trivially fast and the overhead of adding validation would be unnecessary for a single-field read. This is appropriate for the function's role.

## Side Effects

No side effects.
