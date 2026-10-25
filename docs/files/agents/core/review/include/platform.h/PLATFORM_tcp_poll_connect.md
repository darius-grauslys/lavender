PLATFORM_tcp_poll_connect

## 1. Header
- **Function name:** `PLATFORM_tcp_poll_connect`
- **File of origin:** `core/include/platform.h` (declaration, line 399). This is a platform-abstraction API with no in-core implementation; the actual implementations are platform-specific and are identical in logic:
  - `sdl/source/multiplayer/sdl_tcp_context.c` (line 157)
  - `no_gui/source/multiplayer/no_gui_tcp_context.c` (line 166)

## 2. Semantic
Polls a non-blocking TCP socket to determine the final status of an in-progress outgoing `connect()` initiated by `PLATFORM_tcp_connect`, and returns the resulting `TCP_Socket_State` (`Connecting`, `Connected`, or `Disconnected`). Per the header doc-comment and `agents/platform_api.md`, it is intended to be called every loop/frame following `PLATFORM_tcp_connect` using the returned socket.

## 3. Pre-conditions
1. `p_PLATFORM_tcp_socket` is a valid, non-null pointer to an initialized `PLATFORM_TCP_Socket` (allocated from a `PLATFORM_TCP_Context`, with `socket_handle` holding a valid OS socket descriptor and `addr_in` populated).
2. The socket was produced by `PLATFORM_tcp_connect`, which set the OS socket to non-blocking mode and filled in `addr_in` with the destination address.
3. The socket is not a server/listening socket; it is a client socket whose connection is still being awaited.
4. The caller is in a frame/loop where polling the connection is appropriate (the high-level caller gates this on state being `TCP_Socket_State__None` or `TCP_Socket_State__Connecting`).

## 4. Post-conditions
1. Returns `TCP_Socket_State__Connecting` if the connection is still in progress.
2. Returns `TCP_Socket_State__Connected` if the connection has completed successfully.
3. Returns `TCP_Socket_State__Disconnected` if the connection has failed.
4. The `PLATFORM_TCP_Socket` struct itself is not mutated by this function; assignment of the returned state to the higher-level `TCP_Socket` is performed by the caller (`poll_tcp_socket_for__connection` in `core/source/multiplayer/tcp_socket.c:82`).
5. `errno` is left in an indeterminate state (it is only meaningful as a result of the `connect()` call made within this function).

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The semantic intent is that a socket whose connection is still in progress must be reported as `TCP_Socket_State__Connecting` (so the caller keeps polling) until the connection either succeeds (`Connected`) or fails (`Disconnected`). The implementation does **not** fulfill this intent:

- On the first poll, `connect()` returns `-1` with `errno = EINPROGRESS`, which is correctly mapped to `Connecting`.
- On every subsequent poll while the connection is still in progress, Linux's `connect()` returns `-1` with `errno = EALREADY` (an in-progress connection is re-attempted). `EALREADY` is **not** present in the `switch`, so execution falls through to `default`, which returns `TCP_Socket_State__Disconnected` and logs a spurious error.

Because the contract requires this function to be called "every frame during connection," any connection that does not complete within a single frame is premature reported as `Disconnected` on the second poll. The high-level caller (`poll_tcp_socket_for__connection`) then stores `Disconnected`, which trips its `default` short-circuit and permanently halts polling — so a remote connection with any latency beyond one frame can never succeed. This is a semantic failure: the assumption "a not-yet-complete connect stays `Connecting`" does not hold.

## 7. Implementation Correctness
- **Unhandled `EALREADY` (correctness bug):** `EWOULDBLOCK` and `EINPROGRESS` are handled, but the `EALREADY` value — the one Linux actually yields on a re-issued `connect()` against a still-connecting socket — is not. It falls to `default`, producing the spurious `Disconnected` described above.
- **Non-portable polling technique:** Re-issuing `connect()` to probe connection status is not the POSIX-recommended pattern for non-blocking connects. The portable approach is: call `connect()` once (yields `EINPROGRESS`), then poll for writability with `select()`/`poll()`, and finally use `getsockopt(fd, SOL_SOCKET, SO_ERROR, ...)` to read the definitive result (0 = connected; nonzero = the connect error). Repeated `connect()` behavior on an in-progress socket is implementation-defined, so relying on it is fragile across platforms (note NDS has no implementation at all, per `platform_api.md`).
- **`EWOULDBLOCK` handling is misleading:** On Linux, `connect()` for a non-blocking socket returns `EINPROGRESS` (not `EWOULDBLOCK`) for the initial attempt, so the `EWOULDBLOCK`/`EAGAIN` case is effectively dead here.
- **No null-validation:** `p_PLATFORM_tcp_socket` is dereferenced (`->socket_handle`, `->addr_in`) without a null check. This is inconsistent with `PLATFORM_tcp_close_socket` (which null-checks) and relies entirely on the caller's guarantee; under the guide's "validation appropriateness" lens this is a caller-responsibility gap rather than a hard defect for a per-frame platform API, but it is worth flagging for consistency.
- **Type compatibility (minor):** `socket_handle` is stored as `u32` (`no_gui/include/no_gui_defines.h:100`) and implicitly converted to `int` when passed to `connect()`. Valid descriptors fit this range, so no truncation occurs in practice; not a defect.

## 8. Side Effects
- Issues a `connect()` syscall against the underlying OS socket handle. This is the function's intended side effect: it initiates and/or probes the TCP 3-way handshake.
- `errno` is modified as a result of the `connect()` call.
- Logging side effects: emits `debug_info(...)` on a successful connection and `debug_error(...)` on a failure path. No mutation of the `PLATFORM_TCP_Socket` struct or any caller-visible struct is performed by this function itself.
