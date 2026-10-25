get_last_symbol_of__input_for__writing — core/include/input/input.h

Returns the last symbol consumed from the Input writing buffer.

Pre-conditions:
1. p_input must be a non-null pointer to a valid, initialized Input struct.

Post-conditions:
1. Returns p_input->last_symbol, an unsigned char holding the most recent symbol that was polled (consumed) from the writing buffer via poll_input_for__writing. After initialize_input the value is 0.

Correctness Verdict: Correct

Semantic Alignment:
The implementation directly reads p_input->last_symbol and returns it, faithfully exposing the field that poll_input_for__writing writes (input.c:13: p_input->last_symbol = symbol). The accessor itself is a correct, minimal read.

CAVEAT — semantic tension across the writing-buffer lifecycle: The last_symbol field is written ONLY by poll_input_for__writing (input.c:13) and zeroed by initialize_input; it is NOT updated by buffer_input_for__writing (the producer path, input.c:22-29). This conflicts with the test writing_buffer__last_symbol_returns_most_recent (test_suite_input_input.c:869), which buffers 'X' then 'Y' via buffer_input_for__writing and asserts get_last_symbol_of__input_for__writing returns 'Y'. Because buffering never sets last_symbol, it remains 0 there, so that assertion cannot hold against the current implementation. Two readings of intent exist: (A) last_symbol = "last polled/consumed symbol" (consistent with poll_input_for__writing and the sdl_input.c:285 hold-timer reset usage, which detects a NEW symbol vs. the last); (B) last_symbol = "most recently buffered symbol" (matching the test). The accessor under review faithfully returns the field, so it is correct, but the broader writing-buffer contract should be reconciled — either buffer_input_for__writing must update last_symbol (making reading A and B agree), or the test/spec must clarify the intended semantic.

Implementation Correctness:
Type compatibility — the return type (unsigned char) and the field last_symbol (defines.h:1180, unsigned char) match exactly; no implicit conversion or truncation. Undefined behavior — no pointer arithmetic; no null dereference (the caller must supply a valid p_input, consistent with every other inline accessor in this header); no type punning; no out-of-bounds access. Validation — no validation is appropriate for this low-level inline accessor; ensuring p_input validity is the caller's responsibility, matching the file's conventions.

Side Effects:
No side effects. The function is a pure read accessor; it only reads p_input->last_symbol and returns it without modifying any state.
