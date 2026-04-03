# Specification: core/include/game_action/core/tcp/game_action__tcp_connect.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__TCP_Connect` game action. This action represents the
authentication/connection confirmation step in the TCP handshake.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u64`)
- `game.h` (for `dispatch_game_action`)

## Game_Action_Kind

`Game_Action_Kind__TCP_Connect`

## Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__tcp_connect__session_token` | `Identifier__u64` | The session token confirming the connection. |

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__tcp_connect` | `(Game_Action_Logic_Table*) -> void` | Registers the TCP connect action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__tcp_connect` | `(Game_Action*, Identifier__u64 session_token) -> void` | Initializes the action with the session token. |

### Receive

| Function | Signature | Description |
|----------|-----------|-------------|
| `receive_game_action__connect` | `(Game*, Identifier__u32 session_token) -> void` | Handles reception of a connect action. |

### Dispatch (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `dispatch_game_action__connect` | `(Game*, Identifier__u32 session_token) -> void` | Creates and dispatches the connect action. |

## Agentic Workflow

### Connection Sequence Position

This action occurs after `TCP_Connect__Begin` and before
`TCP_Connect__Accept` or `TCP_Connect__Reject`:

    Client                          Server
      |-- TCP_Connect__Begin -------->|
      |                               |-- (validates)
      |<-------- TCP_Connect ---------|
      |                               |
      |   (or TCP_Connect__Accept)    |
      |   (or TCP_Connect__Reject)    |

### Preconditions

- A TCP connection must already be established via `TCP_Connect__Begin`.

### Postconditions

- The session token is communicated between client and server.
