# Function Review: `is_input__forward_released`

**File of origin:** `core/include/input/input.h`

```c
static bool inline is_input__forward_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_FORWARD;
}
```

## 2. Semantic

Tests whether the `INPUT_FORWARD` bit is set in the Input's *released* flags bitmask, i.e. whether the forward control was released this frame.

## 3. Pre-conditions

1. `p_input` is non-null and points to a valid, previously-initialized `Input` struct (field `input_flags__released` must hold a meaningful flag word).
2. No null-check is performed; null dereference is the caller's responsibility (consistent with the inline accessor pattern used across `input.h`).

## 4. Post-conditions

1. Returns `true` if `p_input->input_flags__released & INPUT_FORWARD` is non-zero (bit set); `false` otherwise.
2. `p_input` is not modified (read-only access).

## 5. Correctness Verdict

**Correct**

## 6. Semantic Alignment

The implementation matches the intent exactly: `input_flags__released` is `Input_Flags__u32` (`uint32_t`) and `INPUT_FORWARD` is defined as `(1<<0)` in `platform_defaults.h:203`. The bitwise-AND isolates the forward bit from the released-flags field, correctly answering "was forward released?". Field selection is correct — no other struct field is touched.

## 7. Implementation Correctness

- **Type compatibility:** `input_flags__released` is `uint32_t`; `INPUT_FORWARD` is `int` (`1<<0`). Per the usual arithmetic conversions the `int` operand is converted to `uint32_t`, so the result of `&` is `uint32_t` (either `0` or `1` here). The return type is `bool` (`stdbool.h`, included via `defines.h:7`); the `uint32_t` is implicitly converted to `bool` (`0`→`false`, non-zero→`true`), which is well-defined and the idiomatic flag-test pattern. No truncation or narrowing hazard.
- **Undefined behavior:** None. No pointer arithmetic, no out-of-bounds access, no type punning. The only risk would be a null `p_input`, which is caller responsibility (these accessors deliberately do not validate, matching the codebase convention).
- **Validation:** Appropriate for a small inline accessor. The codebase does not validate inside these flag-checkers.
- Note (non-blocking): the declarator order `static bool inline` is unusual (more common is `static inline bool`) but is valid C and has no behavioral effect.

## 8. Side Effects

No side effects. Pure read accessor. Reads `p_input->input_flags__released`; does not mutate `p_input` or any other state.
