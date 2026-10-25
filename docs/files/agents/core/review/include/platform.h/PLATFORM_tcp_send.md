PLATFORM_tcp_send — core/include/platform.h, line 430
(implemented identically in no_gui/source/multiplayer/no_gui_tcp_context.c, line 343, and sdl/source/multiplayer/sdl_tcp_context.c, line 316; a stub returning -1 in tests/core/source/PLATFORM.c, line 514)

Wraps the POSIX send(2) syscall to transmit a byte buffer over an established TCP connection, returning the number of bytes sent or -1 on error.

Pre-conditions:
1. p_PLATFORM_tcp_socket must be non-null and point to a valid, connected PLATFORM_TCP_Socket whose socket_handle is an open, connected TCP socket descriptor.
2. p_bytes must be non-null and point to at least length_of__bytes readable bytes.
3. length_of__bytes is the quantity of bytes to send (Quantity__u32 / uint32_t); no range constraint beyond that of uint32_t.
No validation is performed inside the function; these are enforced by the caller (e.g., send_bytes_over__tcp_socket in tcp_socket.c).

Post-conditions:
1. Returns i32 (int32_t): the number of bytes successfully sent (>= 0), or -1 on error (errno is set). For a non-blocking socket that cannot send immediately, -1 is returned with errno EWOULDBLOCK/EAGAIN.
2. p_bytes is read but not modified.
3. The PLATFORM_TCP_Socket struct and its socket_handle are not mutated by the function.
Note: TCP send may complete a partial send (fewer than length_of__bytes bytes); the caller is responsible for retrying to achieve full delivery if that is required.

Correctness Verdict: Correct

Semantic Alignment:
The implementation calls send(p_PLATFORM_tcp_socket->socket_handle, p_bytes, length_of__bytes, 0) and returns the result verbatim. This matches the documented semantic ("Returns number of bytes sent, -1 if error"): send(2) returns the byte count on success and -1 on error, so the contract is fulfilled. Flags=0 is the correct default for a plain send. No semantic drift.

Implementation Correctness:
Type compatibility — socket_handle is stored as u32 (uint32_t) and is implicitly converted to send()'s int sockfd parameter; file-descriptor values are always small, so this is safe but is a latent type mismatch (consistent with the codebase's convention of storing handles as u32 across no_gui and sdl). p_bytes (u8* / uint8_t*) binds to send()'s const void *buf with no conversion. length_of__bytes (Quantity__u32 / uint32_t) widens to send()'s size_t len with no loss. The return of send() is ssize_t, narrowed to i32 (int32_t); this is safe in practice because send(2) only ever returns values in [-1, INT_MAX], and INT_MAX equals INT32_MAX, so no value is truncated.
No undefined behavior — the wrapper itself performs no pointer arithmetic, no type punning, and no out-of-bounds access. A null or dangling p_PLATFORM_tcp_socket or p_bytes would be undefined, but those violate the pre-conditions above and are the caller's responsibility.
Validation — no null/length checks are performed. This is appropriate for a thin syscall wrapper; asserting validity here would duplicate work already done (or that must be done) by the PLATFORM_tcp_* callers, so the function's role is correctly limited to delegation.

Side Effects:
- Performs a network transmission: the kernel sends up to length_of__bytes bytes over the TCP connection identified by socket_handle (modifies kernel socket/send-buffer state; may also trigger ACK/timeout behavior on the peer).
- May set errno on error.
- Does not modify the p_bytes buffer (send is read-only) and does not mutate the PLATFORM_TCP_Socket struct or its socket_handle field as observable to the caller.
