# Specification: core/include/game_action/core/world/game_action__world__load_world.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__World__Load_World` game action. This action requests
that the world be loaded for a specific client, initializing the client's
local space manager and beginning chunk loading around the client's
position.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u32`)
- `game.h` (for `dispatch_game_action_to__server`)

## Game_Action_Kind

`Game_Action_Kind__World__Load_World`

## Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__world__load_world__uuid_of__client__u32` | `Identifier__u32` | UUID of the client for whom the world should be loaded. |

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__world__load_world` | `(Game_Action_Logic_Table*) -> void` | Registers the world load action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__world__load_world` | `(Game_Action*, Identifier__u32 client_uuid) -> void` | Initializes a world load action for the specified client. |

### Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__world__load_world` | `(Game*, Identifier__u32 client_uuid) -> bool` | `bool` | Dispatches a world load request to the server. |

## Agentic Workflow

### World Loading Sequence

1. Client connects and is accepted.
2. `dispatch_game_action__world__load_world(p_game, client_uuid)`.
3. The server initializes the client's local space manager.
4. Chunk requests are dispatched for the area around the client.
5. Once chunks are loaded, the client can begin gameplay.

### Preconditions

- The client must be allocated and active.
- The world must be allocated for the game (`is_world_allocated_for__game`).

### Postconditions

- The client's local space manager is initialized.
- Chunk loading begins for the client's surrounding area.
