consume_input — core/include/input/input.h

Clears the specified input flags from the pressed, held, and released flag bitfields of an Input struct, consuming acknowledged input events.

Pre-conditions:
1. p_input must be a non-null pointer to a writable Input object.
2. input_flags is any Input_Flags__u32 (uint32_t) — a bitwise OR of zero or more INPUT_* flag values, or 0 (INPUT_NONE).

Post-conditions:
1. p_input->input_flags__released has all bits set in input_flags cleared (set to 0).
2. p_input->input_flags__pressed has all bits set in input_flags cleared (set to 0).
3. p_input->input_flags__held has all bits set in input_flags cleared (set to 0).
4. All other bits within those three fields are preserved unchanged.
5. All other Input fields — including input_flags__pressed_old, cursor__3i32, cursor__old__3i32, writing_buffer, last_symbol, the writing-buffer indices, and input_mode__u8 — are untouched.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements "consuming" input by clearing the specified flags from all three transient state bitfields (pressed, held, released) via `field &= ~input_flags`. This matches the semantic intent: once an input flag has been consumed/acknowledged, it should no longer appear as pressed, held, or released. The function intentionally does NOT clear input_flags__pressed_old, which tracks the previous polling cycle's state and is not a transient event to be consumed. This is confirmed by the tests in test_suite_input_input.c (lines 645-682) which assert that consumed flags are cleared while unconsumed flags remain set.

Implementation Correctness:
Type compatibility — p_input is Input * (matching struct Input_t via typedef Input); input_flags is Input_Flags__u32 (uint32_t) and the target fields input_flags__released, input_flags__pressed, and input_flags__held are all Input_Flags__u32 (uint32_t). The expression ~input_flags is uint32_t, and the compound AND-assign (&=) operates on two uint32_t values. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no null dereference (p_input non-null is the caller's contract), no type punning, no out-of-bounds access. The bitwise complement (~) and AND (&=) on uint32_t are well-defined per the C standard.
Validation — no validation is needed; this is a low-level inline function operating on a struct via a pointer. Ensuring p_input validity is the caller's responsibility, consistent with the pattern seen in clear_input (line 33) and the audio_effect example.

Side Effects:
Mutates three fields of the struct pointed to by p_input: input_flags__released, input_flags__pressed, and input_flags__held — clearing the bits specified in input_flags from each. All other fields of the Input struct are left unchanged.
