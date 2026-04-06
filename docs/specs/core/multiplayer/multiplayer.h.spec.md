# 1. Specification: core/include/multiplayer/multiplayer.h

## 1.1 Overview

Provides top-level multiplayer state queries for the game session.
These functions determine whether the game is in a multiplayer context
and what role the local instance plays (host or client).

## 1.2 Dependencies

- `defines.h` (for `Game`, `Game_Flags__u32`)

## 1.3 Functions

### 1.3.1 State Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_in_multiplayer_game` | `(Game*) -> bool` | `bool` | Returns true if the game is currently in a multiplayer session (either as host or client). |
| `is_host` | `(Game*) -> bool` | `bool` | Returns true if the local game instance is the host (server) of the multiplayer session. |
| `get_user_id` | `(Game*) -> USER_ID` | `USER_ID` | Returns the local user's identifier for the current session. |

## 1.4 Agentic Workflow

### 1.4.1 Role Determination

The multiplayer system supports two roles, determined by the
`GAME_FLAG__IS_SERVER_OR__CLIENT` flag in `Game.game_flags__u32`:

- **Server (Host):** The game instance that accepts connections,
  manages authoritative world state, and broadcasts updates. The
  `TCP_Socket_Manager` uses `m_poll_tcp_socket_manager_as__server__default`.
- **Client:** The game instance that connects to a server and
  receives world state updates. The `TCP_Socket_Manager` uses
  `m_poll_tcp_socket_manager_as__client__default`.

### 1.4.2 Single-Player Detection

When `Game.max_quantity_of__clients == 0`, the game operates in
single-player mode. In this case `is_in_multiplayer_game` returns
false, and the game uses `Game.input` directly instead of per-client
input from `Client.input_of__client`.

### 1.4.3 Usage Pattern

These queries are used throughout the engine to branch behavior
based on multiplayer context:

    if (is_in_multiplayer_game(p_game)) {
        if (is_host(p_game)) {
            // Server-specific logic
        } else {
            // Client-specific logic
        }
    } else {
        // Single-player logic
    }

### 1.4.4 Relationship to TCP_Socket_Manager

- When `is_in_multiplayer_game` returns true, the game's
  `pM_tcp_socket_manager` is expected to be initialized and active.
- When `is_host` returns true, the `TCP_Socket_Manager` uses the
  server polling strategy.
- When `is_host` returns false (client), the `TCP_Socket_Manager` uses
  the client polling strategy.

### 1.4.5 Preconditions

- `p_game` must be non-null and initialized.

### 1.4.6 Postconditions

- These are pure query functions with no side effects.
