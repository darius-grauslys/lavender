# 1. Specification: core/include/multiplayer/client__default.h

## 1.1 Overview

Provides the default client-side polling implementation for the
`TCP_Socket_Manager`. This is the standard `m_Poll_TCP_Socket_Manager`
callback used when the game is operating as a client in a multiplayer
session.

## 1.2 Dependencies

- `defines.h` (for `TCP_Socket_Manager`, `Game`)
- `defines_weak.h` (forward declarations)

## 1.3 Functions

### 1.3.1 Polling

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_poll_tcp_socket_manager_as__client__default` | `(TCP_Socket_Manager*, Game*) -> void` | Default client-side polling callback. Drives the client's TCP socket I/O each frame, handling connection state transitions, packet reception, and packet dispatch for all active sockets in the manager's pool. |

## 1.4 Agentic Workflow

### 1.4.1 Role in TCP_Socket_Manager

This function is passed to `initialize_tcp_socket_manager` as the
`m_Poll_TCP_Socket_Manager` callback when the game is configured as
a client (i.e. `GAME_FLAG__IS_SERVER_OR__CLIENT` indicates client mode):

    initialize_tcp_socket_manager(
        p_tcp_socket_manager,
        m_poll_tcp_socket_manager_as__client__default);

### 1.4.2 Per-Frame Behavior

Each frame, the `TCP_Socket_Manager` invokes this callback:

    m_poll_tcp_socket_manager(p_tcp_socket_manager, p_game);

The default client implementation:

    1. For each active TCP_Socket in the pool:
       a. Skip sockets where is_tcp_socket__manually_driven() is true.
       b. If state is Connecting: call poll_tcp_socket_for__connection().
       c. If state is Connected or later: call receive_bytes_over__tcp_socket().
       d. Process received packets as inbound game actions via the
          Client's game_action_manager__inbound.

### 1.4.3 Client vs Server

The client polling strategy differs from the server strategy in that:

- It does **not** poll for pending inbound connections.
- It does **not** manage multiple independent client sessions.
- It focuses on maintaining a single outbound connection to the server
  and processing server-originated game actions.

### 1.4.4 Preconditions

- `p_tcp_socket_manager` must be initialized via `initialize_tcp_socket_manager`.
- `p_game` must be valid and in a multiplayer client state.

### 1.4.5 Postconditions

- All non-manually-driven sockets have been polled for I/O.
- Received packets have been enqueued as inbound game actions.
