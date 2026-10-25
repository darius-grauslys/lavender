is_input__click_dragged — core/include/input/input.h

Returns whether the user is performing a click-drag: the click button is held AND the cursor has moved since the last poll.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input struct.
2. cursor__3i32 must contain the current cursor position.
3. cursor__old__3i32 must contain the cursor position from the previous poll cycle (updated by poll_input or clear_input).

Post-conditions:
1. Returns a bool: true if INPUT_CLICK is set in input_flags__held AND cursor__3i32 differs from cursor__old__3i32, false otherwise. Due to short-circuit evaluation, the cursor comparison is only performed when the click button is held.

Correctness Verdict: Correct

Semantic Alignment:
The function combines two conditions to detect a drag gesture — the click button must be held down, and the cursor must have moved. The implementation reads input_flags__held, masks with INPUT_CLICK, and ANDs with the negation of is_vectors_3i32__equal(cursor__3i32, cursor__old__3i32). This correctly expresses the drag semantic: a drag requires both a held click and a cursor movement. The use of && with short-circuit evaluation is appropriate — when the click is not held, the expensive vector comparison is skipped.

Implementation Correctness:
Type compatibility — input_flags__held is Input_Flags__u32 (uint32_t) and INPUT_CLICK is an int (1<<11 = 2048). The bitwise AND of uint32_t and int promotes the int to uint32_t; the result is uint32_t, implicitly converted to bool. is_vectors_3i32__equal takes two Vector__3i32 parameters by value; cursor__3i32 and cursor__old__3i32 are both Vector__3i32 fields (struct of three int32_t: x, y, z — 12 bytes each), so the types match exactly. No implicit conversions or truncation. Undefined behavior — no pointer arithmetic, no null dereference (assuming p_input is valid), no type punning, no out-of-bounds access. The short-circuit && is safe — is_vectors_3i32__equal only receives valid Vector__3i32 values from the struct. Validation — no validation is needed; this is a low-level inline accessor; the caller is responsible for ensuring p_input is valid and that cursor__old__3i32 is properly maintained by the polling infrastructure.

Side Effects:
No side effects — the function only reads from the pointed-to struct and delegates to the pure comparison function is_vectors_3i32__equal, which itself has no side effects (parameters passed by value, no mutation).
