is_input__click_released — core/include/input/input.h

Reports whether the click input was released since the last poll by testing the released-bitmask.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, initialized Input object.
2. INPUT_CLICK is the bitmask (INPUT_TURN_LEFT<<1), a single set bit within a u32; no further constraints on the flag value.

Post-conditions:
1. Returns true if the INPUT_CLICK bit is set in p_input->input_flags__released; returns false otherwise.
2. p_input is not modified — the function is a read-only query.

Correctness Verdict: Correct

Semantic Alignment:
The implementation matches the semantic intent: it inspects the released-flags bitmask for the click bit. It is consistent with every sibling is_input__*_released function (e.g. is_input__forward_released, is_input__consume_released), all of which test input_flags__released against their respective INPUT_* mask.

Implementation Correctness:
Type compatibility — input_flags__released has type Input_Flags__u32 (uint32_t); INPUT_CLICK is an integer constant expression. The bitwise AND yields an int result implicitly converted to bool (non-zero → true, zero → false), which is well-defined C. No truncation or data loss occurs.
No undefined behavior — no pointer arithmetic, no null dereference, no type punning, no out-of-bounds access.
No validation is needed — this is a low-level, header-inline query. Consistent with the engine's convention, none of the sibling is_input__*_released functions null-check; ensuring p_input is valid is the caller's responsibility. (This is not an init/initialize/reset function, so the Lavender "initialization ≠ RAII" distinction does not apply; the function performs no initialization or resource acquisition.)

Side Effects:
No side effects — the only observable effect is a read of p_input->input_flags__released.
