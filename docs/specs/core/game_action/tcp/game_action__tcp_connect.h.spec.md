# 1. Specification: core/include/game_action/core/tcp/game_action__tcp_connect.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect` game action. This action represents the
authentication/connection confirmation step in the TCP handshake.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u64`)
- `game.h` (for `dispatch_game_action`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__TCP_Connect`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__tcp_connect__session_token` | `Identifier__u64` | The session token confirming the connection. |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect action kind. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect` | `(Game_Action*, Identifier__u64 session_token) -> void` | Initializes the action with the session token. |

### 1.5.3. Receive

| Function | Signature | Description |
|----------|-----------|-------------|
| `receive_game_action__connect` | `(Game*, Identifier__u32 session_token) -> void` | Handles reception of a connect action. |

### 1.5.4. Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect` | `(Game*, Identifier__u32 session_token) -> void` | Creates and dispatches the connect action. |

## 1.6. Agentic Workflow

### 1.6.1. Connection Sequence Position

This action occurs after `TCP_Connect__Begin` and before
`TCP_Connect__Accept` or `TCP_Connect__Reject`:

    Client                          Server
      |-- TCP_Connect__Begin -------->|
      |                               |-- (validates)
      |<-------- TCP_Connect ---------|
      |                               |
      |   (or TCP_Connect__Accept)    |
      |   (or TCP_Connect__Reject)    |

### 1.6.2. Preconditions

- A TCP connection must already be established via `TCP_Connect__Begin`.

### 1.6.3. Postconditions

- The session token is communicated between client and server.
