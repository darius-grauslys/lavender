set_client_as__saving — core/include/client.h, lines 146-150

Sets (asserts) the CLIENT_FLAG__IS_SAVING bit in the client's flag field, indicating the client is mid-save, while preserving all other flags.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.
2. p_client->client_flags__u16 is a Client_Flags__u16 (u16); no range constraint on the existing value.

Post-conditions:
1. The CLIENT_FLAG__IS_SAVING (BIT(3)) bit in p_client->client_flags__u16 is set (set to 1).
2. All other bits in p_client->client_flags__u16 are unchanged.
3. No other field of the Client struct or any other object is modified.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to assert the "saving" status flag, marking the client as mid-save. The implementation uses the standard C idiom `flags |= BIT(n)`, which is exactly correct for setting a single bit. CLIENT_FLAG__IS_SAVING is BIT(3) = (1U << 3), well within the 16-bit range of client_flags__u16. No flags are erroneously set or cleared; the operation is a pure bit-set with no side effects on adjacent or distant bits. This is the complement of set_client_as__NOT_saving, which clears the same bit — the pair is consistent.

Implementation Correctness:
Type compatibility — p_client->client_flags__u16 is Client_Flags__u16 (u16 / uint16_t). CLIENT_FLAG__IS_SAVING is BIT(3) = (1U << 3), which is unsigned int (at least 16 bits). The compound assignment |= promotes the u16 to unsigned int via integer promotion, performs the OR, and truncates back to u16 on assignment. Since only bits 0-3 are used for client flags, the truncation of the upper bits has no effect. No implicit narrowing, no truncation of meaningful data.
Undefined behavior — no pointer arithmetic, no null dereference in the code itself, no type punning, no out-of-bounds access. (A null p_client would cause a crash, but null-checking is deliberately omitted for these low-level inline setters.)
Validation — no validation is present; this is consistent with the module's pattern for all set_client_as__* inlines (e.g., set_client_as__NOT_failed_to_load, set_client_as__NOT_loaded, set_client_as__NOT_saving, set_client_as__active, set_client_as__loaded, set_client_as__failed_to_load), none of which guard against null. Validation is the caller's responsibility.

Side Effects:
Mutates p_client->client_flags__u16 by setting the CLIENT_FLAG__IS_SAVING bit. No other state is touched.
