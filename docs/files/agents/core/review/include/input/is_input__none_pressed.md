### 1. Header
- **Function name:** `is_input__none_pressed`
- **File of origin:** `core/include/input/input.h`

### 2. Semantic
Reports whether *no* input action is currently pressed — i.e. the pressed-flags bitfield holds no bits (is zero).

### 3. Pre-conditions
1. `p_input` is a valid, non-null pointer to an initialized `Input` struct.
2. `p_input->input_flags__pressed` is a `uint32_t` (`Input_Flags__u32`) bitfield whose individual bits correspond to input-action flags (`INPUT_FORWARD`, `INPUT_LEFT`, … `INPUT_CLICK`). The value `0` is the sentinel `INPUT_NONE`, meaning "no flags set" (see `clear_input` at `input.h:33`, which resets all three flag fields to `INPUT_NONE`/`0`).

### 4. Post-conditions
1. Returns a `bool`: `true` when no input-action bit is set in `input_flags__pressed`, `false` when one or more bits are set.
2. `p_input` is not modified; the function is a pure read.

### 5. Correctness Verdict
Incorrect

### 6. Semantic Alignment
The semantic intent ("no input is pressed") requires testing that the entire flags field is zero. The implementation instead computes `p_input->input_flags__pressed & INPUT_NONE`, i.e. `& 0`, which is **always `0` (false)**. Because `INPUT_NONE` is defined as `0` (`platform_defaults.h:202`) — a sentinel meaning "no bits set" rather than a real bit position — AND-ing with it can never detect a non-zero field. The function therefore returns `false` in *every* case, including the exact case it is meant to detect (nothing pressed). This is a semantic failure: the function never fulfills its stated purpose. The correct form would be `return !p_input->input_flags__pressed;` (or `p_input->input_flags__pressed == INPUT_NONE`).

This same defect also affects the sibling accessors `is_input__none_released` (`input.h:79`) and `is_input__none_held` (`input.h:160`), but those are outside the scope of this single-function review.

### 7. Implementation Correctness
- **Type compatibility:** `input_flags__pressed` is `uint32_t`; `INPUT_NONE` is `0` (int). The `&` promotes operands and the `int` result is returned as `bool` — no truncation, but the logic is wrong.
- **Undefined behavior:** None. `& 0` is well-defined.
- **Validation:** None required at this layer; like every other `is_input__*` accessor in this file, the function trusts a valid non-null `p_input` (null checks are the caller's responsibility and out of scope for these low-level inline accessors).
- Root cause is logical, not type-based: a bit-test idiom (`flags & MASK`) was applied to a non-bit sentinel (`MASK == 0`).

### 8. Side Effects
No side effects. The function only reads `p_input->input_flags__pressed`; it does not modify `p_input` or any observable state.
