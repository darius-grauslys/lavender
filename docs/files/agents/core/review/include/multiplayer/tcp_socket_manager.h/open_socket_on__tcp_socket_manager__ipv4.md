open_socket_on__tcp_socket_manager__ipv4 — core/source/multiplayer/tcp_socket_manager.c, lines 104-132

Establishes an outbound TCP connection to the given IPv4 address and registers the resulting socket in the manager's pool.

Pre-conditions:
1. p_tcp_socket_manager must be a non-null pointer to a properly initialized TCP_Socket_Manager.
2. ipv4_address is the target address to connect to (any valid IPv4_Address value).
3. uuid_of__tcp_socket__u32 is the UUID to assign to the new TCP_Socket (must be unique within the manager's pool for successful allocation).

Post-conditions:
1. On success: a PLATFORM_tcp_connect call has been issued, a TCP_Socket has been allocated from the manager's pool, the socket has been initialized (serialization header, address, state, queues), the platform socket pointer has been bound to the TCP_Socket, the manager's quantity_of__connections has been incremented, and the pointer has been registered in the manager's ptr_array_of__tcp_sockets.
2. On failure (PLATFORM_tcp_connect returns null): the function logs an error and returns 0 (null) without modifying the manager.
3. On failure (allocation returns null): the function returns 0 (null). However, this path is buggy — see Implementation Correctness.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to connect a platform TCP socket and wrap it in a TCP_Socket managed by the TCP_Socket_Manager. The high-level flow (connect → allocate → initialize → bind platform socket) matches this intent. However, the implementation has a critical defect in the allocation path.

Implementation Correctness:
- **Missing null check on p_tcp_socket after allocation**: After calling `allocate_tcp_socket_from__tcp_socket_manager`, the return value is not checked for null. If the pool is exhausted (MAX_QUANTITY_OF__TCP_SOCKETS reached), `allocate_tcp_socket_from__tcp_socket_manager` returns 0. The function then unconditionally calls `initialize_tcp_socket(p_tcp_socket, ...)`, which dereferences the null pointer via `memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))`. This is undefined behavior (null pointer dereference).
- **Resource leak on allocation failure**: `PLATFORM_tcp_connect` is called and succeeds (returning a non-null `p_PLATFORM_tcp_socket`) before `allocate_tcp_socket_from__tcp_socket_manager` is attempted. If allocation fails, the platform socket is never closed. `PLATFORM_tcp_close_socket` is available and should be called to release the platform resource before returning 0.
- **No null check on p_tcp_socket_manager**: The function does not validate that `p_tcp_socket_manager` is non-null before dereferencing it via `get_p_PLATFORM_tcp_context_from__tcp_socket_manager`. All sibling functions in this file share this assumption, so this is consistent with the codebase convention — however, it is worth noting that no validation is performed.
- **Related callee bug in initialize_tcp_socket**: The `initialize_tcp_socket` function (in tcp_socket.c, line 84) calls `memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))`. Since `queue_of__tcp_packet` is not at offset 0 in the TCP_Socket struct (it follows `_serialization_header`), this memset writes `sizeof(Serialization_Header)` bytes past the end of the struct, causing a buffer overflow. This bug is triggered whenever `initialize_tcp_socket` is called, including from this function.

Side Effects:
- Mutates the TCP_Socket_Manager: increments `quantity_of__connections`, registers the new socket in `ptr_array_of__tcp_sockets`, and the allocated TCP_Socket is placed in the `tcp_sockets` contiguous array.
- Mutates the newly allocated TCP_Socket: zero-fills its packet queue, sets the serialization header, copies the IPv4 address, resets enqueue index and received packet count, sets state to TCP_Socket_State__None, and binds the platform socket pointer.
- Initiates a platform-level TCP connection via `PLATFORM_tcp_connect`, which has side effects on the underlying network stack.
- Logs an error via `debug_error` if the platform connection fails.
