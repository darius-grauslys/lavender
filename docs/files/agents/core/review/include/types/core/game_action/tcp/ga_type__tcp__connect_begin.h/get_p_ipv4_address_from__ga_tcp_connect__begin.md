get_p_ipv4_address_from__ga_tcp_connect__begin — core/include/types/core/game_action/tcp/ga_type__tcp__connect_begin.h

Returns a pointer to the ipv4_address field of the GA_TCP_Connect__Begin payload within a Game_Action.

Pre-conditions:
1. p_game_action must be a non-null pointer to a valid Game_Action object.
2. The Game_Action's _ga_payload_union must contain a GA_TCP_Connect__Begin payload (i.e., the game action kind must be GA_TCP_Connect__Begin). This is the caller's responsibility.

Post-conditions:
1. Returns a non-null pointer to the IPv4_Address field within the GA_TCP_Connect__Begin payload.
2. No mutation of the Game_Action or its payload occurs; the function is read-only.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves a pointer to the ipv4_address field from the GA_TCP_Connect__Begin payload. It uses the GET_P_GAME_ACTION_PAYLOAD_AS_P macro to cast the _ga_payload_union to a GA_TCP_Connect__Begin pointer, then takes the address of the ipv4_address field. This matches the semantic intent of providing access to the IPv4 address within the TCP connect begin game action.

Implementation Correctness:
Type compatibility — the function returns IPv4_Address* which matches the type of the ipv4_address field in GA_TCP_Connect__Begin. No implicit conversions or truncation.
Undefined behavior — no broken pointer arithmetic, no null dereference (assuming pre-conditions are met), no type punning, no out-of-bounds access.
Validation — no validation is performed, which is appropriate for this low-level accessor function. The caller is responsible for ensuring p_game_action is valid and contains the correct payload type.

Side Effects:
No side effects — the function is a pure accessor that reads from the Game_Action's payload and returns a pointer to a field within it. No mutation of any state occurs.
