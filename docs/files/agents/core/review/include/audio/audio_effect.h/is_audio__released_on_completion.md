is_audio__released_on_completion — core/include/audio/audio_effect.h, lines 42-45

### 1. Header
- **Function name:** `is_audio__released_on_completion`
- **File of origin:** `core/include/audio/audio_effect.h`

### 2. Semantic

Returns `true` if the specified audio effect has the `RELEASE_ON_COMPLETE` flag (`AUDIO_FLAG__RELEASE_ON_COMPLETE`) set in its `audio_flags__u8` field, and `false` otherwise. This indicates that the audio effect should be released (freed) once it finishes playing.

### 3. Pre-conditions
1. `p_audio_effect` must be non-null. Dereferencing a null pointer is undefined behavior.
2. `p_audio_effect->audio_flags__u8` must be a valid `Audio_Flags__u8` value (a byte-sized flag container).
3. The `Audio_Effect` struct must already have been initialized so that its fields exist.

### 4. Post-conditions
1. Returns `true` if `(p_audio_effect->audio_flags__u8 & BIT(1))` is non-zero (i.e., the `RELEASE_ON_COMPLETE` bit is set).
2. Returns `false` if `(p_audio_effect->audio_flags__u8 & BIT(1))` is zero (i.e., the `RELEASE_ON_COMPLETE` bit is not set).

### 5. Correctness Verdict

Correct

### 6. Semantic Alignment

The implementation fulfills the semantic intent. It performs a clean, isolated bit check against `AUDIO_FLAG__RELEASE_ON_COMPLETE` (defined as `BIT(1)` in `defines.h`). This follows the exact same pattern as the sibling functions `is_audio__active` (checks `BIT(0)`) and `is_audio__looping` (checks `BIT(2)`), which also check single flags from the same `audio_flags__u8` field. The flag `BIT(1)` is isolated — it does not overlap with `BIT(0)` (`IS_ACTIVE`) or `BIT(2)` (`IS_LOOPING`), so the check is unambiguous.

### 7. Implementation Correctness

- **Type compatibility:** The parameter `p_audio_effect` is `Audio_Effect *`, and the function accesses `audio_flags__u8` which is of type `Audio_Flags__u8`. The flag `AUDIO_FLAG__RELEASE_ON_COMPLETE` is defined as `BIT(1)`, which is a mask of the same byte type. No implicit conversions or truncation occur. The return type `bool` is appropriate for a binary flag check.
- **Undefined behavior:** No broken pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access. The function accesses exactly one byte-sized field (`audio_flags__u8`) of the struct — no field reordering or padding issues can affect a single-byte access.
- **Validation:** The function assumes a valid non-null pointer is passed by the caller, which is consistent with the Lavender style for `static inline` query helpers.

### 8. Side Effects

No side effects. This is a pure read-only query function — it does not modify the `Audio_Effect` struct or any other state.
