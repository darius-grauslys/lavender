is_input__turn_left_held — core/include/input/input.h

Returns whether the turn-left input bit is set in the held flags.

Pre-conditions:
1. p_input must be a non-null pointer to an initialized Input struct.
2. input_flags__held is expected to be a valid Input_Flags__u32 bitmask of INPUT_* flag values (the caller's responsibility).

Post-conditions:
1. Returns true if the INPUT_TURN_LEFT bit is set in p_input->input_flags__held; returns false (0) otherwise.
2. No state is mutated.

Correctness Verdict: Correct

Semantic Alignment:
The implementation checks the held-flags bitmask for the INPUT_TURN_LEFT bit, matching the intent of reporting whether the turn-left input is currently held. It is consistent with all sibling is_input__*_held functions (e.g. is_input__turn_right_held, is_input__forward_held) at input.h:132-176.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t) and INPUT_TURN_LEFT is an integer constant derived via INPUT_TURN_RIGHT<<1; the & result is a uint32_t, implicitly converted to bool (nonzero -> true, 0 -> false). No truncation or problematic conversion.
No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only dereference is p_input->input_flags__held, which is safe given the non-null pre-condition. Dereferencing a null p_input is UB but is not this function's validation responsibility; this matches the established pattern of every is_input__* query in this file.
No validation is needed here beyond the non-null contract — this is a low-level inline bitmask query; validation is the caller's responsibility.

Side Effects:
No side effects — the function is a pure read of p_input->input_flags__held.
