print_log__global — core/source/game.c

Appends a C string as a new message to the global log, then advances the log's message pointer.

Pre-conditions:
1. p_game must be a non-null pointer to a valid, initialized Game object. The Game struct must have its log__global member properly initialized (via initialize_log or initialize_game).
2. cstr must be a non-null pointer to a null-terminated C string. The string may be empty (zero-length).
3. The global Log (p_game->log__global) must have its p_next_message pointing to a valid Message slot within the messages array (established by initialize_log or a prior flush_message_into__log call).

Post-conditions:
1. The C string pointed to by cstr is copied into the body of the Message at p_log->p_next_message (the slot that was current before flushing). If the string exceeds MESSAGE_MAX_LENGTH_OF (96) characters, the message body is truncated.
2. p_log->p_next_message is advanced to the next Message slot (with circular wrapping at MESSAGE_MAX_QUANTITY_OF). The Message at the new p_next_message position is reinitialized to a clean/empty state.
3. If p_log->p_oldest_message had caught up to p_next_message (i.e., the log was full), p_oldest_message is also advanced to drop the oldest message, maintaining the circular buffer invariant.
4. The return value is true if the message body was full and the string was truncated; false if the entire string was written successfully.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the intent of "printing a log message to the global log." It writes the string into the current next-message slot, then flushes (advances the pointer and prepares the next slot). The return value correctly propagates the truncation status from put_cstr_into__message. The implementation matches the semantic intent with no drift.

Implementation Correctness:
Type compatibility — all types match exactly: get_p_log__global_from__game returns Log * (matching flush_message_into__log's parameter), get_next_p_message_in__log returns Message * (matching put_cstr_into__message's first parameter), and char * is passed directly to put_cstr_into__message's second parameter. No implicit conversions or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference (pre-conditions require valid pointers), no type punning, no out-of-bounds access. The circular buffer wrapping logic in flush_message_into__log and poll_message_pointer_for__wrapping correctly handles boundary conditions.
Validation — the function does not perform null checks on p_game or cstr, which is consistent with the codebase pattern (callee validation is minimal; caller responsibility is assumed). The debug check for p_message null is performed inside put_cstr_into__message. The lack of null checks for p_game and cstr is acceptable given the codebase conventions.
Minor inefficiency — get_p_log__global_from__game(p_game) is called twice (once for getting the message, once for flushing). This is a trivial inline accessor returning &p_game->log__global, so the redundancy has no semantic impact, only a negligible performance cost.

Side Effects:
Mutates p_game->log__global: writes the C string into the current p_next_message Message body, advances p_next_message (with circular wrapping), reinitializes the new p_next_message Message, and potentially advances p_oldest_message if the log was full. The commented-out PLATFORM_update_log__global(p_game) call is not executed.
