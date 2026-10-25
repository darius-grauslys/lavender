set_client_as__failed_to_load — core/include/client.h, lines 93-98

Resets all client flags to none, then sets only the failed-to-load flag.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.

Post-conditions:
1. p_client->client_flags__u16 is set to CLIENT_FLAGS__NONE (0), then CLIENT_FLAG__IS_FAILED_TO_LOAD is set via bitwise OR.
2. After the function returns, only CLIENT_FLAG__IS_FAILED_TO_LOAD (bit 2) is set; all other flags (IS_ACTIVE bit 0, IS_LOADED bit 1, IS_SAVING bit 3, IS_FRESH bit 4) are cleared.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of marking a client as having failed to load. The two-step approach (clear all flags, then set one) is equivalent to a direct assignment p_client->client_flags__u16 = CLIENT_FLAG__IS_FAILED_TO_LOAD, but is more explicit and readable. No flag is omitted — all five defined flags are accounted for (only IS_FAILED_TO_LOAD survives). No reordering occurs.

One semantic observation: this function clears IS_FRESH (bit 4) along with all other flags. If a client was fresh and then failed to load, the fresh attribute is lost. This may be intentional (a fresh client that failed to load is no longer "fresh" in the lifecycle sense), but is worth noting.

Implementation Correctness:
Type compatibility — client_flags__u16 is u16, CLIENT_FLAGS__NONE is 0 (int), CLIENT_FLAG__IS_FAILED_TO_LOAD is BIT(2) = (1U) << 2 = 4U. The |= promotes u16 to int, ORs, and stores the result back to u16. The result is 4 (well within u16 range). No truncation or implicit conversion issues.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access.
No validation — consistent with the low-level setter pattern. The caller is responsible for ensuring p_client is valid.

Side Effects:
Mutates p_client->client_flags__u16. All five flag bits are affected: IS_FAILED_TO_LOAD is set; IS_ACTIVE, IS_LOADED, IS_SAVING, and IS_FRESH are all cleared. No other client fields are touched.
