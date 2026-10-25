set_audio_effect — core/include/audio/audio_effect.h, lines 15-27

## 1. Header

**Function name:** `set_audio_effect`
**File of origin:** `core/include/audio/audio_effect.h`

## 2. Semantic

Sets all properties of an existing `Audio_Effect` (kind, flags, duration) while preserving the audio instance handle and the IS_ACTIVE flag from its prior state.

## 3. Pre-conditions

1. `p_audio_effect` must be non-null and point to a valid, allocated `Audio_Effect` struct.
2. `the_kind_of__audio_effect` must be a valid value of `enum Audio_Effect_Kind`.
3. `audio_flags` must be a valid value of `Audio_Flags__u8` (a bitmask of defined flag bits).
4. `duration_of__audio` must be a valid `Timer__u32` value.

## 4. Post-conditions

1. `p_audio_effect->the_kind_of__audio_effect` is set to `the_kind_of__audio_effect`.
2. `p_audio_effect->p_audio_instance_handle` retains its prior value (passed through unchanged).
3. `p_audio_effect->audio_flags__u8` is set to `audio_flags | (prior_audio_flags & AUDIO_FLAG__IS_ACTIVE)` — new flags from the parameter are applied, and the IS_ACTIVE bit from the prior state is preserved.
4. `p_audio_effect->timer_for__audio` is set to `duration_of__audio`.
5. All other fields of `p_audio_effect` retain their prior values (unchanged by this function).

## 5. Correctness Verdict

Correct

## 6. Semantic Alignment

The function's semantic intent is to set the audio effect's properties (kind, flags, duration) while preserving the audio instance handle and active state. The implementation fulfills this intent. The `initialize_audio_effect` call resets all struct fields, but the handle is passed through as a read-write that preserves its value, and the IS_ACTIVE flag is explicitly preserved via the `audio_flags | (p_audio_effect->audio_flags__u8 & AUDIO_FLAG__IS_ACTIVE)` expression. Other flags (`RELEASE_ON_COMPLETE`, `IS_LOOPING`) are intentionally reset to the values in the `audio_flags` parameter, which is consistent with the pattern of using individual `set_audio_as__*` functions for fine-grained flag manipulation.

## 7. Implementation Correctness

- **Type compatibility:** All parameter types match their target struct field types exactly. No implicit conversions or truncation occur.
- **Undefined behavior:** The function dereferences `p_audio_effect` without a null check. This is acceptable because `set_audio_effect` is a `static inline` that is called only from `play_audio_effect_and__forget` (which validates the pointer after allocation) and other contexts where the pointer is expected to be valid. No broken pointer arithmetic, null dereference, type punning, or out-of-bounds access occurs within the function body.
- **Validation:** Null-pointer validation is the caller's responsibility, which is consistent with the Lavender pattern of relying on caller contract adherence for `static inline` utility functions.

## 8. Side Effects

Mutates `p_audio_effect`:

- `p_audio_effect->the_kind_of__audio_effect` — set to `the_kind_of__audio_effect`
- `p_audio_effect->audio_flags__u8` — set to `audio_flags | (prior_audio_flags__u8 & AUDIO_FLAG__IS_ACTIVE)`
- `p_audio_effect->timer_for__audio` — set to `duration_of__audio`
- `p_audio_effect->p_audio_instance_handle` — read then written with the same value (no observable change)

No side effects beyond the mutation of `p_audio_effect`. No resource acquisition occurs — this is a pure Lavender-style initialization (state reset), not RAII.
