dispatch_game_action_for__client — core/source/client.c, lines 292-403

Sanitizes an outbound game action, tags it with the originating client's UUID, dispatches any associated process (allocating a copy from the client's outbound pool when needed), and sends the action over TCP — unless the action is local, the TCP socket manager is null, or the client is the game's local client (self-send skipped). Returns false on dispatch failure.

Pre-conditions:
1. p_client must be a non-null pointer to a valid Client.
2. p_game must be a non-null pointer to a valid Game.
3. p_tcp_socket_manager may be NULL.
4. p_game_action must be a non-null pointer to a valid Game_Action.
5. The game action's kind must have a corresponding Game_Action_Logic_Entry in the game's Game_Action_Logic_Table.
6. If the action is "with process" and not already allocated, the client's outbound Game_Action_Manager must have a free slot for allocation.
7. If the action is "with process" and requires processing on invocation or response, and a copy was needed, the Process_Manager must have a free slot for process allocation.
8. If the action has an m_process (and is not "with process"), the Game_Action_Logic_Table must provide a valid outbound m_process for the action's kind.

Post-conditions:
1) If returns true:
   - The game action was sanitized for outbound (via santize_game_action__outbound).
   - The game action's uuid_of__client__u32 was set to the originating client's UUID.
   - If the action was "with process" and not already allocated, a copy was allocated from the client's outbound pool and the original was discarded (p_game_action now points to the copy).
   - If the action was "with process" and required processing on invocation or response, the process was dispatched and the allocated copy is now in the outbound pool.
   - If the action has an m_process (and is not "with process"), the m_process was invoked with the action as process data; if the process failed, the action was marked as bad request.
   - If a TCP socket was obtainable and the action is not local and the client is not the game's local client, the action was serialized and sent over TCP.
2) If returns false:
   - p_game_action was null, OR
   - No Game_Action_Logic_Entry was found for the action's kind, OR
   - Failed to allocate a copy of the action from the outbound pool (for "with process" actions), OR
   - Failed to allocate a Process for dispatch, OR
   - No TCP socket was obtainable for the client's UUID.
   - In the false-return cases involving allocation failure, the allocated copy was released back to the outbound pool before returning.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's name and surrounding API (allocate_game_action_from__client, release_game_action_from__client, receive_game_action_for__client) confirm that this function is responsible for dispatching a game action on behalf of a client: sanitizing it for outbound, tagging it with the client identifier, handling any associated process logic, and transmitting it over TCP. The implementation fulfills this semantic intent — sanitization, UUID tagging, process handling, and TCP transmission are all present and correctly ordered. However, there is a critical null-pointer bug when a "with process" action is already allocated (see Implementation Correctness).

Implementation Correctness:
Type compatibility — every parameter type matches its usage: Client *, Game *, TCP_Socket_Manager *, Game_Action *. No implicit conversions or truncation.
No undefined behavior — there is a NULL dereference bug when a "with process" action is already allocated. When is_game_action__allocated(p_game_action) is true, the local p_game_action__allocated remains NULL (0). This NULL is then passed to:
  1. dispatch_game_action_process__outbound() at line 341, which dereferences it to look up the action's kind — causing a NULL pointer dereference crash.
  2. release_game_action_from__game_action_manager() at lines 348-350 on process failure — which writes a deallocated header through NULL, causing a NULL write in release builds.
  This is a known bug (see agents/BUGS.md, Bug #13). The fix is to assign p_game_action__allocated = p_game_action after the allocation if/else block, so the already-allocated action is used consistently.
No validation is needed for p_client, p_game, or p_tcp_socket_manager — these are caller responsibilities consistent with Lavender patterns. p_game_action is validated at line 303-306.
Validation is appropriate — the function validates its Game_Action pointer and the existence of the corresponding logic entry, which is correct for a dispatch function.

Side Effects:
1. Mutates p_game_action: sanitizes it for outbound via santize_game_action__outbound.
2. Mutates p_game_action: sets uuid_of__client__u32 to the originating client's UUID.
3. May allocate a new Game_Action from the client's outbound pool (if "with process" and not already allocated).
4. May dispatch a Process for the action (if "with process" and requires processing on invocation or response).
5. May set the game action as bad request (if m_process invocation fails).
6. May send serialized Game_Action bytes over TCP (if not local and TCP socket is available).
7. May release an allocated Game_Action back to the outbound pool (on process allocation failure).
