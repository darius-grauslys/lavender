is_tcp_socket__manually_driven — core/include/multiplayer/tcp_socket.h

Queries whether the TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN bit is set in the socket's flags field.

Pre-conditions:
1. p_tcp_socket must be a non-null pointer to a valid TCP_Socket object.

Post-conditions:
1. Returns true if the TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN bit is set in p_tcp_socket->tcp_socket_flags__u8, false otherwise.
2. The TCP_Socket object is not modified.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly checks the manually-driven flag by performing a bitwise AND between the socket's flags field and TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN (defined as BIT(0), which is 1U). The result is implicitly converted to bool, which is correct: any non-zero value yields true, zero yields false. This matches the semantic intent of querying whether the socket is manually driven.

Implementation Correctness:
Type compatibility — get_tcp_socket_flags_from__tcp_socket returns TCP_Socket_Flags__u8 (typedef'd to uint8_t). The bitwise AND with TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN (which expands to (1U << 0), i.e. unsigned int) promotes the uint8_t to unsigned int via integer promotion, which is safe and well-defined. The resulting unsigned int is then implicitly converted to bool for the return, which is the intended behavior. No truncation occurs.
Undefined behavior — no pointer arithmetic, no null dereference (caller must provide valid pointer), no type punning, no out-of-bounds access.
Validation — no validation is performed inside the function. This is appropriate for a low-level inline accessor; the caller is responsible for ensuring p_tcp_socket is valid.

Side Effects:
No side effects — the function is a pure query that reads the flags field and returns a boolean result. The TCP_Socket object is not modified.