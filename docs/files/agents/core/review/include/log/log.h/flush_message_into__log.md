flush_message_into__log — core/source/log/log.c

Advances the log's circular buffer write pointer to the next slot, initializes (clears) the Message at that slot, and if the buffer is full, advances the oldest-message pointer to drop the oldest entry.

Pre-conditions:
1. p_log must be a non-null pointer to a writable Log object.
2. The Log must have been initialized via initialize_log (so p_next_message points to a valid Message slot within the messages array, and p_oldest_message is either NULL or a valid pointer within the array).

Post-conditions:
1. p_log->p_next_message is advanced by one slot, wrapping around to &messages[0] if it was at the last slot in the array.
2. The Message at the new p_log->p_next_message is initialized (all fields cleared/reset to defaults via initialize_message).
3. If the buffer was full (p_oldest_message == p_next_message after advancing p_next_message), p_log->p_oldest_message is also advanced by one slot (with wrapping), effectively dropping the oldest message from the buffer.
4. If this is the first call after initialize_log (p_oldest_message was NULL), p_oldest_message is set to &messages[0] by poll_message_pointer_for__wrapping.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly fulfills the semantic intent of flushing a new message slot into the log's circular buffer. The function uses poll_message_pointer_for__wrapping to handle wrap-around of the write pointer (p_next_message), then calls initialize_message to clear the Message at the new position — consistent with Lavender's pattern of "initialization" meaning cleanup to initial conditions (not RAII resource acquisition). When the buffer is full (all MESSAGE_MAX_QUANTITY_OF slots occupied), the oldest message pointer (p_oldest_message) is advanced to drop the oldest entry, making room for new messages. This is a standard ring-buffer flush pattern.

Implementation Correctness:
Type compatibility — p_log is Log *, matching the parameter type. p_log->p_next_message is Message *, which matches the Message * parameter of initialize_message. No implicit conversions or truncation.
No undefined behavior — no null dereference (assuming pre-conditions are met), no out-of-bounds access (wrap-around is handled by poll_message_pointer_for__wrapping which checks pointer arithmetic against MESSAGE_MAX_QUANTITY_OF and resets to &messages[0]), no type punning.
Validation — no validation is needed within this function; it is a low-level buffer management routine. The caller is responsible for ensuring p_log is valid and initialized.

Side Effects:
- Mutates p_log->p_next_message (advanced by one slot with wrapping).
- Mutates p_log->p_oldest_message (set to &messages[0] on first call after initialization, or advanced by one slot when the buffer is full).
- Mutates the Message at the new p_next_message position (via initialize_message, which clears title/body arrays and resets length/index fields).
