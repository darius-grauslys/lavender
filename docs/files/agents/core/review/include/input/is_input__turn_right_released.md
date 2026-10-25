1. Header
- **Function name:** `is_input__turn_right_released`
- **File of origin:** `core/include/input/input.h` (lines 75-77)

2. Semantic
- Returns whether the "turn right" input was released on this frame by testing the `INPUT_TURN_RIGHT` bit in the input's released-flags.

3. Pre-conditions
1. `p_input` must be a non-null, valid pointer to an initialized `Input` struct.
2. The caller is responsible for ensuring the pointer validity (no null check is performed; consistent with all sibling accessors in this header).

4. Post-conditions
1. On return the `Input` struct is unmodified.
2. Returns `true` if the `INPUT_TURN_RIGHT` bit is set in `p_input->input_flags__released`; returns `false` otherwise.
3. The integer result of the bitwise AND is converted to `bool` per the C standard (0 → false, non-zero → true).

5. Correctness Verdict
- `Correct`

6. Semantic Alignment
- The implementation performs exactly one bitwise AND between `input_flags__released` and the `INPUT_TURN_RIGHT` bitmask and returns its truthiness. This matches the semantic intent of a "turn right released" query. No semantic drift. The function is one of 24 identical-pattern accessors (`is_input__*_released`/`*_pressed`/`*_held`) in the same header, all sharing this exact structure; the sibling `is_input__turn_left_released`, `is_input__turn_right_pressed`, and `is_input__turn_right_held` all confirm the intended pattern.

7. Implementation Correctness
- Type compatibility: `p_input->input_flags__released` is `Input_Flags__u32` (`uint32_t`); `INPUT_TURN_RIGHT` expands to `(INPUT_CONSUME<<1)` = `(INPUT_EXAMINE<<2)`, an integer constant expression. The bitwise AND produces an integer-compatible result with no implicit narrowing or truncation, and conversion of the result to `bool` is well-defined by the C standard.
- Undefined behavior: No pointer arithmetic, no null dereference (guarded by the documented pre-condition that `p_input` is non-null), no type punning, and no out-of-bounds access. The bit-flag `INPUT_TURN_RIGHT` is well within the 32-bit width of `input_flags__released` (it is `INPUT_EXAMINE<<2`, a low-order bit), so there is no overflow.
- Validation: No null/validity check is performed inside the function. This is appropriate for an `inline` query accessor used in tight game-loop hot paths, and it is consistent with the codebase-wide convention — none of the sibling accessors validate either. Validation responsibility rests with the caller, which matches the role of these helpers.

8. Side Effects
- No side effects. The function performs a read-only access through the `p_input` pointer and does not modify any observable state.
