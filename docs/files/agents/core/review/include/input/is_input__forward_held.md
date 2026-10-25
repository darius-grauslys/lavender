is_input__forward_held — core/include/input/input.h

Returns whether the "forward" action flag is currently held.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.

Post-conditions:
1. Returns a bool: true if the INPUT_FORWARD bit is set in p_input->input_flags__held, false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The function checks the held flag for the forward action. The implementation directly reads input_flags__held and masks with INPUT_FORWARD, matching the semantic intent of detecting forward movement input that is being held down.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t). INPUT_FORWARD is defined as (1<<0), which evaluates to the integer 1 (type int). Per C usual arithmetic conversions, the AND of uint32_t and int promotes the int operand to uint32_t; the result is uint32_t, which is implicitly converted to bool on return (non-zero → true, zero → false). No truncation or precision loss. No undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning, no out-of-bounds access. No validation is needed — this is a low-level inline accessor; the caller is responsible for ensuring p_input is valid.

Side Effects:
No side effects — the function only reads from the pointed-to struct and returns a value without modifying any state.
