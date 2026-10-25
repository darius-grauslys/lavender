m_game_action_handler__dispatch__multiplayer — core/source/game.c (declaration: lines 68-71, implementation: lines 768-798)

Routes a Game_Action through the multiplayer dispatch policy: local actions fall back to the singleplayer dispatcher, broadcasted actions are sent to all eligible clients, and any other action is dispatched directly to the given p_client over TCP.

Pre-conditions:
1. p_game must be a non-null pointer to a Game whose multiplayer state is active (i.e., begin_multiplayer_for__game() has run and installed this handler as the dispatch function pointer).
2. p_game must carry an initialized TCP_Socket_Manager; it is read via get_p_tcp_socket_manager_from__game(p_game) on the unicast path.
3. p_game_action must be a non-null pointer to a writable Game_Action. This is a hard precondition: the flag predicates is_game_action__local() and is_game_action__broadcasted() dereference p_game_action at the top of the function before any null guard, so a null p_game_action is undefined behavior. Note this is asymmetric with dispatch_game_action_for__client(), which itself null-checks p_game_action.
4. p_client may be NULL. It is only required on the unicast fallback path; the local and broadcasted branches do not use p_client.

Post-conditions:
1. For a local action: returns the result of m_game_action_handler__dispatch__singleplayer(p_game, p_client, p_game_action); the singleplayer dispatcher may assign uuid_of__client__u32 and dispatch a process.
2. For a broadcasted action: call broadcast_game_action(p_game, p_game_action) — which dispatches to the local client and to every remote client whose loaded local space matches the action's broadcast point — then returns is_game_action__bad_request(p_game_action). The action's uuid_of__client__u32 and flags (notably BAD_REQUEST) may have been mutated by the broadcast traversal.
3. For a unicast action with a NULL p_client: logs a debug error and returns false.
4. For a unicast action with a non-null p_client: returns the result of dispatch_game_action_for__client(p_client, p_game, get_p_tcp_socket_manager_from__game(p_game), p_game_action), which sanitizes the action, stamps uuid_of__client__u32, optionally copies the action into the client's outbound game-action pool (when is_game_action__with_process and not already allocated), and transmits it over TCP to p_client (skipping the send when p_tcp_socket_manager is null, when the client is the local client, or when the action is local).
5. The Game_Action argument is not guaranteed const: its uuid_of__client__u32 field is written and its flag bits (e.g., BAD_REQUEST) may be toggled by the dispatched callee.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its dispatch intent. The three-way branch (local -> singleplayer, broadcasted -> broadcast_game_action, else -> unicast dispatch) matches the documented multiplayer policy. The author's own TODO (line 783, "is this sufficient to handle errors?") flags uncertainty about whether returning the is_game_action__bad_request flag is an adequate error contract for the broadcast path; it is a reasonable, conservative contract (the broadcast marks the action BAD_REQUEST on internal failure and that is propagated as the return value), but it is not a full error code. This is a design uncertainty, not a semantic drift — the function does what it says it does.

Implementation Correctness:
Type compatibility — all arguments match their targets exactly. p_game (Game*) feeds broadcast_game_action(Game*, Game_Action*), m_game_action_handler__dispatch__singleplayer(Game*, Client*, Game_Action*), and get_p_tcp_socket_manager_from__game(p_game) whose return (TCP_Socket_Manager*) is passed positionally to dispatch_game_action_for__client(Client*, Game*, TCP_Socket_Manager*, Game_Action*). p_client (Client*) matches. The returned bool from each callee is returned directly. No implicit conversions or truncation.
Undefined behavior — no pointer arithmetic, no type punning, no out-of-bounds access. The only UB risk is a null p_game_action dereference at the top (see Pre-condition 3), which is governed by an explicit precondition and is consistent with the singleplayer dispatcher's expectations; p_game null would also be UB because broadcast_game_action and the unicast path dereference it. get_p_tcp_socket_manager_from__game(p_game) is only reached on the unicast path, so p_game null is not additionally exposed on the local/broadcast paths beyond the predicate reads.
Validation — p_client is validated (NULL-guarded) on the unicast path, which is appropriate since the local/broadcast branches legitimately do not need it. p_game_action is NOT null-guarded here, creating an asymmetry with dispatch_game_action_for__client (client.c:303-306), which does guard. This is a minor validation gap rather than a defect; because the predicates at the top cannot tolerate a null action, the gap is best closed by treating non-null p_game_action as a hard precondition (as listed above) or by adding an early null-guard.

Side Effects:
- Delegates to m_game_action_handler__dispatch__singleplayer (local branch), which may mutate the action and dispatch a process.
- Invokes broadcast_game_action (broadcast branch), whose observable effect is dispatching the action to the local client and to each remote client whose loaded local space contains the action's broadcast point; this stamps uuid_of__client__u32 and may set BAD_REQUEST on the action.
- Invokes dispatch_game_action_for__client (unicast branch), which sanitizes the action, stamps uuid_of__client__u32, may copy the action into the outbound game-action pool, and transmits it over TCP to p_client (with the documented "do not tcp send to self" / null-manager skips).
- Reads the Game's TCP_Socket_Manager via get_p_tcp_socket_manager_from__game(p_game) but does not directly mutate Game or Client beyond what the delegated callees do.
- Emits a debug_error log line only on the unicast-with-NULL-client failure path.
