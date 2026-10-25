set_client_as__active — core/include/client.h, lines 160-167

Clears the failed-to-load, loaded, and saving flags, then sets the active flag on the client.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.

Post-conditions:
1. p_client->client_flags__u16 has CLIENT_FLAG__IS_ACTIVE cleared-then-set, so IS_ACTIVE is set (bit 0 = 1).
2. p_client->client_flags__u16 has CLIENT_FLAG__IS_LOADED cleared (bit 1 = 0).
3. p_client->client_flags__u16 has CLIENT_FLAG__IS_FAILED_TO_LOAD cleared (bit 2 = 0).
4. p_client->client_flags__u16 has CLIENT_FLAG__IS_SAVING cleared (bit 3 = 0).
5. CLIENT_FLAG__IS_FRESH (bit 4) is preserved — set_client_as__active does not touch it.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of marking a client as active. It clears three mutually-exclusive lifecycle flags (loaded, failed-to-load, saving) before setting active, which is a sensible transition — a client moving into the active state should not simultaneously carry a loaded, failed, or saving state. No flag is omitted or accidentally reordered.

However, one semantic observation: set_client_as__active clears IS_LOADED but set_client_as__loaded does NOT clear IS_ACTIVE. This creates an asymmetry — calling set_client_as__loaded on an already-active client would leave both IS_ACTIVE and IS_LOADED set, whereas calling set_client_as__active on a loaded client clears IS_LOADED. This is likely intentional (active and loaded are distinct lifecycle states), but is worth noting.

Implementation Correctness:
Type compatibility — client_flags__u16 is a u16, CLIENT_FLAG__IS_ACTIVE is BIT(0) = (1U) << 0 = 1U. The |= operation promotes u16 to int, ORs, and stores the result back to u16. No truncation affects the IS_ACTIVE bit. No implicit conversions beyond standard integer promotions.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access.
No validation — consistent with the low-level setter pattern. The caller is responsible for ensuring p_client is valid.

Side Effects:
Mutates p_client->client_flags__u16. The mutation is performed directly (bitwise OR for IS_ACTIVE) and indirectly via three callee calls (set_client_as__NOT_failed_to_load, set_client_as__NOT_loaded, set_client_as__NOT_saving), each of which clears a single flag bit. No other client fields are touched.
