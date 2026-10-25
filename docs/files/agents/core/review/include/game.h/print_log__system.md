print_log__system — core/source/game.c

Writes a C-string into the system Log's next available Message slot and advances the log's message pointer.

Pre-conditions:
1. p_game must be a non-null pointer to a properly initialized Game object. Specifically, initialize_game(...) must have been called so that log__system has been initialized via initialize_log(...).
2. cstr must be a non-null pointer to a valid null-terminated C-string. It is passed directly to put_cstr_into__message(...) which iterates over it byte-by-byte until a null terminator is found.

Post-conditions:
1. p_game->log__system is mutated: the string cstr is written into the Message at p_log->p_next_message. If the message body (fixed at MESSAGE_MAX_LENGTH_OF = 96 bytes) cannot hold the entire string, it is truncated.
2. The log's p_next_message pointer is advanced (with wrapping) via flush_message_into__log(...), and the newly pointed-to Message is re-initialized to a clean state. If the oldest message pointer catches up to the next message pointer (ring buffer full), the oldest message pointer is also advanced.
3. Returns true if the message body was full (i.e., the string was truncated), false if the entire string fit without truncation. This return value is the return of put_cstr_into__message(...).

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully fulfills the semantic intent of writing a log entry to the system log. The function follows the exact same pattern as print_log__global and print_log__local, differing only in which Log accessor is used (get_p_log__system_from__game). The call sequence — put_cstr_into__message on the next message, then flush_message_into__log — correctly writes the string and advances the ring buffer. No semantic drift is present.

Implementation Correctness:
Type compatibility — p_game is Game* which matches the parameter type of get_p_log__system_from__game(Game *p_game). cstr is char* which matches the parameter type of put_cstr_into__message(Message *p_message, char *cstr). No implicit conversions or truncation.
Undefined behavior — no broken pointer arithmetic, no out-of-bounds access, no type punning. The function relies on p_game and cstr being valid, but this is consistent with the codebase convention where validation is the caller's responsibility (e.g., put_cstr_into__message itself does not validate cstr). No null dereference occurs as long as pre-conditions are met.
Validation — no validation is performed within the function itself. This is appropriate for a low-level logging utility; the caller is responsible for ensuring p_game and cstr are valid. The debug-mode null check in put_cstr_into__message guards against a null p_message but not a null cstr.

Side Effects:
Mutates p_game->log__system: writes the string into the current message slot and advances the log's internal message pointers (p_next_message and potentially p_oldest_message) via flush_message_into__log(...). No other observable side effects.
