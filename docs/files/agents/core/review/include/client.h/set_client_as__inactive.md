set_client_as__inactive — core/include/client.h, lines 78-82

Clears only the active flag from the client's flag bitmask, leaving all other flags intact.

Pre-conditions:
1. p_client must be a non-null pointer to a writable Client object.

Post-conditions:
1. p_client->client_flags__u16 has CLIENT_FLAG__IS_ACTIVE cleared (bit 0 = 0).
2. All other flag bits (IS_LOADED bit 1, IS_FAILED_TO_LOAD bit 2, IS_SAVING bit 3, IS_FRESH bit 4) are preserved unchanged.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of marking a client as inactive. It clears exactly one bit (IS_ACTIVE) and preserves all others. The bitwise operation p_client->client_flags__u16 &= ~CLIENT_FLAG__IS_ACTIVE is the canonical C idiom for clearing a single bit. No struct field is omitted or reordered.

Implementation Correctness:
Type compatibility — client_flags__u16 is u16, CLIENT_FLAG__IS_ACTIVE is BIT(0) = (1U) << 0 = 1U. The ~ operator inverts 1U to 0xFFFFFFFE (on a 32-bit int). The &= promotes u16 to int, ANDs with ~1U, and stores the result back to u16. Bit 0 is correctly cleared; all other u16 bits are preserved because the inverted mask has 1s in all positions except bit 0. No truncation affects any other bit. No implicit conversions beyond standard integer promotions.
No undefined behavior — no pointer arithmetic, no null dereference (caller responsibility), no type punning, no out-of-bounds access.
No validation — consistent with the low-level setter pattern. The caller is responsible for ensuring p_client is valid.

Side Effects:
Mutates p_client->client_flags__u16. Specifically, only the CLIENT_FLAG__IS_ACTIVE bit (bit 0) is cleared. No other client fields are touched. No callee calls.
