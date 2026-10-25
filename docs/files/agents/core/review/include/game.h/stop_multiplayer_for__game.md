stop_multiplayer_for__game — core/source/game.c, lines 292-298

Tears down the TCP socket manager and platform TCP context that were set up by begin_multiplayer_for__game.

Pre-conditions:
1. p_game must be a non-null pointer to a valid Game object.
2. p_game may or may not have an active pM_tcp_socket_manager. If it is null, the function is a no-op.

Post-conditions:
1. If p_game->pM_tcp_socket_manager was non-null, PLATFORM_tcp_end is called to tear down the platform TCP context, and the TCP_Socket_Manager allocation is freed via free.
2. The game state is NOT fully restored to its pre-multiplayer (singleplayer) state. Specifically:
   - p_game->pM_tcp_socket_manager is left as a dangling pointer (freed but not set to NULL).
   - p_game->m_game_action_handler__dispatch, __receive, and __resolve remain set to their multiplayer variants.
   - p_game->game_flags__u32 retains the GAME_FLAG__IS_SERVER_OR__CLIENT bit set (client or server flag is not cleared).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation partially fulfills its semantic intent. It correctly calls PLATFORM_tcp_end and frees the TCP_Socket_Manager allocation when one exists. However, it fails to restore the Game struct to its initial singleplayer state. Comparing against initialize_game (which sets pM_tcp_socket_manager to 0, sets all three game action handlers to their __singleplayer variants, and leaves game_flags__u32 cleared), stop_multiplayer_for__game should perform the inverse of begin_multiplayer_for__game:
- Set p_game->pM_tcp_socket_manager = 0 after freeing (to avoid dangling pointer).
- Reset p_game->m_game_action_handler__dispatch to m_game_action_handler__dispatch__singleplayer.
- Reset p_game->m_game_action_handler__receive to m_game_action_handler__receive__singleplayer.
- Reset p_game->m_game_action_handler__resolve to m_game_action_handler__resolve__singleplayer.
- Clear the GAME_FLAG__IS_SERVER_OR__CLIENT bit in p_game->game_flags__u32.

The omission of these resets is a correctness bug. After stop_multiplayer_for__game returns:
- is_game__multiplayer(p_game) returns true (non-null dangling pointer).
- Any subsequent call to get_p_PLATFORM_tcp_context_from__game dereferences freed memory.
- The game action handlers remain multiplayer variants, which will attempt to use the freed TCP socket manager, leading to undefined behavior.

Implementation Correctness:
Type compatibility: The parameter type Game * matches the function signature. No implicit conversions.
Undefined behavior: The dangling pointer left in p_game->pM_tcp_socket_manager is a use-after-free hazard. Any code that checks is_game__multiplayer or calls get_p_tcp_socket_manager_from__game after stop_multiplayer_for__game will operate on freed memory.
Validation: The null check on p_game->pM_tcp_socket_manager is appropriate for the function's role. However, the lack of post-free cleanup is the core defect.

Side Effects:
1. Calls PLATFORM_tcp_end(p_game), which tears down the platform TCP context (e.g., closes sockets, frees platform resources).
2. Frees the heap allocation pointed to by p_game->pM_tcp_socket_manager.
3. Leaves p_game->pM_tcp_socket_manager as a dangling pointer (not set to NULL).
4. Does NOT reset the game action handler function pointers to singleplayer variants.
5. Does NOT clear the server/client game flag.
