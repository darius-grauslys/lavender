is_input__right_held — core/include/input/input.h

Returns whether the "right" direction flag is currently held.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.

Post-conditions:
1. Returns a bool: true if the INPUT_RIGHT bit is set in p_input->input_flags__held, false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The function checks the held flag for rightward input. The implementation directly reads input_flags__held and masks with INPUT_RIGHT, matching the semantic intent of detecting a held right-direction key.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t). INPUT_RIGHT is defined as (INPUT_LEFT<<1) where INPUT_LEFT is (INPUT_FORWARD<<1) and INPUT_FORWARD is (1<<0), so INPUT_RIGHT evaluates to the integer 4. The bitwise AND of uint32_t and int promotes the int to uint32_t per C conversion rules; the result is uint32_t and is implicitly converted to bool on return (non-zero → true, zero → false). No truncation or precision loss. No undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning, no out-of-bounds access. No validation is needed — this is a low-level inline accessor; the caller is responsible for ensuring p_input is valid.

Side Effects:
No side effects — the function only reads from the pointed-to struct and returns a value without modifying any state.
