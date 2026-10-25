set_audio_as__active — core/include/audio/audio_effect.h, lines 54-57

### 1. Header

- **Function name:** `set_audio_as__active`
- **File of origin:** `core/include/audio/audio_effect.h`

### 2. Semantic

Sets the `audio_flags__u8` field of the `Audio_Effect` struct to include the `AUDIO_FLAG__IS_ACTIVE` bit, marking the audio effect as active.

### 3. Pre-conditions

1. `p_audio_effect` must be non-null (dereferenced directly on line 55).
2. `p_audio_effect->audio_flags__u8` must be a valid `Audio_Flags__u8` value (type compatibility is guaranteed by the struct definition).
3. No other pre-conditions — the function is a simple flag setter and does not depend on the state of any other field.

### 4. Post-conditions

1. After the function returns, `p_audio_effect->audio_flags__u8` has the `AUDIO_FLAG__IS_ACTIVE` bit set (i.e., `audio_flags__u8 & AUDIO_FLAG__IS_ACTIVE` is non-zero).
2. All other fields of the `Audio_Effect` struct are unchanged.
3. The function is non-mutating with respect to any other state — only `audio_flags__u8` is modified.

### 5. Correctness Verdict

Correct

### 6. Semantic Alignment

The function's semantic intent is to mark an audio effect as active. The implementation uses a bitwise OR (`|=`) with `AUDIO_FLAG__IS_ACTIVE` (defined as `BIT(0)`) on `audio_flags__u8`, which correctly sets the active bit regardless of its prior state without clearing other bits. This aligns with the semantic intent — the effect is now active, and no other flags are affected.

### 7. Implementation Correctness

- **Type compatibility:** The parameter `p_audio_effect` is `Audio_Effect *`, and `p_audio_effect->audio_flags__u8` is `Audio_Flags__u8` (which is `u8`). The flag value `AUDIO_FLAG__IS_ACTIVE` is `BIT(0)`, which is also `u8`. No implicit conversions or truncation issues.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (caller is responsible for ensuring non-null), no type punning, no out-of-bounds access. The function is a simple bit-field operation on a valid struct member.
- **Validation:** As a static inline helper, the responsibility for passing a valid, non-null `Audio_Effect *` lies with the caller, consistent with the Lavender codebase pattern where helper functions do not validate their inputs.

### 8. Side Effects

- Mutates `p_audio_effect->audio_flags__u8` by setting the `AUDIO_FLAG__IS_ACTIVE` bit via bitwise OR.
- No other side effects — this is a pure flag-setting operation with no I/O, no memory allocation, and no interaction with other systems.
