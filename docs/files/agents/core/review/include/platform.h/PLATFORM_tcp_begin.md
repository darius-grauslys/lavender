PLATFORM_tcp_begin — core/include/platform.h

Begins the platform TCP subsystem: heap-allocates a PLATFORM_TCP_Context and zero-initializes all of its sockets (Lavender-style reset-to-default / pooled state), returning a pointer the caller owns (freed by PLATFORM_tcp_end), or NULL on failure. On Win32 it is also intended to call WSAStartup.

Pre-conditions:
1. p_game is accepted but unused (not dereferenced) by every shipped implementation, so it may be NULL without causing undefined behavior.
2. The C heap (malloc) must be available and the allocation must succeed.
3. On Win32: Winsock must be functional — see the inverted-condition bug noted under Semantic Alignment / Implementation Correctness.

Post-conditions:
1. On success: returns a non-null, heap-allocated PLATFORM_TCP_Context whose entire storage is zeroed, so every PLATFORM_tcp_socket in the context has socket_handle == 0 and is therefore "inactive"/available for allocation (confirmed by SDL_is_PLATFORM_tcp_socket__in_use / NO_GUI_is_PLATFORM_tcp_socket__in_use, which test the handle for truthiness). Ownership transfers to the caller.
2. On failure: the error is logged via debug_error and NULL is returned; nothing is leaked (no allocated memory is abandoned).

Correctness Verdict: Incorrect

Semantic Alignment:
The Unix (sdl/source/multiplayer/unix/sdl_unix_tcp_context.c) and no_gui (no_gui/source/multiplayer/no_gui_tcp_context.c) implementations correctly fulfill the intent — allocate the context then zero-initialize it so sockets begin inactive. The inner *_initialize_PLATFORM_tcp_context calls perform Lavender-style initialization (memset to 0), which is appropriate and is NOT RAII resource acquisition.

The Win32 implementation (sdl/source/multiplayer/win64/sdl_win64_tcp_context.c) does NOT fulfill the intent because its condition is inverted:
    if (!WSAStartup(MAKEWORD(2,2), &__SDL_wsa_data)) {
        debug_error(...);
        return 0;
    }
WSAStartup returns 0 on SUCCESS and a non-zero code on FAILURE. `!WSAStartup(...)` is therefore TRUE on success, so the function logs "failed on WSAStartup" and returns NULL (0) on the SUCCESS path, while it proceeds to malloc + zero-init + return a context only when WSAStartup FAILED — i.e. without Winsock actually initialized. The caller (begin_multiplayer_for__game, core/source/game.c:267) treats a NULL return as fatal and aborts, so on Win32 multiplayer cannot begin. If the failure-return branch were ever taken, returning a "valid" context without Winsock initialized would make subsequent socket use undefined.

Implementation Correctness:
- Type compatibility: parameter and return types match the declaration exactly; `return 0;` for a pointer return is a valid null-pointer constant in C; the malloc sizeof argument is correct.
- Undefined behavior: no out-of-bounds, no type punning, no null dereference in the Unix/no_gui paths; p_game is never dereferenced. (The Win32 path does not itself crash because of the inversion, but the resulting state — using sockets without WSAStartup succeeding — is undefined.)
- Validation: the malloc result is checked against NULL in every implementation, which is appropriate for this allocator-based "begin" step.
- Minor defect: every implementation misspells the function name in its debug_error string as "PLATFORM_tcp_being" (should be "PLATFORM_tcp_begin") — cosmetic, but worth correcting for diagnosability.
- p_game is unused in all shipped implementations (only the test stubs ignore it intentionally too); harmless, but signals either dead API surface or an unimplemented future use.

Side Effects:
- Heap allocation via malloc (one fresh allocation per call); the returned pointer is owned by the caller and must be released by PLATFORM_tcp_end.
- On Win32: WSAStartup is invoked — its side effect is intended platform initialization, but it is gated behind the inverted condition described above.
- On failure: an error is logged via debug_error.
- p_game itself is not mutated by any implementation.
