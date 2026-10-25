is_client__loaded — core/include/client.h, lines 109-113

Queries whether a Client has completed loading by checking the IS_LOADED flag.

Pre-conditions:
1. p_client may be NULL; the function handles this safely via short-circuit evaluation.
2. p_client may be non-NULL; in this case it must point to a valid, initialized Client struct.

Post-conditions:
1. Returns true if p_client is non-NULL and the CLIENT_FLAG__IS_LOADED bit is set in client_flags__u16.
2. Returns false if p_client is NULL or if the IS_LOADED bit is not set.
3. No state is mutated; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly fulfills its semantic intent: it returns whether the client has been marked as loaded. The CLIENT_FLAG__IS_LOADED flag is set by set_client_as__loaded (line 117), which is called in m_process__deserialize_client__default (client.c, line 465) after successful deserialization. The single usage site in game_action__world__load_client.c (line 104) relies on this return value to decide whether to proceed with client teleport logic, which is the correct semantic usage.

Implementation Correctness:
Type compatibility — p_client is Client *, which is the expected parameter type. client_flags__u16 is Client_Flags__u16 (typedef'd as u16). CLIENT_FLAG__IS_LOADED is BIT(1), an integer constant. The bitwise AND between a u16 and an int produces an int, which is then implicitly converted to bool for the return. No implicit truncation or conversion issues arise because the result is either 0 or a power of two, both safely representable as bool.
Operator precedence — the expression p_client && p_client->client_flags__u16 & CLIENT_FLAG__IS_LOADED is parsed as p_client && (p_client->client_flags__u16 & CLIENT_FLAG__IS_LOADED) because bitwise & binds tighter than logical && in C. This is the intended behavior: the NULL check short-circuits before dereferencing. While technically correct, the lack of explicit parentheses around the bitwise expression is a latent readability hazard; the codebase consistently uses this same pattern across all is_client__* predicate functions (lines 88, 111, 134, 141), so it is stylistically consistent.
Undefined behavior — none. If p_client is NULL, the && short-circuits and p_client->client_flags__u16 is never evaluated. No pointer arithmetic, type punning, or out-of-bounds access occurs.
Validation — no validation is needed; the NULL check is built into the expression itself, and this is the established convention for all client flag predicate functions in this header.

Side Effects:
No side effects. The function reads only the p_client pointer and its client_flags__u16 field without modifying any state.
