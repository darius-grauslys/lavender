set_client_as__loaded — core/include/client.h, lines 117-122

Clears the failed-to-load flag, then sets the loaded flag on the client, leaving other flags intact.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.

Post-conditions:
1. p_client->client_flags__u16 has CLIENT_FLAG__IS_FAILED_TO_LOAD cleared (bit 2 = 0), via the callee set_client_as__NOT_failed_to_load.
2. p_client->client_flags__u16 has CLIENT_FLAG__IS_LOADED set (bit 1 = 1), via direct bitwise OR.
3. All other flag bits (IS_ACTIVE bit 0, IS_SAVING bit 3, IS_FRESH bit 4) are preserved unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of marking a client as loaded. Clearing the failed-to-load flag before setting loaded is semantically correct — a successfully loaded client should not carry a failed-to-load status. The IS_LOADED bit is set via the standard |= idiom. No flag is omitted or accidentally reordered.

One semantic observation: set_client_as__loaded does NOT clear IS_ACTIVE, IS_SAVING, or IS_FRESH. This means a client can simultaneously be loaded and active, or loaded and saving, or loaded and fresh. This is in contrast to set_client_as__active, which clears IS_LOADED. The asymmetry is likely intentional (loaded is a data-state, active is a connection-state, and they are not mutually exclusive), but is worth noting.

Implementation Correctness:
Type compatibility — client_flags__u16 is u16, CLIENT_FLAG__IS_LOADED is BIT(1) = (1U) << 1 = 2U. The |= promotes u16 to int, ORs, and stores the result back to u16. Bit 1 is correctly set. No truncation or implicit conversion issues.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access.
No validation — consistent with the low-level setter pattern. The caller is responsible for ensuring p_client is valid.

Side Effects:
Mutates p_client->client_flags__u16. The IS_FAILED_TO_LOAD bit is cleared (via callee set_client_as__NOT_failed_to_load) and the IS_LOADED bit is set (direct). No other client fields are touched. The indirect mutation via set_client_as__NOT_failed_to_load only affects the IS_FAILED_TO_LOAD bit.
