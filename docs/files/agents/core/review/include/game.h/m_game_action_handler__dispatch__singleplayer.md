m_game_action_handler__dispatch__singleplayer — core/source/game.c (declaration: lines 64-67, implementation: lines 757-766)

Adapter that routes a Game_Action through the single-client dispatch path by delegating to dispatch_game_action_for__client with a NULL TCP_Socket_Manager, suppressing all network transmission.

Pre-conditions:
1. p_game must be a non-null pointer to a Game whose action-logic table and process manager have been initialized (initialize_game has run). dispatch_game_action_for__client dereferences p_game immediately via get_p_process_manager_from__game and get_p_game_action_logic_table_from__game.
2. p_client must be a non-null pointer to a Client. dispatch_game_action_for__client dereferences it unconditionally at line 323 via GET_UUID_P(p_client) to stamp uuid_of__client__u32; there is no null guard on p_client in the callee. In singleplayer this is the local client (slot 0), which is always present once a session runs.
3. p_game_action must be a non-null pointer to a writable Game_Action. Unlike p_client and p_game, this one IS null-guarded in the callee (client.c:303-306), so a null p_game_action yields a safe false return rather than a crash.

Post-conditions:
1. Returns the bool result of dispatch_game_action_for__client(p_client, p_game, NULL, p_game_action).
2. The Game_Action is sanitized outbound (santize_game_action__outbound), its uuid_of__client__u32 field is stamped with the client's UUID, and a process may be dispatched or invoked via the action's logic entry — exactly as in the multiplayer unicast path.
3. Because the TCP_Socket_Manager argument is NULL (the literal 0 at line 764), dispatch_game_action_for__client short-circuits at line 376 (`if (!p_tcp_socket_manager || is_game_action__local(p_game_action)) return true;`) and performs no TCP send. This is the defining singleplayer behavior: the action is processed locally and never serialized to a socket.
4. The function itself performs no direct mutation of p_game; all mutation (uuid stamping, flag toggling, outbound pool copy) is performed by the delegated callee.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its intent exactly. This is the default dispatch handler registered in initialize_game (game.c:124-125) and is also reached from the multiplayer dispatcher's local-action branch (game.c:773). Passing 0 as the TCP_Socket_Manager argument is the correct mechanism to suppress network transmission in singleplayer — the callee treats a null manager as "no socket, skip send." The argument reordering (Game*, Client*, Game_Action* -> Client*, Game*, TCP_Socket_Manager*, Game_Action*) is intentional and matches the callee's parameter order precisely. No struct initializer is involved, so the "all fields assigned" concern does not apply.

Implementation Correctness:
Type compatibility — the three pointer arguments match their callee targets exactly: p_client (Client*) -> param 1, p_game (Game*) -> param 2, p_game_action (Game_Action*) -> param 4. The literal 0 is a valid null pointer constant for the TCP_Socket_Manager* parameter (param 3) in standard C; there is no truncation or implicit conversion concern. The returned bool from the callee is returned directly with no conversion.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access in the wrapper itself. The only UB risk is a null p_client or p_game, both of which are dereferenced inside the callee (not guarded there); this is governed by explicit preconditions and is identical to the expectations of the sibling multiplayer dispatcher.
Validation — no validation is performed in the wrapper, which is appropriate: it is a thin adapter and delegate. Null-guarding of p_game_action is handled by the callee; the asymmetry (p_game_action is guarded but p_client is not) is a callee-level property, not a defect introduced here.

Side Effects:
- Delegates entirely to dispatch_game_action_for__client, which mutates p_game_action (stamps uuid_of__client__u32, may set BAD_REQUEST via set_game_action_as__bad_request on process failure) and may mutate the client's outbound Game_Action_Manager pool (allocating a copy when is_game_action__with_process and not already allocated).
- No TCP transmission occurs because the TCP_Socket_Manager argument is NULL; the callee returns true at line 376 without reaching send_bytes_over__tcp_socket.
- No direct mutation of p_game, p_client, or any other Client is performed by this function; all side effects are inherited from the delegated callee.
