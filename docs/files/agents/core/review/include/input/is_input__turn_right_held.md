is_input__turn_right_held — core/include/input/input.h

Returns whether the turn-right input flag is currently held.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, initialized Input struct.
2. The input_flags__held field must be readable (i.e., the Input struct has been initialized via initialize_input or clear_input).

Post-conditions:
1. Returns true if the INPUT_TURN_RIGHT bit is set in p_input->input_flags__held; returns false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The function name (is_input__turn_right_held) precisely matches its behavior: it tests the INPUT_TURN_RIGHT bit in the held flags field. No semantic drift.

Implementation Correctness:
- Type compatibility — p_input->input_flags__held is Input_Flags__u32 (uint32_t); INPUT_TURN_RIGHT is an integer constant defined as (INPUT_CONSUME<<1), a distinct power-of-two bitmask. The & operator yields uint32_t, which is implicitly converted to bool on return (zero becomes false, non-zero becomes true). This is well-defined and correct.
- No undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only risk is null dereference if p_input is NULL, but this is consistent with the codebase design (all is_input__* query functions follow the same pattern without null checks).
- No validation is needed — this is a low-level query function. Ensuring p_input is non-null is the caller's responsibility (consistent with the rest of the file.

Side Effects:
No side effects — the function only reads from the pointed-to Input struct and returns a bool.
