poll_message_pointer_for__wrapping — core/source/log/log.c

Advances a message pointer by one position, wrapping it to the beginning of the log's message array if it exceeds the array bounds.

Pre-conditions:
1. p_log must be non-null and point to a valid, initialized Log struct.
2. p_message_ptr must be non-null and point to a valid Message* that references an element within p_log->messages (or one-past-the-end, which is valid for pointer arithmetic).
3. p_log->messages must be a valid array of MESSAGE_MAX_QUANTITY_OF (32) Message elements.

Post-conditions:
1. *p_message_ptr is advanced by one position (incremented by 1).
2. If the advanced pointer exceeds the bounds of p_log->messages (i.e., points at or past messages[MESSAGE_MAX_QUANTITY_OF]), it is wrapped to &p_log->messages[0].
3. If p_log->p_oldest_message was NULL (sentinel for "empty log"), it is set to &p_log->messages[0] — this is an initialization side effect that does not belong in this function (see Semantic Alignment).

Correctness Verdict: Incorrect

Semantic Alignment:
The function's name, "poll_message_pointer_for__wrapping", indicates its semantic intent: to advance (poll) a message pointer and handle circular-buffer wrapping. The implementation partially fulfills this intent but introduces two problems:

1. Side effect mismatch: The function has an unrelated side effect of initializing p_log->p_oldest_message when it is NULL. In Lavender semantics, "initialization" means resetting a struct to its initial/default conditions — it is NOT RAII-style resource acquisition. Setting p_oldest_message from NULL to &messages[0] is a state transition (marking the log as non-empty), which is an initialization concern, not a wrapping concern. This side effect is semantically misplaced in a function whose purpose is wrapping. It also causes issues for the get_p_message_from__log call site, where modifying p_log->p_oldest_message during a read operation is inappropriate.

2. Skipped wrapping check: The early `return` when p_oldest_message is NULL causes the wrapping check (the `if (p_message - p_log->messages >= MESSAGE_MAX_QUANTITY_OF)` block) to be skipped entirely. This means that if the pointer has advanced past the end of the messages array, it will NOT be wrapped. While this does not manifest in the current call sites — because p_oldest_message is NULL only after initialize_log sets p_next_message to &messages[0], so the first advance goes to messages[1] which is in bounds — it is a latent logic error. If the function were called with a pointer already near the end of the array while p_oldest_message is NULL, the pointer would remain out-of-bounds.

Recommended fix: Move the p_oldest_message initialization to the caller (flush_message_into__log), so this function purely handles pointer advancement and wrapping. The wrapping check should always be performed after advancing the pointer, regardless of the state of p_oldest_message.

Implementation Correctness:
Type compatibility: All types are correct. p_message_ptr is Message**, p_message is Message*, p_log is Log*. The expression `p_message - p_log->messages` is valid pointer arithmetic (both are Message*). The comparison `>= MESSAGE_MAX_QUANTITY_OF` (32) is valid. No implicit conversions or truncation.

Undefined behavior: The (*p_message_ptr)++ operation is valid pointer arithmetic if *p_message_ptr points within or one-past-the-end of the messages array. The p_message - p_log->messages subtraction is also valid. No null dereference (p_log and p_message_ptr are assumed non-null by the caller). No type punning. No out-of-bounds array access. However, if *p_message_ptr is NULL (which could occur if p_oldest_message is NULL and the function is called with &p_oldest_message), then (*p_message_ptr)++ would be incrementing a null pointer, which is undefined behavior — though this does not occur in the current call sites.

Validation: The function performs no validation of its parameters. This is appropriate for a low-level internal helper — the caller is responsible for ensuring p_log and p_message_ptr are valid.

Side Effects:
1. Mutates *p_message_ptr: the pointed-to Message* is advanced by one position, and wrapped to &p_log->messages[0] if it exceeds the array bounds.
2. Mutates p_log->p_oldest_message: sets it to &p_log->messages[0] when it was NULL. This side effect is inappropriate for a wrapping function and represents a semantic mismatch (see Semantic Alignment).
