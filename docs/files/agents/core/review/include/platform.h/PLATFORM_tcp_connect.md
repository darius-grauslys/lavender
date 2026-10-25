PLATFORM_tcp_connect — core/include/platform.h

Initiates a TCP connection to a remote IPv4 address using the given platform TCP context, returning a platform socket handle or null on failure.

Pre-conditions:
1. p_PLATFORM_tcp_context must be a non-null pointer to a valid, initialized PLATFORM_TCP_Context (previously obtained via PLATFORM_tcp_begin).
2. p_ipv4_address must be a non-null pointer to a valid IPv4_Address specifying the remote endpoint to connect to.

Post-conditions:
1. On success, returns a non-null PLATFORM_TCP_Socket* representing the newly initiated connection. The socket is in a connecting state; the caller must poll it with PLATFORM_tcp_poll_connect to determine when the connection is fully established.
2. On failure, returns null. No socket is allocated.

Correctness Verdict: Correct

Semantic Alignment:
The function signature and documentation align with the intended semantic purpose: initiating a TCP client connection. The comment "Returns null if failed to connect" matches the usage in open_socket_on__tcp_socket_manager__ipv4, where the return value is checked for null and an error is logged if the connection fails. The parameter types (PLATFORM_TCP_Context*, IPv4_Address*) are appropriate for the function's role. The function does not take a port parameter, which is consistent with it connecting to a specific remote address provided by the caller.

Implementation Correctness:
No implementation is available in the core module — this is a platform-dependent function declared in the PLATFORM abstraction layer and implemented by a backend (e.g., nds, SDL, etc.). The header documentation is clear and consistent with the call site in tcp_socket_manager.c. No type mismatches are evident from the declaration. The use of a pointer return and pointer parameters is appropriate for this API.

Side Effects:
As a platform-level networking function, PLATFORM_tcp_connect has the side effect of allocating and initiating a TCP socket connection to the specified remote address. This involves system-level resource allocation (socket descriptor, network connection state). The caller is responsible for managing the lifecycle of the returned socket, including eventual closure via PLATFORM_tcp_close_socket.
