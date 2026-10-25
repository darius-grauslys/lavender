# is_input__examine_released

## 1. Header
- **Function name:** `is_input__examine_released`
- **File of origin:** `core/include/input/input.h`

## 2. Semantic
Returns whether the "examine" input release event is set for the current frame — i.e., whether the `INPUT_EXAMINE` bit is present in the input's released-flags bitmask.

## 3. Pre-conditions
1. `p_input` must be a non-null pointer to a valid, initialized `Input` struct.
2. `p_input->input_flags__released` must have been populated by `poll_input` / cleared by `clear_input` or `initialize_input` so it reflects the current frame's released events.

## 4. Post-conditions
1. Returns `true` if the `INPUT_EXAMINE` bit is set in `p_input->input_flags__released`; returns `false` otherwise.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The implementation fulfills the semantic intent. `INPUT_EXAMINE` is a single power-of-two bit (value `1<<11` = 2048, derived via chained `<<=1` from `INPUT_FORWARD`), so `input_flags__released & INPUT_EXAMINE` isolates exactly that bit: result is `0` (bit clear) or `2048` (bit set). This is identical to the pattern used by all sibling accessors (e.g. `is_input__use_released` at input.h:60, `is_input__examine_held` at input.h:157). No semantic drift.

## 7. Implementation Correctness
- **Type compatibility:** `input_flags__released` is `Input_Flags__u32` (`uint32_t`); `INPUT_EXAMINE` is an `int` literal. Per integer promotion rules the `int` is converted to `uint32_t`; the result is `uint32_t`, then implicitly converted to the `bool` return type (nonzero → `true`). No truncation.
- **Undefined behavior:** None. No pointer arithmetic; `p_input` is dereferenced only under the assumption it is a valid pointer (consistent with all sibling accessors — null-checking is the caller's responsibility, not the role of these inline query functions).
- **Validation:** Appropriate as-is. These are inline input-query accessors; per the codebase convention (see `is_input__forward_released`, `is_input__use_released`, etc.), `p_input` validity is the caller's precondition, not re-validated inline.

## 8. Side Effects
No side effects. This is a pure, non-mutating query: it reads a single field of `*p_input` and returns a boolean. It does not modify `p_input` or any observable state.
