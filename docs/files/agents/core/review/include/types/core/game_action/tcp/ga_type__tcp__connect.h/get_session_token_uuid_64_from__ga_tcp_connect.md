get_session_token_uuid_64_from__ga_tcp_connect — core/include/types/core/game_action/tcp/ga_type__tcp__connect.h

Retrieves the 64-bit session token UUID from a Game_Action whose payload union holds a GA_TCP_Connect struct.

Pre-conditions:
1. p_game_action must be a non-null pointer to a valid Game_Action object.
2. The caller must ensure that the Game_Action's _ga_payload_union currently holds a GA_TCP_Connect payload (the function performs no type-tag check; it is the caller's responsibility).

Post-conditions:
1. Returns the session_token__uuid_u64 field (of type Identifier__u64 / uint64_t) from the GA_TCP_Connect payload stored in p_game_action->_ga_payload_union.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves the session_token__uuid_u64 field from the GA_TCP_Connect struct. The struct GA_TCP_Connect has exactly one field — session_token__uuid_u64 of type Identifier__u64 — and the function accesses that field and returns it by value. The return type (Identifier__u64) matches the field type exactly. No field is omitted or misaccessed. The GET_P_GAME_ACTION_PAYLOAD_AS_P macro casts the _ga_payload_union to a GA_TCP_Connect* pointer, which is the established payload-access pattern used throughout the engine for Game_Action payloads.

Implementation Correctness:
Type compatibility — the return type (Identifier__u64, which is uint64_t) matches the struct field type (Identifier__u64) exactly; no implicit conversions or truncation.
No undefined behavior — the function does not perform pointer arithmetic, does not dereference a null pointer (assuming pre-condition 1 holds), does not engage in type punning beyond the union cast that is the established engine pattern, and does not access out of bounds. The macro expands to ((GA_TCP_Connect*)&p_game_action->_ga_payload_union)->session_token__uuid_u64, which is a straightforward union pointer cast followed by member access.
No validation is needed — this is a low-level accessor. The caller is responsible for ensuring p_game_action is valid and contains the correct payload type.

Side Effects:
No side effects — this is a pure accessor function. It reads from the Game_Action struct and returns a value by copy; it does not mutate any state.
