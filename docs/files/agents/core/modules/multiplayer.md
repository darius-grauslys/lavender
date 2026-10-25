# Multiplayer — TCP transport layer between client and server

**Sources:** `core/source/multiplayer/tcp_socket.c` + `tcp_socket_manager.c` + `core/include/multiplayer/tcp_socket.h` + `tcp_socket_manager.h`

## Surface Concerns

The multiplayer module owns the TCP transport layer: a single `TCP_Socket_Manager` manages a pool of `TCP_Socket` objects, each with a fixed-capacity ring buffer for received packets. Socket lifecycle (connect/accept/bind/unbind) and non-blocking connect polling are handled here; actual TCP I/O is delegated to `platform.h` (9 TCP functions). The default poll implementations wire received packets into the game-action receive pipeline via type punning through the `TCP_DELIVERY` union.

Driven by `poll_multiplayer()` (game.c), which invokes the `m_Poll_TCP_Socket_Manager` callback installed in `begin_multiplayer_for__game`. Note: `poll_multiplayer()` is not called from core's frame loop (`manage_game__post_render`) as of today — the game layer or backend must drive it.

- **Socket pool** — A single-slot pool (`MAX_QUANTITY_OF__TCP_SOCKETS=1`) of `TCP_Socket` structs, UUID-indexed with a fast ptr-array for iteration. Each socket owns a 256-entry ring buffer of 512-byte packets.
- **Non-blocking connect** — Client sockets transition through `Connecting` -> `Connected` (or `Disconnected`) via `poll_tcp_socket_for__connection` calling `PLATFORM_tcp_poll_connect`. Server sockets accept incoming connections via `poll_tcp_socket_manager_for__pending_connections`.
- **Packet queue** — Fixed-size ring buffer using `MASK` bit arithmetic for indexing. Enqueue via `receive_bytes_over__tcp_socket` (returns `TCP_ERROR__QUEUE_FULL` when 256 packets are buffered), dequeue via `get_latest__delivery_from__tcp_socket` (FIFO, zeroes the slot after copy, false when empty).
- **Zero-copy delivery** — The `TCP_DELIVERY(type, name)` macro overlays a concrete type (e.g. `Game_Action`) on top of `TCP_Packet`, allowing casts to dispatch received packets through the existing `receive_game_action` pipeline.
- **Client/server symmetry** — Both paths converge on `receive_game_action`. Server dispatches with each client's UUID; client dispatches with `uuid_of__client__u32 = 0` (local player). The same action logic table processes both.
- **Fixed capacity / no core allocation** — Socket pool, packet queue, and packet size are all compile-time arrays. The only heap allocation is `Game.pM_tcp_socket_manager`, allocated once at begin-multiplayer.
- **Session identity** — `Session_Token` carries a `u64` player UUID; `get_uuid_u32_of__session_token_player_uuid_u64` compresses it to a `u32` identifier via bit masking and `Lavender_Type__Player` branding.
- **IPv4 address parsing** — `populate_ipv4_address` converts dotted-decimal IP strings and port numbers into `IPv4_Address` structs.

## Key Types

**`TCP_Socket_State`** — defined in `defines_weak.h`. States for the non-blocking connect state machine: `None`, `Disconnected`, `Connecting`, `Connected`, `Authenticating`, `Authenticated`, `Unknown`.

**`TCP_Socket`** — defined in `defines.h`. One socket connection:
- `Serialization_Header _serialization_header` — pool identity branding.
- `TCP_Packet queue_of__tcp_packet[256]` — fixed-capacity packet ring buffer.
- `Quantity__u16 packet_size__entries[256]` — byte size of each enqueued packet.
- `IPv4_Address tcp_socket__address` — peer address.
- `PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket` — platform socket handle.
- `Index__u32 index_of__enqueue_begin` — ring buffer read head.
- `Quantity__u32 quantity_of__received_packets` — packet count in queue.
- `TCP_Socket_State tcp_socket__state_of` — connection state.
- `TCP_Socket_Flags__u8 tcp_socket_flags__u8` — socket flags.

**`TCP_Socket_Manager`** — defined in `defines.h`. Owns the socket pool:
- `TCP_Socket tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS]` — ID-based pool (each slot carries its `Serialization_Header`).
- `TCP_Socket *ptr_array_of__tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS]` — fast ptr-array iteration.
- `PLATFORM_TCP_Context *p_PLATFORM_tcp_context` — platform TCP context.
- `m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager` — installed poll callback.
- `PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__pending_connection` — pending accept handle.
- `IPv4_Address ipv4__pending_connection` — pending connect address.
- `Quantity__u32 quantity_of__connections` — active connection count.

**`Session_Token`** — defined in `defines.h` (`session_token.h` provides the UUID-extraction inline). Carries `player_uuid` + `session_token` (both `u64`) for server-side identity.

## Key Functions

- `void initialize_tcp_socket(TCP_Socket *p, IPv4_Address, Identifier__u32);`
- `void initialize_tcp_socket_as__deallocated(TCP_Socket *p);` — brands socket as free in the pool.
- `void bind_tcp_socket(TCP_Socket *, PLATFORM_TCP_Socket *);` / `void unbind_tcp_socket(PLATFORM_TCP_Context *, TCP_Socket *);`
- `TCP_Socket *accept_socket_on__tcp_socket_manager__ipv4(TCP_Socket_Manager *, PLATFORM_TCP_Socket *, IPv4_Address, Identifier__u32);` — accepts pending connection.
- `TCP_Socket *open_socket_on__tcp_socket_manager__ipv4(TCP_Socket_Manager *, IPv4_Address, Identifier__u32);` — opens outgoing client socket.
- `TCP_Socket *open_server_socket_on__tcp_socket_manager__ipv4(TCP_Socket_Manager *, Identifier__u32, Index__u16);` — binds a listening server socket.
- `void close_socket_on__tcp_socket_manager__ipv4(TCP_Socket_Manager *, TCP_Socket *);` — unbinds and deallocates.
- `TCP_Socket_State poll_tcp_socket_for__connection(TCP_Socket *);` — non-blocking connect poll; returns new state.
- `void send_bytes_over__tcp_socket(TCP_Socket *, u8 *, Quantity__u32);`
- `i32 receive_bytes_over__tcp_socket(TCP_Socket *);` — returns total bytes received or error code.
- `bool get_latest__delivery_from__tcp_socket(TCP_Socket *, TCP_Packet *);` — dequeues one packet (FIFO).
- `void initialize_tcp_socket_manager(TCP_Socket_Manager *, m_Poll_TCP_Socket_Manager);`
- `PLATFORM_TCP_Socket *poll_tcp_socket_manager_for__pending_connections(TCP_Socket_Manager *, TCP_Socket *, IPv4_Address *);` — returns pending accept handle or 0.
- `TCP_Socket *accept_pending_connection(TCP_Socket_Manager *, Identifier__u32);` — returns socket or 0 on failure.
- `void reject_pending_connection(TCP_Socket_Manager *);`
- `static inline TCP_Socket *get_p_tcp_socket_for__this_uuid(TCP_Socket_Manager *, Identifier__u32);` / `Quantity__u32 get_quantity_of__active_tcp_sockets(TCP_Socket_Manager *);`
- `static inline PLATFORM_TCP_Context *get_p_PLATFORM_tcp_context_from__tcp_socket_manager(TCP_Socket_Manager *);`
- `void m_poll_tcp_socket_manager_as__client__default(TCP_Socket_Manager *, Game *);` — default client poll: connect, receive, dispatch actions.
- `void m_poll_tcp_socket_manager_as__server__default(TCP_Socket_Manager *, Game *);` — default server poll: accept, auth, receive, dispatch actions.
- `bool populate_ipv4_address(IPv4_Address *, const char *, const char *);` — parses IP string and port.
- `bool is_in_multiplayer_game(Game *);` / `bool is_host(Game *);` / `get_user_id(Game *);` — declared in `multiplayer.h`, no core implementations (and `USER_ID`, the declared return type of `get_user_id`, is undefined).

## Key Files Table

| File | Role |
|------|------|
| `core/source/multiplayer/tcp_socket_manager.c` | Socket pool management: alloc, accept, open, close, pending connection polling |
| `core/source/multiplayer/tcp_socket.c` | Socket lifecycle: connect polling, send/receive, packet queue, bind/unbind |
| `core/source/multiplayer/server__default.c` | Default server poll: pending conn handling, auth, client iteration |
| `core/source/multiplayer/client__default.c` | Default client poll: connect polling, packet receive, action dispatch |
| `core/source/multiplayer/ipv4_address.c` | IPv4 string parsing |
| `core/include/multiplayer/tcp_socket_manager.h` | Manager API and inline helpers |
| `core/include/multiplayer/tcp_socket.h` | Socket API, `TCP_DELIVERY` macro, state helpers, flags |
| `core/include/multiplayer/ipv4_address.h` | IPv4 parser declaration |
| `core/include/multiplayer/server__default.h` | Server poll function declaration |
| `core/include/multiplayer/client__default.h` | Client poll function declaration |
| `core/include/multiplayer/session_token.h` | Session token UUID-extraction inline |
| `core/include/multiplayer/multiplayer.h` | `is_in_multiplayer_game`, `is_host`, `get_user_id` (declared, unimplemented) |
| `core/include/defines.h` | `TCP_Socket`, `TCP_Socket_Manager`, `Session_Token`, capacity constants |
| `core/include/defines_weak.h` | `TCP_Socket_State` enum, primitive types |
