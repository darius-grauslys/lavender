is_input__lockon_pressed — core/include/input/input.h

Returns whether the "lockon" action flag was pressed this frame.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.

Post-conditions:
1. Returns a bool: true if the INPUT_LOCKON bit is set in p_input->input_flags__pressed, false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The function checks the pressed flag for the lockon action. The implementation directly reads input_flags__pressed and masks with INPUT_LOCKON, matching the semantic intent of detecting a lockon key that was pressed in the current poll cycle.

Implementation Correctness:
Type compatibility — input_flags__pressed is Input_Flags__u32 (uint32_t). INPUT_LOCKON is defined as (INPUT_GAME_SETTINGS<<1) where INPUT_GAME_SETTINGS is (INPUT_BACKWARD<<1), and so on down to INPUT_FORWARD which is (1<<0). Following the chain, INPUT_LOCKON evaluates to the integer 32. The bitwise AND of uint32_t and int promotes the int to uint32_t per C conversion rules; the result is uint32_t and is implicitly converted to bool on return (non-zero → true, zero → false). No truncation or precision loss. No undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning, no out-of-bounds access. No validation is needed — this is a low-level inline accessor; the caller is responsible for ensuring p_input is valid.

Side Effects:
No side effects — the function only reads from the pointed-to struct and returns a value without modifying any state.
