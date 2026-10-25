m_game_action_handler__receive__singleplayer — core/source/game.c

Forwards an inbound singleplayer game action to the owning client's action receiver and returns that callee's result verbatim.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game. It is forwarded unchecked to receive_game_action_for__client (core/source/client.c:182), which dereferences it via get_p_process_manager_from__game and get_p_game_action_logic_table_from__game at client.c:187-190.
2. p_client must be a non-null pointer to a valid Client. It is forwarded unchecked to receive_game_action_for__client, which dereferences it via GET_UUID_P(p_client) at client.c:202 and get_p_game_action_manager__outbound_from__client at client.c:208-209.
3. p_game_action must be a non-null pointer to a valid Game_Action. It is forwarded unchecked to receive_game_action_for__client, which dereferences it via get_kind_of__game_action(p_game_action) at client.c:195 and stamps it at client.c:201-202.
4. None of the three parameters are null-guarded within this function; the absence of guards matches the codebase convention for this handler layer (consistent with m_game_action_handler__receive__multiplayer's local path at game.c:814-818 and the callee receive_game_action_for__client, which also do not guard here) and is the caller's responsibility.

Post-conditions:
1. Returns the bool result of receive_game_action_for__client(p_client, p_game, p_game_action) — the return value is propagated verbatim (no masking, no hard-coding). A callee failure (unsupported action kind — client.c:198; missing responded-to action — client.c:225; copy/allocation failure — client.c:254; WITH_PROCESS dispatch failure — client.c:268) is faithfully reported as false, as is a responding action handled inline without a pool dispatch (client.c:240).
2. No direct mutation of any struct by this function; all observable mutations (stamping p_game_action->uuid_of__client__u32 at client.c:201, running santize_game_action__inbound at client.c:204, mutating the client's outbound game-action manager lookup at client.c:208-209, dispatching/locally-running an m_Process) occur inside receive_game_action_for__client and are not re-traced here.

Correctness Verdict: Correct

Semantic Alignment:
The function's intent — as the singleplayer receive handler, whose bool return is consumed by receive_game_action (core/include/game.h:385) and forwarded to that caller's callers — is to report whether an inbound game action was actually received and processed by the client subsystem. The implementation fulfills this intent faithfully: it delegates to receive_game_action_for__client and returns that callee's bool result directly, so every failure and success mode of the callee is reported to the caller with no distortion.

This is the structurally identical sibling of m_game_action_handler__receive__multiplayer's local branch (game.c:814-818), which likewise returns `return m_game_action_handler__receive__singleplayer(...)`. The key contrast with the multiplayer handler is that multiplayer's non-local branch (game.c:826-830) discards its callee's return and hard-codes true — a defect this singleplayer handler does not share, since its sole path propagates the callee's result. The implementation therefore does exactly what its semantic intent requires.

Implementation Correctness:
- Type compatibility: good. p_game (Game *), p_client (Client *), and p_game_action (Game_Action *) are forwarded to receive_game_action_for__client, whose parameters are (Client *p_client, Game *p_game, Game_Action *p_game_action). The argument order at the call site is (p_client, p_game, p_game_action), matching the callee's parameter order exactly — p_client-to-p_client, p_game-to-p_game, p_game_action-to-p_game_action — each the identical type. No implicit conversions or truncation. The callee's bool return is returned directly from a bool-returning function — no conversion hazard.
- Undefined behavior: none under the stated pre-conditions. No null dereference occurs within this function itself: no parameter is dereferenced here — the call passes the pointers by value to the callee, which is the sole site of dereference. No pointer arithmetic, no out-of-bounds access, no type punning. If any pre-condition is violated (a NULL argument), the dereference occurs in the callee, consistent with the callee's own unguarded GET_UUID_P / get_kind_of__game_action usage.
- Validation: no validation is performed or needed at this layer — this is a faithful pass-through/delegation. The absence of p_game/p_client/p_game_action null guards matches the codebase convention for this handler layer (cf. m_game_action_handler__receive__multiplayer's local path and the callee receive_game_action_for__client, which also lack guards here) and is the caller's responsibility; it is not a defect.

Side Effects:
- No side effects — this function itself assigns to no field of any struct, performs no logging, and executes no I/O. The only observable effects of a call (stamping p_game_action->uuid_of__client__u32, running santize_game_action__inbound, mutating the client's game-action managers, dispatching/locally-running an m_Process, or debug_error logging) all occur inside the forwarded callee receive_game_action_for__client and are not re-traced here.
- The function performs no direct mutation of p_game, p_client, or p_game_action.
