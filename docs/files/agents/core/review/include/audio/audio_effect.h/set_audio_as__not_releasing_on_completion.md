set_audio_as__not_releasing_on_completion — core/include/audio/audio_effect.h, lines 71-75

## 1. Header
- **Function name**: `set_audio_as__not_releasing_on_completion`
- **File of origin**: `core/include/audio/audio_effect.h`

## 2. Semantic
Clears the `RELEASE_ON_COMPLETE` flag bit from the `audio_flags__u8` field of the given `Audio_Effect` instance, leaving all other flags unchanged.

## 3. Pre-conditions
1. `p_audio_effect` must be non-null — the function dereferences it on the next line.
2. `p_audio_effect->audio_flags__u8` must be a valid `Audio_Flags__u8` value — the field is always valid as long as the `Audio_Effect` struct itself is valid.

## 4. Post-conditions
1. The `RELEASE_ON_COMPLETE` flag bit (`AUDIO_FLAG__RELEASE_ON_COMPLETE`, i.e. `BIT(1)` = 0x02) is cleared from `p_audio_effect->audio_flags__u8`.
2. All other flag bits in `audio_flags__u8` remain unchanged.
3. No other fields of the `Audio_Effect` struct are modified.
4. The caller's pointer `p_audio_effect` is unchanged.

## 5. Correctness Verdict
`Correct`

## 6. Semantic Alignment
The implementation fulfills the semantic intent. The function uses `p_audio_effect->audio_flags__u8 &= ~AUDIO_FLAG__RELEASE_ON_COMPLETE` to selectively clear only the `RELEASE_ON_COMPLETE` bit while preserving all other bits. This is the correct complementary operation to `set_audio_as__releasing_on_completion`, which sets the flag with `|=`. No struct fields are omitted, no reordering occurs, and the bit-level operation matches the documented intent.

## 7. Implementation Correctness
- **Type compatibility**: `Audio_Flags__u8` is a `u8` type. `AUDIO_FLAG__RELEASE_ON_COMPLETE` is defined as `BIT(1)`, which evaluates to a `u8` constant (0x02). The `~` operator on a `u8` operand produces a `u8` result, and `&=` between two `u8` operands is well-defined. No implicit conversions or truncation occur.
- **Undefined behavior**: None. The `&=` with a complemented flag constant is safe, well-defined behavior. No null dereference occurs (caller guarantees a valid pointer). No type punning or out-of-bounds access.
- **Validation**: The function does not validate that `p_audio_effect` is non-null. This is consistent with all other `set_audio_as_*` functions in the same header (`set_audio_as__active`, `set_audio_as__inactive`, `set_audio_as__releasing_on_completion`, etc.), which also lack null checks. In this codebase pattern, null validation is the caller's responsibility for this class of static inline flag setters.

## 8. Side Effects
- **Mutating**: Mutates exactly one field of the provided `Audio_Effect` struct — the `audio_flags__u8` field is modified to clear the `RELEASE_ON_COMPLETE` bit. No other fields are mutated. No observable side effects beyond this bit-level modification.
