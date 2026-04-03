# Specification: core/include/game_action/core/tcp/game_action__tcp_connect__reject.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect__Reject` game action. This action is
invoked by the **TCP server** (not the client) to reject a client's
connection request.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Client`)
- `game.h` (for `dispatch_game_action`, `GET_UUID_P`)

## Game_Action_Kind

`Game_Action_Kind__TCP_Connect__Reject`

## Payload Fields

No kind-specific payload fields. The client UUID in the header identifies
which client is being rejected.

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect__reject` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect reject action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect__reject` | `(Game_Action*, Client*) -> void` | Initializes the reject action for the given client. |

### Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect__reject` | `(Game*, Client*) -> void` | Creates and dispatches the reject action to the specified client. Uses `GET_UUID_P(p_client)` for the client UUID. |

## Agentic Workflow

### Server-Side Only

This action is only dispatched by the server. The client receives it
as an inbound action indicating their connection was rejected.

### Preconditions

- `p_client` must be a valid, allocated `Client` with a valid UUID.

### Postconditions

- The client is informed that their connection has been rejected.
- The server should clean up the client's TCP socket after dispatch.
