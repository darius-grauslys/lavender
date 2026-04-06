# 1. Specification: core/include/game_action/core/tcp/game_action__tcp_connect__reject.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect__Reject` game action. This action is
invoked by the **TCP server** (not the client) to reject a client's
connection request.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Client`)
- `game.h` (for `dispatch_game_action`, `GET_UUID_P`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__TCP_Connect__Reject`

## 1.4. Payload Fields

No kind-specific payload fields. The client UUID in the header identifies
which client is being rejected.

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect__reject` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect reject action kind. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect__reject` | `(Game_Action*, Client*) -> void` | Initializes the reject action for the given client. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect__reject` | `(Game*, Client*) -> void` | Creates and dispatches the reject action to the specified client. Uses `GET_UUID_P(p_client)` for the client UUID. |

## 1.6. Agentic Workflow

### 1.6.1. Server-Side Only

This action is only dispatched by the server. The client receives it
as an inbound action indicating their connection was rejected.

### 1.6.2. Preconditions

- `p_client` must be a valid, allocated `Client` with a valid UUID.

### 1.6.3. Postconditions

- The client is informed that their connection has been rejected.
- The server should clean up the client's TCP socket after dispatch.
