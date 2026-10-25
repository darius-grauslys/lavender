# Function Review: is_input__left_pressed

## 1. Header
- **Function name:** `is_input__left_pressed`
- **File of origin:** `core/include/input/input.h`

## 2. Semantic
Inline query that returns whether the Left input bit is currently set in the Input's "pressed" bitmask (`input_flags__pressed`).

## 3. Pre-conditions
1. `p_input` must be a non-null pointer to an `Input` struct.
2. `input_flags__pressed` must have been populated by platform polling (e.g. `poll_input` -> `PLATFORM_poll_input`); callers of this accessor are responsible for providing a valid, initialized `Input` (the struct need not be zeroed for this query to be safe, only `p_input` itself must be valid).
3. The `INPUT_LEFT` bitmask is a compile-time constant `(1<<1)` = `2`.

## 4. Post-conditions
1. Returns `true` if the `INPUT_LEFT` bit is set in `p_input->input_flags__pressed`, `false` otherwise.
2. No state of the `Input` struct is mutated.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The implementation exactly matches its intent. The bitwise AND `input_flags__pressed & INPUT_LEFT` isolates the Left flag within the pressed bitmask, and the implicit conversion to `bool` yields `true` when the bit is set and `false` when it is not. This is identical to the pattern used by every sibling query in the file (e.g. `is_input__forward_pressed`, `is_input__left_released`, `is_input__left_held`), so the semantics are consistent across the input API.

## 7. Implementation Correctness
- **Type compatibility:** `input_flags__pressed` is `Input_Flags__u32` (`uint32_t`); `INPUT_LEFT` is the integer constant `2`. The `&` operator produces a `uint32_t`. Conversion of that `uint32_t` result to the `bool` return type is well-defined in C: any nonzero value becomes `true`, zero becomes `false`. No truncation of meaningful data occurs for a boolean predicate. The result matches all sibling functions and is idiomatic for this codebase.
- **Undefined behavior:** None. The pointer is dereferenced once to read `input_flags__pressed`; the bitmask `INPUT_LEFT` is a small value well within the `uint32_t` range, so the AND is well-defined. No pointer arithmetic, no type punning, no out-of-bounds array access.
- **Validation:** Appropriate for the function's role. As an `inline` accessor, it does not null-check `p_input` or otherwise guard its input; this is the established convention across all sibling accessors in this header (`is_input__*_pressed`, `is_input__*_released`, `is_input__*_held`, `get_last_symbol_of__input_for__writing`, `clear_input`, etc.). Responsibility for passing a valid non-null pointer rests with the caller, which is consistent with the codebase's inline-accessor design.

## 8. Side Effects
No side effects. The function is a pure, non-mutating read of `input_flags__pressed`.
