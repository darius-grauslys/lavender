# Specification: core/include/game_action/core/global_space/game_action__global_space__resolve.h

## Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__Global_Space__Resolve` game action. This action
signals that a global space (chunk) at the specified coordinates has
been resolved (loaded/generated and is ready for use).

## Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `Global_Space_Vector__3i32`)
- `game.h` (for `dispatch_game_action_to__server`)

## Game_Action_Kind

`Game_Action_Kind__Global_Space__Resolve`

## Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__global_space__resolve__gsv__3i32` | `Global_Space_Vector__3i32` | Chunk coordinates of the resolved global space. |

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__global_space__resolve` | `(Game_Action_Logic_Table*) -> void` | Registers the global space resolve action kind. |

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__global_space__resolve` | `(Game_Action*, Global_Space_Vector__3i32) -> void` | Initializes a resolve action for the given chunk coordinates. |

### Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__global_space__resolve` | `(Game*, Global_Space_Vector__3i32) -> bool` | `bool` | Dispatches a global space resolve to the server. |

## Agentic Workflow

### Chunk Resolution Flow

This action is the completion signal for a `Global_Space__Request`:

    Request -> (load/generate) -> Resolve

### Preconditions

- A corresponding `Global_Space__Request` should have been issued.
- The chunk data must be fully loaded/generated.

### Postconditions

- The global space is marked as active and ready for rendering and
  collision detection.
