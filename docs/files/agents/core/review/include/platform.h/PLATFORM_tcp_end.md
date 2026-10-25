PLATFORM_tcp_end — core/include/platform.h

Tears down the platform TCP subsystem: releases the heap-allocated PLATFORM_TCP_Context owned by the Game's TCP_Socket_Manager back to the C heap and clears the manager's context pointer to NULL (Lavender-style reset of the owning field to its idle state), returning the subsystem to its initial conditions. It is the inverse of PLATFORM_tcp_begin. On Win32 it is also the reference-count counterpart to WSAStartup (WSACleanup).

Pre-conditions:
1. p_game must be a non-null pointer to a valid, live Game object (null-checking p_game is the caller's responsibility, consistent with begin_multiplayer_for__game/stop_multiplayer_for__game at core/source/game.c:292-298 and the low-level accessor convention throughout core/include/game.h).
2. p_game->pM_tcp_socket_manager may be NULL — the function tests it first and returns early (no-op), so no dereference occurs in that case.
3. If pM_tcp_socket_manager is non-null, the PLATFORM_TCP_Context it holds (retrieved via get_p_PLATFORM_tcp_context_from__game, game.h:280) must have been heap-allocated by PLATFORM_tcp_begin so that free() is valid; a NULL context is also acceptable since free(NULL) is well-defined in C.
4. The caller (stop_multiplayer_for__game, core/source/game.c:295) is responsible for subsequently freeing p_game->pM_tcp_socket_manager itself; this function does not free the manager.

Post-conditions:
1. If pM_tcp_socket_manager was NULL: the function is a no-op and p_game is unchanged.
2. If non-null: p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context is set to NULL (0) and the previously held PLATFORM_TCP_Context object (if non-null) has been released to the heap. The local pointer used for the free preserves the original address (the field is zeroed before the free, using the local copy), so no dangling pointer remains in the field.
3. On Win32: WSACleanup() has been called as the reference-count counterpart to the WSAStartup performed in PLATFORM_tcp_begin.
4. The OS-level socket handles of any still-open PLATFORM_tcp_sockets in the context's pool are NOT closed by this function (see observations under Implementation Correctness / Side Effects); only the context block itself is released.

Correctness Verdict: Correct

Semantic Alignment:
The Unix (sdl/source/multiplayer/unix/sdl_unix_tcp_context.c:20), no_gui (no_gui/source/multiplayer/no_gui_tcp_context.c:54), and Win32 (sdl/source/multiplayer/win64/sdl_win64_tcp_context.c:27) implementations together faithfully realize the documented "shut down the backend TCP subsystem" semantic of agents/platform_api.md:564.

The null-guard on pM_tcp_socket_manager makes the no-op case safe. The sequence null-the-field-then-free is correct because free() uses the local copy of the pointer, not the now-zeroed field, and free(NULL) correctly handles an unset context. The Win32-only WSACleanup() is the correct platform counterpart to PLATFORM_tcp_begin's WSAStartup. This is resource release (free) plus a field reset to idle — NOT a mislabeled Lavender "initialization"; it is the proper teardown/inverse of begin.

Note (not a defect of this function): PLATFORM_tcp_begin's Win32 path suffers an inverted WSAStartup condition (documented as Incorrect in PLATFORM_tcp_begin.md). Because of that, WSACleanup() here is reached both on the begin-success abort path (balanced: WSAStartup succeeded) and on the begin-Failure path (where WSAStartup itself failed). This is a consequence of the begin bug, not an error in PLATFORM_tcp_end's logic.

Implementation Correctness:
- Type compatibility: returns void (matches the declaration at platform.h:384); all pointer types (Game *, PLATFORM_TCP_Context *, and the p_PLATFORM_tcp_context field, typed PLATFORM_TCP_Context * at defines.h:1239) match exactly; assigning 0 to a pointer field is a valid null-pointer constant in C; free()'s argument matches the malloc'd type from PLATFORM_tcp_begin. No implicit conversions or truncation.
- Undefined behavior: no broken pointer arithmetic, no null dereference (the only p_game dereference is guarded by the pM_tcp_socket_manager null check, and null-checking p_game itself is the caller's responsibility per codebase convention), no type punning, no out-of-bounds access. free of a NULL or valid pointer is well-defined.
- Validation: appropriate for the function's role. The manager null check plus caller responsibility for p_game mirror the convention used by begin_multiplayer_for__game/stop_multiplayer_for__game and the get_p_* accessors in game.h. Adding a p_game NULL check here would be inconsistent with the low-level accessor contract used throughout game.h.
- Test stubs: tests/core/source/PLATFORM.c:458 and tests/templates/source/PLATFORM.c:458 are intentional empty no-ops ({}) that do not dereference p_game, matching the stubbing pattern of PLATFORM_tcp_begin's stub (which returns 0).
- Observation (resource hygiene, not UB): the function does not iterate context->PLATFORM_tcp_sockets[] and close still-open OS socket handles before freeing the context. If any active socket (socket_handle != 0) remains open at teardown, its OS file descriptor leaks; closing sockets is the documented job of PLATFORM_tcp_close_socket (platform.h:414), and stop_multiplayer_for__game (core/source/game.c:292-298) does not close them either. This is a real leak risk but is a separate resource-management concern from the function's stated semantic; it is noted here for completeness rather than treated as a contract violation.

Side Effects:
- Releases the heap allocation previously obtained by PLATFORM_tcp_begin (the PLATFORM_TCP_Context block) via free().
- Mutates the owning Game: writes p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context = 0 (field reset to idle/null).
- On Win32: calls WSACleanup(), decrementing the Winsock 2 reference count (counterpart to PLATFORM_tcp_begin's WSAStartup).
- On the Unix/no_gui path and on the NULL-manager path: no other externally observable effects.
- Does NOT close open OS socket descriptors held by the context's socket pool (see observation above) and does NOT free pM_tcp_socket_manager (caller's responsibility, see stop_multiplayer_for__game at core/source/game.c:292-298).
- On the test stubs: no side effects (empty body).
