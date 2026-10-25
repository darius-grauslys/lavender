# is_input__backward_held

- **File of origin:** `core/include/input/input.h` (lines 141-143)

## Semantic

Returns whether the "backward" input flag is currently held (set in the held-flags bitmask).

## Pre-conditions

1. `p_input` must be a valid, non-null pointer to an initialized `Input` struct.
2. `p_input->input_flags__held` must reflect the current held input state, maintained by `poll_input` (called by `game.c`) and reset by `clear_input`.

## Post-conditions

1. Returns `true` if the `INPUT_BACKWARD` bit is set in `p_input->input_flags__held`, `false` otherwise.
2. No struct state is mutated; the function is read-only.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation matches the semantic intent: it tests the `held` flag-field for the backward-direction bit. It is structurally identical to every sibling `*_held` accessor in the same header (e.g. `is_input__forward_held`, `is_input__left_held`, `is_input__right_held`), so it fulfills its intent. `INPUT_BACKWARD` is defined as `(INPUT_RIGHT<<1)` = `(1<<3)` = `8`, a single bit, so the bitwise AND isolates exactly the backward flag.

## Implementation Correctness

- **Type compatibility:** `input_flags__held` is `Input_Flags__u32` (`uint32_t`); `INPUT_BACKWARD` is an integer constant (`8`). The bitwise AND yields `uint32_t`, which is implicitly converted to `bool` on return (0 -> `false`, non-zero -> `true`). This is the same pattern used by all other accessors in this header and is correct for a single-bit flag. No truncation occurs for a single-bit flag.
- **Undefined behavior:** None. Simple struct member dereference and bitwise operation; no pointer arithmetic, no out-of-bounds access, no aliasing violation.
- **Validation:** No null check on `p_input`. This is consistent with the entire family of low-level inline accessors in this header (`is_input__forward_held`, `get_input_mode_of__input`, `consume_input`, etc.), where validation is the caller's responsibility. No change needed to match conventions.

## Side Effects

No side effects. The function only reads `p_input->input_flags__held` and returns a `bool`.
