is_input__examine_pressed — core/include/input/input.h

Returns whether the examine input is currently pressed.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, readable Input object.
2. p_input->input_flags__pressed is an Input_Flags__u32 (uint32_t) bitmask holding the currently-pressed input flags; it need not be freshly initialized.

Post-conditions:
1) Returns true if the INPUT_EXAMINE bit is set in p_input->input_flags__pressed, otherwise false (0).
2) The Input object is not modified — only input_flags__pressed is read.

Correctness Verdict: Correct

Semantic Alignment: The function tests the INPUT_EXAMINE bit of the pressed-flags bitmask and returns its boolean state. This matches the function name and is consistent with every sibling `is_input__*_pressed` function (e.g. is_input__forward_pressed at line 87, is_input__use_pressed at line 105), which all follow the identical pattern.

Implementation Correctness:
Type compatibility — input_flags__pressed is Input_Flags__u32 (uint32_t) and INPUT_EXAMINE is a bitmask literal. The bitwise AND yields an integer result that is implicitly and safely converted to the bool return type (non-zero → true, zero → false); this conversion is well-defined in C and matches the pattern of all sibling pressed-query functions. bool itself is available via <stdbool.h> included transitively through defines.h.
Undefined behavior — none. No pointer arithmetic, no null dereference (precondition mandates non-null), no type punning, no out-of-bounds access. INPUT_EXAMINE is a single-bit flag (bit 8) so the AND isolates exactly one bit with no multi-bit overlap concerns.
Validation — no validation is needed in this function. This is a low-level read-only query accessor; per the codebase convention (no sibling `is_input__*` function validates), null-checking is the caller's responsibility.

Side Effects: No side effects — the function is a pure query; it only reads p_input->input_flags__pressed and does not modify any memory or state.
