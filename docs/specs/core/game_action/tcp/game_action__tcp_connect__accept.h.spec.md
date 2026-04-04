# Specification: core/include/game_action/core/tcp/game_action__tcp_connect__accept.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect__Accept` game action. This action is
invoked by the **TCP server** (not the client) to accept a client's
connection request.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Client`)
- `game.h` (for `dispatch_game_action`, `GET_UUID_P`)

## Game_Action_Kind

`Game_Action_Kind__TCP_Connect__Accept`

## Payload Fields

No kind-specific payload fields. The client UUID in the header identifies
which client is being accepted.

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect__accept` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect accept action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect__accept` | `(Game_Action*, Client*) -> void` | Initializes the accept action for the given client. |

### Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect__accept` | `(Game*, Client*) -> void` | Creates and dispatches the accept action to the specified client. Uses `GET_UUID_P(p_client)` for the client UUID. |

## Agentic Workflow

### Server-Side Only

This action is only dispatched by the server. The client receives it
as an inbound action confirming their connection was accepted.

### Preconditions

- `p_client` must be a valid, allocated `Client` with a valid UUID.
- The client must have an active TCP connection.

### Postconditions

- The client is informed that their connection has been accepted.
- The client can now begin sending game actions.
