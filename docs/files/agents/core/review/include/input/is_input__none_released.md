is_input__none_released — core/include/input/input.h

Returns whether no input actions were released this frame.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.

Post-conditions:
1. Returns a bool: true if no release flags are set (released flags equal INPUT_NONE/0), false otherwise.

Correctness Verdict: Incorrect

Semantic Alignment:
The function is intended to detect when no release events occurred in the current poll cycle (i.e., the released flags are zero). However, the implementation reads input_flags__released & INPUT_NONE, where INPUT_NONE is defined as 0. A bitwise AND with 0 always evaluates to 0 (false), regardless of the actual flag state. This means the function can never return true, even when no flags are set. The correct implementation to fulfill the semantic intent would be to check for equality: return p_input->input_flags__released == INPUT_NONE (or equivalently, return !p_input->input_flags__released). The same semantic mismatch exists in the sibling functions is_input__none_pressed (input.h:123) and is_input__none_held (input.h:159), which also AND with INPUT_NONE (0) and thus always return false. If the intent were literally "was the INPUT_NONE bit released?", the question is meaningless since INPUT_NONE is a sentinel value (0), not a physical input — there is no bit to set or check.

Implementation Correctness:
Type compatibility — input_flags__released is Input_Flags__u32 (uint32_t), INPUT_NONE is defined as 0 (int), and the result is implicitly converted to bool. No type incompatibility, but the logic is semantically wrong. Undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning, no out-of-bounds access. The code is well-formed; the issue is not undefined behavior but a semantic defect — the bitmask query is meaningless because INPUT_NONE carries no bits to test. Validation — no validation is needed at this level; the caller is responsible for ensuring p_input is valid.

Side Effects:
No side effects — the function only reads from the pointed-to struct and returns a value without modifying any state.
