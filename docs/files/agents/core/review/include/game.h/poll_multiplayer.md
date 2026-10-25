poll_multiplayer — core/source/game.c

Polls the TCP socket manager for pending network events (connections, data, disconnections) if multiplayer is active, delegating to a platform-specific callback.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game struct.
2. If multiplayer is active, p_game->pM_tcp_socket_manager must be a valid, non-null pointer to an initialized TCP_Socket_Manager.
3. If pM_tcp_socket_manager is non-null, its m_poll_tcp_socket_manager function pointer must be set (guaranteed by begin_multiplayer_for__game which calls initialize_tcp_socket_manager).

Post-conditions:
1. If p_game->pM_tcp_socket_manager is NULL, the function returns immediately with no side effects.
2. If p_game->pM_tcp_socket_manager is non-NULL, the m_poll_tcp_socket_manager callback is invoked with (p_game->pM_tcp_socket_manager, p_game). The specific side effects (e.g., accepting connections, receiving data) are determined by the platform-specific callback implementation.
3. The function has no return value (void).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills its semantic intent. It acts as a guard-and-dispatch: it checks whether multiplayer is active (pM_tcp_socket_manager is non-null) and, if so, delegates to the platform-specific poll function. The null check on pM_tcp_socket_manager correctly prevents dereferencing a null pointer when multiplayer is not initialized. The function pointer m_poll_tcp_socket_manager is always set during begin_multiplayer_for__game via initialize_tcp_socket_manager, so the dereference is safe whenever pM_tcp_socket_manager is non-null.

Implementation Correctness:
Type compatibility — the function pointer m_poll_tcp_socket_manager has type m_Poll_TCP_Socket_Manager which is `void (*)(TCP_Socket_Manager*, Game*)`, and the call passes (TCP_Socket_Manager*, Game*), which matches exactly. No implicit conversions or truncation.
No undefined behavior — no broken pointer arithmetic, no null dereference (guarded by the null check on pM_tcp_socket_manager), no type punning, no out-of-bounds access.
Validation — the null check on pM_tcp_socket_manager is appropriate for this function's role. The function does not validate p_game itself, which is consistent with the codebase convention (e.g., is_game__multiplayer also does not null-check p_game). No additional validation is needed.

Side Effects:
If pM_tcp_socket_manager is non-null, the function invokes the platform-specific m_poll_tcp_socket_manager callback, which may have side effects such as accepting pending TCP connections, receiving data, or updating socket states. These side effects are delegated to the callback and are outside the scope of this function's own observable effects. If pM_tcp_socket_manager is null, there are no side effects.
