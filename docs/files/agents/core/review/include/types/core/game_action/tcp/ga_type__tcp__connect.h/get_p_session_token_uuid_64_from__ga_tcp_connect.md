get_p_session_token_uuid_64_from__ga_tcp_connect — core/include/types/core/game_action/tcp/ga_type__tcp__connect.h

Returns a pointer to the session_token__uuid_u64 field of the GA_TCP_Connect payload within a Game_Action.

Pre-conditions:
1. p_game_action must be a non-null pointer to a valid, writable Game_Action object.
2. The Game_Action's _ga_payload_union must currently hold a GA_TCP_Connect payload (i.e., the caller must ensure the action kind is GA_TCP_Connect). The function performs no kind check.

Post-conditions:
1. Returns a non-null pointer to the session_token__uuid_u64 field inside the Game_Action's payload union, cast as a GA_TCP_Connect. The returned pointer references memory owned by p_game_action.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent: it extracts a pointer to the session_token__uuid_u64 field from the Game_Action's payload union by casting it to the GA_TCP_Connect type. The field exists in the GA_TCP_Connect struct and the cast is consistent with the macro-based payload extraction pattern used throughout the codebase. No fields are omitted or reordered.

Implementation Correctness:
Type compatibility — `Identifier__u64 *` is the return type and `session_token__uuid_u64` is declared as `Identifier__u64` in the GA_TCP_Connect struct, so the pointer type matches exactly. No implicit conversions or truncation.
Undefined behavior — the function uses the `GET_P_GAME_ACTION_PAYLOAD_AS_P` macro which casts the `_ga_payload_union` to `GA_TCP_Connect*` and takes the address of a field within it. This is valid as long as the union actually holds a GA_TCP_Connect (pre-condition #2). If the pre-condition is violated, accessing the wrong union member is undefined behavior. No null dereference occurs if p_game_action is non-null. No out-of-bounds access.
Validation — no validation is performed. This is consistent with the low-level accessor pattern used across the codebase (e.g., the sibling get_session_token_uuid_64_from__ga_tcp_connect function). The caller is responsible for ensuring p_game_action is valid and that the payload kind matches.

Side Effects:
No side effects — the function is a pure accessor. It does not modify any state; it only reads the pointer to the Game_Action struct and returns an address within it.
