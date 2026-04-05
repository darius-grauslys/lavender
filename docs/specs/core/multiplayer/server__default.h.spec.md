# Specification: core/include/multiplayer/server__default.h

## Overview

Provides the default server-side polling implementation for the
`TCP_Socket_Manager`. This is the standard `m_Poll_TCP_Socket_Manager`
callback used when the game is operating as a server (host) in a
multiplayer session.

## Dependencies

- `defines.h` (for `TCP_Socket_Manager`, `Game`)
- `defines_weak.h` (forward declarations)

## Functions

### Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_poll_tcp_socket_manager_as__server__default` | `(TCP_Socket_Manager*, Game*) -> void` | Default server-side polling callback. Drives the server's TCP socket I/O each frame, handling inbound connection acceptance/rejection, packet reception from connected clients, and packet dispatch. |

## Agentic Workflow

### Role in TCP_Socket_Manager

This function is passed to `initialize_tcp_socket_manager` as the
`m_Poll_TCP_Socket_Manager` callback when the game is configured as
a server (i.e. `GAME_FLAG__IS_SERVER_OR__CLIENT` indicates server mode):

    initialize_tcp_socket_manager(
        p_tcp_socket_manager,
        m_poll_tcp_socket_manager_as__server__default);

### Per-Frame Behavior

Each frame, the `TCP_Socket_Manager` invokes this callback:

    m_poll_tcp_socket_manager(p_tcp_socket_manager, p_game);

The default server implementation:

    1. Poll the server (listening) socket for pending connections:
       → poll_tcp_socket_manager_for__pending_connections(...)
       → If pending: evaluate via game action logic
           → accept_pending_connection(...) or reject_pending_connection(...)

    2. For each active client TCP_Socket in the pool:
       a. Skip sockets where is_tcp_socket__manually_driven() is true.
       b. If state is Connected or later: call receive_bytes_over__tcp_socket().
       c. Process received packets as inbound game actions via the
          corresponding Client's game_action_manager__inbound.
       d. Send any queued outbound game actions from the Client's
          game_action_manager__outbound.

### Server vs Client

The server polling strategy differs from the client strategy in that:

- It **does** poll for pending inbound connections on the server socket.
- It manages **multiple** concurrent client connections (up to
  `MAX_QUANTITY_OF__TCP_SOCKETS` minus the server socket itself).
- It is responsible for connection acceptance/rejection decisions.
- It may broadcast outbound game actions to multiple clients.

### Connection Acceptance Flow

    poll_tcp_socket_manager_for__pending_connections(...)
        → PLATFORM_tcp_poll_accept(...)
        → if pending:
            → Game logic evaluates (session token, capacity, etc.)
            → accept_pending_connection(manager, uuid)
                → allocates TCP_Socket from pool
                → binds PLATFORM_TCP_Socket
                → increments quantity_of__connections
            OR
            → reject_pending_connection(manager)
                → PLATFORM_tcp_close_socket(...)
                → clears p_PLATFORM_tcp_socket__pending_connection

### Preconditions

- `p_tcp_socket_manager` must be initialized with a server socket open
  via `open_server_socket_on__tcp_socket_manager__ipv4`.
- `p_game` must be valid and in a multiplayer server state.

### Postconditions

- Pending connections have been accepted or rejected.
- All non-manually-driven client sockets have been polled for I/O.
- Received packets have been enqueued as inbound game actions.
