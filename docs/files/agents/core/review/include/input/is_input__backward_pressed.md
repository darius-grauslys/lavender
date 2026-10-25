### 1. Header
- **Function name:** `is_input__backward_pressed`
- **File of origin:** `core/include/input/input.h`

### 2. Semantic
Returns whether the backward input bit is currently held in the pressed flag field of the `Input`.

### 3. Pre-conditions
1. `p_input` must be a valid, non-null pointer to an initialized `Input` struct.
2. `p_input->input_flags__pressed` is expected to be a `uint32_t` bitmask maintained by the input polling layer (`poll_input`).
3. No internal null-check is performed; null-pointer safety is the caller's responsibility (consistent with all sibling `is_input__*` accessors).

### 4. Post-conditions
1. Returns `bool` — `true` if the `INPUT_BACKWARD` bit is set in `p_input->input_flags__pressed`, otherwise `false`.
2. The `Input` struct is read-only; no state is modified.

### 5. Correctness Verdict
Correct

### 6. Semantic Alignment
The implementation correctly tests the backward bit via a bitwise AND against the non-overlapping `INPUT_BACKWARD` flag (value 8, i.e. `INPUT_RIGHT<<1`). The bit-flag definitions (`INPUT_FORWARD = 1<<0`, each subsequent flag shifted left by one) are mutually exclusive, so the result of the AND is either `0` (not pressed) or `8` (`INPUT_BACKWARD` itself). The result is semantically a "is this pressed?" boolean, which matches the function's name and intent. This matches the exact pattern used by every sibling accessor (e.g. `is_input__forward_pressed`, `is_input__click_pressed`, `is_input__backward_held`), so it is consistent with the codebase convention.

### 7. Implementation Correctness
- **Type compatibility:** `input_flags__pressed` is `Input_Flags__u32` (`uint32_t`); `INPUT_BACKWARD` is an `int` macro with value `8`. In the expression `uint32_t & int`, the `int` undergoes integer promotion to `uint32_t`, producing a `uint32_t` result. This is then implicitly converted to `bool` (0 → false, nonzero → true). No truncation or data loss occurs; the conversion is well-defined per the C standard.
- **Undefined behavior:** No pointer arithmetic, no null dereference (caller guarantees a valid pointer), no out-of-bounds access. The expression is a simple bitwise test.
- **Validation:** No validation is performed, which is appropriate for an `inline` accessor in a performance-critical game engine where the caller is responsible for providing a valid `Input` — this matches the established convention of all sibling functions.
- **Potential concern (minor, by design):** The returned `bool` before conversion is `8`, not `1`. This is harmless because any nonzero integer converts to `true`, but it is a pattern-wide characteristic rather than a defect in this function specifically.

### 8. Side Effects
No side effects. The function performs a read-only test on `p_input->input_flags__pressed` and returns a `bool`.
