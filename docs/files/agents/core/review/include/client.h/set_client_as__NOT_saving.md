set_client_as__NOT_saving — core/include/client.h, lines 153-157

Clears the CLIENT_FLAG__IS_SAVING bit from the client's flag field while preserving all other flags.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.
2. p_client->client_flags__u16 is a Client_Flags__u16 (u16); no range constraint on the existing value.

Post-conditions:
1. The CLIENT_FLAG__IS_SAVING (BIT(3)) bit in p_client->client_flags__u16 is cleared (set to 0).
2. All other bits in p_client->client_flags__u16 are unchanged.
3. No other field of the Client struct or any other object is modified.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent is to clear the "saving" status flag, indicating the client is no longer mid-save. The implementation uses the standard C idiom `flags &= ~BIT(n)`, which is exactly correct for clearing a single bit. CLIENT_FLAG__IS_SAVING is BIT(3) = (1U << 3), well within the 16-bit range of client_flags__u16. No flags are erroneously set or cleared; the operation is a pure bit-clear with no side effects on adjacent or distant bits.

Implementation Correctness:
Type compatibility — p_client->client_flags__u16 is Client_Flags__u16 (u16 / uint16_t). CLIENT_FLAG__IS_SAVING is BIT(3) = (1U << 3), which is unsigned int (at least 16 bits). The compound assignment &= promotes the u16 to unsigned int via integer promotion, performs the AND, and truncates back to u16 on assignment. Since only bits 0-3 are used for client flags, the truncation of the upper all-ones bits of ~BIT(3) has no effect. No implicit narrowing, no truncation of meaningful data.
Undefined behavior — no pointer arithmetic, no null dereference in the code itself, no type punning, no out-of-bounds access. (A null p_client would cause a crash, but null-checking is deliberately omitted for these low-level inline setters.)
Validation — no validation is present; this is consistent with the module's pattern for all set_client_as__* inlines (e.g., set_client_as__NOT_failed_to_load, set_client_as__NOT_loaded, set_client_as__active, set_client_as__loaded, set_client_as__failed_to_load), none of which guard against null. Validation is the caller's responsibility.

Side Effects:
Mutates p_client->client_flags__u16 by clearing the CLIENT_FLAG__IS_SAVING bit. No other state is touched.
