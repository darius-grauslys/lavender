# bind_tcp_socket

**File of origin:** `core/source/multiplayer/tcp_socket.c`

## Semantic

Associates a platform-level TCP socket handle with a `TCP_Socket` struct by storing the platform socket pointer in the struct. This is a binding operation that links the engine-level abstraction to the underlying platform socket.

## Pre-conditions

1. `p_tcp_socket` must be a valid, non-null pointer to an initialized `TCP_Socket` struct.
2. `p_PLATFORM_tcp_socket` may be null or non-null; it is a raw platform socket handle pointer. If non-null, it should reference a valid opened platform socket.
3. The `TCP_Socket` must not already be bound — i.e., `p_tcp_socket->p_PLATFORM_tcp_socket` must be null (0). Binding an already-bound socket is an error condition.

## Post-conditions

1. On success: `p_tcp_socket->p_PLATFORM_tcp_socket` is set to `p_PLATFORM_tcp_socket`.
2. On failure (already bound): the function calls `debug_abort` with an error message and returns early without modifying the struct.
3. The `TCP_Socket` struct's other fields remain unchanged.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent of binding a platform socket to the engine's `TCP_Socket` abstraction. The guard against double-binding (checking if `p_PLATFORM_tcp_socket` is already non-null) is consistent with the one-to-one ownership model where each `TCP_Socket` holds at most one platform socket handle. The `unbind_tcp_socket` counterpart resets the pointer to 0, confirming this is the intended lifecycle.

This is **not** a Lavender-style initialization function (no "init" in the name, no pool cleanup semantics). It is a binding/association operation.

## Implementation Correctness

- **Type compatibility:** The parameter `PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket` matches the struct field `p_PLATFORM_tcp_socket` of type `PLATFORM_TCP_Socket *` exactly. No implicit conversions or truncation.
- **Undefined behavior:** Dereferencing `p_tcp_socket` without a null check is a potential concern. However, the function does not check for null `p_tcp_socket`. If `p_tcp_socket` is null, the dereference on line 165 (`p_tcp_socket->p_PLATFORM_tcp_socket`) would be undefined behavior. That said, this is consistent with the codebase's convention where callers are expected to pass valid pointers (see `poll_tcp_socket_for__connection` which does null-check, but other functions like `set_state_of__tcp_socket` do not). The null-check responsibility is on the caller.
- **Validation:** The pre-condition check for already-bound sockets (`if (p_tcp_socket->p_PLATFORM_tcp_socket)`) is appropriate for this function's role. It prevents accidental re-binding which could leak the previous platform socket handle.

## Side Effects

- **Mutating:** Sets `p_tcp_socket->p_PLATFORM_tcp_socket` to the provided `p_PLATFORM_tcp_socket` pointer (on the success path).
- Calls `debug_abort` (which may log, assert, or terminate depending on build configuration) when the socket is already bound.
- No side effects on the `p_PLATFORM_tcp_socket` parameter itself.
