is_input__lockon_held — core/include/input/input.h

Returns whether the lockon input is currently held down.

Pre-conditions:
1. p_input must be a non-null pointer to a valid Input object.
2. p_input->input_flags__held must be a populated Input_Flags__u32 (uint32_t) holding the currently-held input flags, as maintained by poll_input (held = pressed_old & pressed).

Post-conditions:
1) Returns true if the INPUT_LOCKON bit is set in input_flags__held, false otherwise.

Correctness Verdict: Correct

Semantic Alignment:
The implementation tests the INPUT_LOCKON bit directly against input_flags__held, which (per the polling logic input_flags__held = input_flags__pressed_old & input_flags__pressed) holds exactly the inputs currently held across frames. This matches the "held" semantic and is consistent with sibling queries (is_input__forward_held, is_input__lockon_pressed, is_input__lockon_released). Not an initialization function, so the Lavender "init != RAII" note does not apply.

Implementation Correctness:
Type compatibility — input_flags__held is uint32_t; INPUT_LOCKON is an integer constant expression (value 256, within int range) implicitly converted to uint32_t for the & operation; the uint32_t result is implicitly converted to bool (non-zero -> true). No truncation or lossy conversion.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
Validation — no validation is needed at this level. Like all is_input__* inline queries, a non-null p_input is assumed; null-checking is the caller's responsibility, which matches the codebase convention.

Side Effects:
No side effects — pure query function returning a boolean derived from the read-only input_flags__held field.