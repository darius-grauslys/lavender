print_log__local — core/source/game.c, lines 659-667

Appends a null-terminated string to the local log's next available message slot and advances the log's internal pointers.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game object (i.e., initialize_game has been called so that p_game->log__local is properly initialized).
2. cstr must be a non-null pointer to a null-terminated char array (string). If cstr is null, put_cstr_into__message will dereference it, causing undefined behavior.
3. The local Log (p_game->log__local) must have been initialized via initialize_log (called during initialize_game). After initialization, p_log->p_next_message points to &p_log->messages[0], so get_next_p_message_in__log returns a valid non-null Message pointer.

Post-conditions:
1. The Message at p_log->p_next_message (before flushing) has the contents of cstr written into its message__body via put_cstr_into__message. If the string exceeds MESSAGE_MAX_LENGTH_OF (96), the body is filled to capacity and remaining characters are discarded.
2. The log's p_next_message pointer is advanced to the next Message slot (wrapping around to messages[0] if necessary) via flush_message_into__log, and that new slot is initialized to a clean state.
3. If p_oldest_message equals the new p_next_message (i.e., the log has wrapped around and the oldest message would be overwritten), p_oldest_message is also advanced to prevent losing unread messages.
4. The return value is true if the message body was full (string was truncated to fit MESSAGE_MAX_LENGTH_OF), and false if the entire string fit without truncation.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements the semantic intent of "print a local log message": it writes the provided string into the next available message slot in the local log, then flushes (advances pointers) so subsequent calls use a fresh slot. The behavior matches the sibling functions print_log__global and print_log__system, which follow the identical pattern using their respective Log accessors.

Implementation Correctness:
Type compatibility — get_p_log__local_from__game returns Log *, which is passed to get_next_p_message_in__log (expects Log *) and flush_message_into__log (expects Log *). Both return/use Message *. put_cstr_into__message expects (Message *, char *), and the arguments match exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic within this function (all pointer arithmetic is encapsulated in poll_message_pointer_for__wrapping, which correctly bounds-checks against MESSAGE_MAX_QUANTITY_OF). No null dereference occurs as long as preconditions hold (p_game non-null, cstr non-null, log initialized). No type punning. No out-of-bounds access — put_cstr_into__message bounds-checks via put_char_into__message which checks index_of__body >= MESSAGE_MAX_LENGTH_OF before writing.
No validation is needed within this function — it is a thin wrapper that delegates to lower-level functions. The caller is responsible for ensuring p_game and cstr are valid. This is consistent with the codebase pattern where inline accessors and print_log_* functions do not perform null checks.

Side Effects:
Mutates p_game->log__local: writes characters into the current message body, advances p_next_message to the next slot (with wrap-around), initializes the new message slot to a clean state, and potentially advances p_oldest_message if the log has wrapped around. No other state is modified.
