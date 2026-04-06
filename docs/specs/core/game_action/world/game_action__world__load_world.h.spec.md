# 1. Specification: core/include/game_action/core/world/game_action__world__load_world.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__World__Load_World` game action. This action requests
that the world be loaded for a specific client, initializing the client's
local space manager and beginning chunk loading around the client's
position.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u32`)
- `game.h` (for `dispatch_game_action_to__server`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__World__Load_World`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__world__load_world__uuid_of__client__u32` | `Identifier__u32` | UUID of the client for whom the world should be loaded. |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__world__load_world` | `(Game_Action_Logic_Table*) -> void` | Registers the world load action kind. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__world__load_world` | `(Game_Action*, Identifier__u32 client_uuid) -> void` | Initializes a world load action for the specified client. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__world__load_world` | `(Game*, Identifier__u32 client_uuid) -> bool` | `bool` | Dispatches a world load request to the server. |

## 1.6. Agentic Workflow

### 1.6.1. World Loading Sequence

1. Client connects and is accepted.
2. `dispatch_game_action__world__load_world(p_game, client_uuid)`.
3. The server initializes the client's local space manager.
4. Chunk requests are dispatched for the area around the client.
5. Once chunks are loaded, the client can begin gameplay.

### 1.6.2. Preconditions

- The client must be allocated and active.
- The world must be allocated for the game (`is_world_allocated_for__game`).

### 1.6.3. Postconditions

- The client's local space manager is initialized.
- Chunk loading begins for the client's surrounding area.
