### 1. Header
- **Function name**: `PLATFORM_tcp_poll_accept`
- **File of origin**: `core/include/platform.h` (declaration, line 422); implementations in `sdl/source/multiplayer/sdl_tcp_context.c` (SDL) and `no_gui/source/multiplayer/no_gui_tcp_context.c` (no-GUI)

### 2. Semantic
Checks a non-blocking TCP server socket for incoming connection requests. When a connection is pending, accepts it, allocates a fresh `PLATFORM_TCP_Socket` from the context's pool, optionally records the peer's `IPv4_Address`, sets the new socket to non-blocking mode, and returns it. Returns null when no connection is pending or on any error.

### 3. Pre-conditions
1. `p_PLATFORM_tcp_context` must be non-null and point to a valid, initialized `PLATFORM_TCP_Context` whose socket pool contains a free slot for the new connection.
2. `p_PLATFORM_tcp_socket__server` must be non-null and point to an initialized, bound, listening, non-blocking server socket (created via `PLATFORM_tcp_server`); its `socket_handle` must be a valid open socket descriptor.
3. `p_ipv4` may be null (optional output); if non-null, it must point to writable memory.
4. The calling thread owns the server socket; `accept` is non-blocking (`O_NONBLOCK` set during `PLATFORM_tcp_server`), so it returns `-1`/`EAGAIN` when idle rather than blocking.

### 4. Post-conditions
1. Returns a pointer to a newly-allocated `PLATFORM_TCP_Socket` from the context pool, configured non-blocking and bound to the accepted connection; OR returns null (`0`).
2. Returns null when no connection is pending (`accept` returned `-1` with `errno == EAGAIN` or `EWOULDBLOCK`).
3. Returns null on error — pool exhaustion (after closing the leaked descriptor) or failure to set non-blocking mode (after closing the descriptor and resetting the pool slot to inactive via `initialize ... as__inactive`).
4. If `p_ipv4` is non-null and a connection was accepted, it is populated with the peer's IPv4 address in host byte order (`ip_bytes[0..3]` and `port`).
5. No partially-allocated state is leaked: every error path closes the accepted file descriptor and resets the pool slot before returning null.

### 5. Correctness Verdict
Correct

### 6. Semantic Alignment
The implementations (SDL and no-GUI) faithfully realize the documented intent. The `accept` call is made on the server socket; `EAGAIN`/`EWOULDBLOCK` is correctly distinguished from genuine errors (only `EAGAIN`/`EWOULDBLOCK` are treated as "no pending connection" — other `errno` values log an error and return null). The IPv4 extraction (`ntohl` + byte-shift into `ip_bytes`, `ntohs` for `port`) yields the correct host-byte-order representation. Pool-slot allocation failure is handled by closing the just-accepted descriptor. Non-blocking setup via `fcntl(F_GETFL`/`F_SETFL | O_NONBLOCK)` is correct, and its failure path properly closes and resets the slot in both implementations. No semantic drift is present.

### 7. Implementation Correctness
- **Type compatibility**: `accept` expects `int` for its first argument but `socket_handle` is `u32`; the implicit unsigned-to-signed conversion is safe for all real socket descriptors (small non-negative values), but is technically a type mismatch. `socket_handle__new_connection` is an `int` compared against `-1`, which is correct.
- **Undefined behavior**: None — `p_PLATFORM_tcp_socket__server` is dereferenced without a null check, but this is the caller's responsibility (validation is not this function's role for already-validated server sockets); `p_ipv4` is null-checked before use. The `sockaddr_in`/`socklen_t` usage and `sockaddr*` cast are standard and valid.
- **Validation**: No parameter null-validation is performed for `p_PLATFORM_tcp_context` or `p_PLATFORM_tcp_socket__server` — consistent with the Lavender convention that pre-conditions are the caller's responsibility (the server socket is obtained via `PLATFORM_tcp_server` and the context via context initialization). No additional validation is warranted.

### 8. Side Effects
- **Allocates** a pool slot from `p_PLATFORM_tcp_context` (via the platform-specific allocator) on a successful accept.
- **Writes** the peer `IPv4_Address` into `*p_ipv4` when non-null (successful accept only).
- **Opens** an OS file descriptor via `accept`.
- **Mutates** the allocated `PLATFORM_TCP_Socket` struct (via `initialize ... _PLATFORM_tcp_socket`) and its `socket_handle`.
- **Sets** the new socket non-blocking via `fcntl`.
- **Error-path effects**: closes the leaked descriptor and resets the pool slot to inactive (`initialize ... as__inactive`) on allocation failure or non-blocking setup failure.
- No side effects on `p_PLATFORM_tcp_socket__server` beyond the `accept` system call (server socket handle is not modified).

### Notes
- The original review file claimed "(no implementation found)" — implementations exist in both `sdl/source/multiplayer/sdl_tcp_context.c` and `no_gui/source/multiplayer/no_gui_tcp_context.c`; the header is a declaration, platform implementations are per-frontend.
- Both implementations' `fcntl`-failure debug message incorrectly says "PLATFORM_tcp_connect" (copy-paste from `PLATFORM_tcp_connect`) rather than "PLATFORM_tcp_poll_accept". This is a cosmetic/logging issue that does not affect correctness but makes debugging confusing.
- The no-GUI `PLATFORM_tcp_close_socket` inverts its return-value contract relative to the header ("Returns true if any errors were encountered"): it returns `false` on close failure and `true` on success. The SDL version matches the documented contract. Within `PLATFORM_tcp_poll_accept` the no-GUI path does **not** call `PLATFORM_tcp_close_socket` (it closes and resets the slot directly), so this inconsistency does not affect this function; it is a separate bug in `PLATFORM_tcp_close_socket`.
