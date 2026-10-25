PLATFORM_tcp_server — core/include/platform.h

Allocates and configures a non-blocking TCP server socket, binds it to the given port on all local interfaces, and begins listening for incoming connections.

Pre-conditions:
1. p_PLATFORM_tcp_context must be a non-null pointer to a valid, initialized PLATFORM_TCP_Context (e.g., one produced by PLATFORM_tcp_begin). The function does not defensively null-check the context; a null context dereferences into the pool array and crashes (caller responsibility, per Lavender's low-level convention).
2. The context must contain at least one free pool slot — a slot whose socket_handle is 0 (tested via NO_GUI_is_PLATFORM_tcp_socket__in_use). If every slot is in use, or if socket() itself fails, allocation fails and the function returns null.
3. port is any Index__u16 (uint16_t) host-byte-order value. No range constraint is enforced; 0 lets the OS choose a port, and a privileged port (<1024) without privileges causes bind to fail (handled by the bind-failure path).

Post-conditions:
1. On success: returns a non-null PLATFORM_TCP_Socket* to a pool slot whose socket_handle is valid, has been set non-blocking, is bound to INADDR_ANY:<port>, and is actively listening with a backlog of MAX_QUANTITY_OF__TCP_SOCKETS - 1. The slot is marked in-use.
2. On socket-allocation failure (no free slot or socket() failure): returns null; the pool is left unchanged (no slot marked in-use, since a failed socket() does not invoke the slot initializer).
3. On fcntl (non-blocking mode) failure: returns null; the socket handle is closed and the slot is reset to inactive (socket_handle = 0).
4. On bind failure: returns null; the socket handle is closed and the slot is reset to inactive.
5. On listen failure: returns null — see note under Post-conditions; intended cleanup does not occur here (see Issues).

Correctness Verdict: Incorrect

Semantic Alignment:
The implementation fulfills the documented intent — it produces a listening server socket on success and returns null on failure — so the happy path is semantically correct. However, the function's own doc comment says "Returns null if failed," which implies a clean failure (no leftover acquired resource). This intent is NOT met on the listen-failure path, where the descriptor is leaked and the pool slot is left marked in-use. The use of NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive is Lavender-style pool cleanup (resetting a struct to its inactive/reusable condition), not RAII; this matches the engine's model and is appropriate here.

Implementation Correctness:
Type compatibility — port is Index__u16 (uint16_t) and is passed to htons(uint16_t); sin_addr.s_addr is in_addr_t (u32) and receives htonl(INADDR_ANY); socket_handle is u32 and matches the struct member. No implicit conversions or truncation. The struct literal is zeroed with memset before field assignment. No type punning.
Undefined behavior — no broken pointer arithmetic, no out-of-bounds array access (the allocation loop is bounded by MAX_QUANTITY_OF__TCP_SOCKETS and guarded by NO_GUI_get_p_PLATFORM_tcp_socket_by__index_from__context in debug), and no null dereference on a valid context.
Validation — no null check on p_PLATFORM_tcp_context is consistent with this engine's low-level PLATFORM convention (the caller owns context validity); this is acceptable for the function's role.
Issues:
- Listen-failure path (no_gui_tcp_context.c:236-239; mirrored in sdl_tcp_context.c:228-231): when listen() fails the function returns 0 without closing the socket handle and without resetting the pool slot. This leaks the OS socket descriptor and permanently occupies a pool slot (the slot stays marked in-use because socket_handle remains non-zero), violating the post-condition that a failed call leaves the context pool usable. Unlike the fcntl and bind paths, no cleanup is invoked here.
- fcntl-failure path (no_gui_tcp_context.c:212-224): if close() itself fails (returns non-zero), the function returns early WITHOUT calling NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive, leaving the slot marked in-use with a stale handle; this is a minor secondary leak. The fcntl path also inlines close()+reset rather than delegating to PLATFORM_tcp_close_socket, diverging from the bind path's approach.
- SDL mirror (sdl_tcp_context.c:208-216) has an additional defect in its fcntl-failure path: it checks `if (PLATFORM_tcp_close_socket(...))`, which is true on a SUCCESSFUL close, yet logs "failed to close socket" only in that success case — the error message is inverted relative to the actual outcome.

Side Effects:
- Acquires an OS socket descriptor via socket(PF_INET, SOCK_STREAM, 0).
- Mutates one slot of the context's PLATFORM_tcp_sockets pool (sets socket_handle to the acquired descriptor on success).
- May close the descriptor and reset the slot to inactive on the fcntl-failure and bind-failure paths (via PLATFORM_tcp_close_socket or inline close()+NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive).
- On the listen-failure path it performs NO cleanup (bug — see Issues).
- Emits debug log output (debug_error / debug_info) on both success and failure.
- Does not otherwise modify the context structure or read/write any other global state.
