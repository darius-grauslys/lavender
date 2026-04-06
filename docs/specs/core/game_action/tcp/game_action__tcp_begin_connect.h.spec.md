# 1. Specification: core/include/game_action/core/tcp/game_action__tcp_begin_connect.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect__Begin` game action. This action is
invoked by the **TCP client** (not the server) to initiate a connection
to a remote server.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `IPv4_Address`, `Session_Token`)
- `game_action/game_action.h` (for `dispatch_game_action`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__TCP_Connect__Begin`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__tcp_connect__begin__ipv4_address` | `IPv4_Address` | The server's IPv4 address and port to connect to. |
| `ga_kind__tcp_connect__begin__session_token` | `Session_Token` | The client's session token for authentication. |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect__begin` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect begin action kind. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect__begin` | `(Game_Action*, IPv4_Address, Session_Token) -> void` | Initializes the action with the target address and session token. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect__begin` | `(Game*, IPv4_Address, Session_Token) -> void` | Creates and dispatches the connect begin action. Dispatches with client UUID 0 since the server has not yet assigned a UUID. |

## 1.6. Agentic Workflow

### 1.6.1. Connection Sequence

1. Client calls `dispatch_game_action__connect__begin(...)`.
2. The action is processed, initiating a TCP connection via
   `PLATFORM_tcp_connect`.
3. On success, the server responds with `TCP_Connect__Accept` or
   `TCP_Connect__Reject`.
4. On accept, the client receives a `TCP_Connect` action with the
   assigned session token.

### 1.6.2. Preconditions

- The game must have multiplayer initialized (`begin_multiplayer_for__game`).
- `IPv4_Address` must have valid IP bytes and port.
- `Session_Token` must be initialized.

### 1.6.3. Postconditions

- A TCP connection attempt is initiated to the specified address.

### 1.6.4. Important Notes

- The client UUID is passed as 0 to `dispatch_game_action` because the
  server has not yet determined the client's UUID. This is noted as a
  potential concern in the source but is functionally correct.
