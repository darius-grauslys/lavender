is_input__turn_left_released — core/include/input/input.h

Returns whether the turn-left input transitioned to the released state this frame.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, populated Input object.
2. input_flags__released must have been set by a prior call to poll_input; its value is otherwise meaningless to this function.

1) Returns true when the INPUT_TURN_LEFT bit is set in input_flags__released; false otherwise.
2) p_input is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The implementation directly tests the INPUT_TURN_LEFT bit (defined in platform_defaults.h as INPUT_TURN_RIGHT<<1, a power-of-two flag) against the input_flags__released bitfield (Input_Flags__u32 / uint32_t). This faithfully implements the semantic intent: "was turn-left released this frame?" It is identical in form to every other is_input__*_released accessor in this file (e.g. is_input__forward_released), so there is no semantic drift relative to its sibling functions.

Implementation Correctness:
Type compatibility — input_flags__released is Input_Flags__u32 (uint32_t). INPUT_TURN_LEFT is an int literal; the bitwise AND applies the usual arithmetic conversions, converting the int operand to unsigned int (uint32_t) because INPUT_TURN_LEFT is a positive power-of-two, so no sign issues arise. The result (uint32_t) is implicitly converted to the bool return type: any non-zero value becomes true, zero becomes false — well-defined per the C standard. No implicit truncation or narrowing occurs.
Operator precedence — '->' binds tighter than binary '&', so the expression parses as (p_input->input_flags__released) & (INPUT_TURN_LEFT) as intended; no parentheses are needed.
Undefined behavior — none. No pointer arithmetic, no null dereference (validation is the caller's responsibility, consistent with all sibling accessors), no type punning, no out-of-bounds access.
Validation — none required; this is a low-level inline accessor and null-checking is pushed to callers throughout the input query family.

Side Effects:
No side effects — this is a pure query. The only observable effect is reading the input_flags__released field of the pointed-to Input struct and deriving a bool from it; no state is mutated.
