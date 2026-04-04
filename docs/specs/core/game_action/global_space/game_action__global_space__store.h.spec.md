# Specification: core/include/game_action/core/global_space/game_action__global_space__store.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__Global_Space__Store` game action. This action
requests that a global space (chunk) at the specified coordinates be
serialized (saved) to persistent storage.

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `Global_Space_Vector__3i32`)
- `game.h` (for `dispatch_game_action_to__server`)

## Game_Action_Kind

`Game_Action_Kind__Global_Space__Store`

## Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__global_space__store__gsv__3i32` | `Global_Space_Vector__3i32` | Chunk coordinates of the global space to store. |

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__global_space__store` | `(Game_Action_Logic_Table*) -> void` | Registers the global space store action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__global_space__store` | `(Game_Action*, Global_Space_Vector__3i32) -> void` | Initializes a store action for the given chunk coordinates. |

### Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__global_space__store` | `(Game*, Global_Space_Vector__3i32) -> bool` | `bool` | Dispatches a global space store to the server. |

## Agentic Workflow

### Chunk Persistence Flow

1. A chunk is modified (tiles updated, `CHUNK_FLAG__IS_UPDATED` set).
2. When the chunk is about to be unloaded or the game is saving,
   `dispatch_game_action__global_space__store(p_game, chunk_coords)`.
3. The chunk data is serialized to disk via the platform file system.

### Preconditions

- The chunk at the specified coordinates must be loaded and active.
- The chunk should have the `CHUNK_FLAG__IS_UPDATED` flag set.

### Postconditions

- The chunk data is written to persistent storage.
- The `CHUNK_FLAG__IS_UPDATED` flag may be cleared after successful save.
