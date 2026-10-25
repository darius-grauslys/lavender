get_p_PLATFORM_tcp_socket_from__tcp_socket — core/include/multiplayer/tcp_socket.h

Accessor that returns the platform-level TCP socket pointer stored in a TCP_Socket.

Pre-conditions:
1. p_tcp_socket must be a non-null pointer to a valid TCP_Socket object.

Post-conditions:
1. Returns the PLATFORM_TCP_Socket* stored in p_tcp_socket->p_PLATFORM_tcp_socket. May be NULL if the socket is not bound (i.e., between unbind_tcp_socket calls).

Correctness Verdict: Correct

Semantic Alignment:
The function correctly retrieves the platform-level TCP socket pointer from the TCP_Socket struct. It accesses the p_PLATFORM_tcp_socket field, which is the field intended to hold the platform socket reference. This field is set by bind_tcp_socket and cleared (set to 0) by unbind_tcp_socket. The accessor is used by unbind_tcp_socket itself to retrieve the platform socket before closing it.

Implementation Correctness:
Type compatibility — the return type PLATFORM_TCP_Socket * matches the field type p_PLATFORM_tcp_socket exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (assuming the pre-condition is met), no type punning, no out-of-bounds access. The function performs a single field dereference and return.
No validation is needed — this is a low-level inline accessor. The caller is responsible for ensuring p_tcp_socket is valid and non-null.

Side Effects:
No side effects — this is a pure read accessor. It only reads the p_PLATFORM_tcp_socket field and returns it.