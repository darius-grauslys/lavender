# 1. Specification: core/include/game_action/core/entity/game_action__entity__spawn.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__Entity__Spawn` game action. This action requests
the spawning of an entity of a given kind, optionally with a specific
UUID. Supports both targeted dispatch and broadcast dispatch.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`,
  `Entity_Kind`, `Identifier__u32`)
- `game.h` (for `dispatch_game_action_to__server`)
- `game_action/game_action.h` (for `set_game_action_as__broadcasted`)
- `types/implemented/entity_kind.h` (for `Entity_Kind` enum)
- `vectors.h` (for `Vector__3i32F4`, `VECTOR__3i32F4__OUT_OF_BOUNDS`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__Entity__Spawn`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__entity__uuid` | `Identifier__u32` | UUID to assign to the spawned entity. |
| `ga_kind__entity__the_kind_of__entity` | `Entity_Kind` | The kind of entity to spawn. |

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__entity__spawn_for__server` | `(Game_Action_Logic_Table*) -> void` | Registers entity spawn for server-side processing. |
| `register_game_action__entity__spawn_for__client` | `(Game_Action_Logic_Table*) -> void` | Registers entity spawn for client-side processing. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__entity__spawn` | `(Game_Action*, Identifier__u32 uuid, Entity_Kind kind) -> void` | Initializes an entity spawn action. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__entity__spawn` | `(Game*, Identifier__u32 uuid, Entity_Kind kind) -> bool` | `bool` | Dispatches a targeted entity spawn to the server. |
| `broadcast_game_action__entity__spawn` | `(Game*, Identifier__u32 uuid, Entity_Kind kind, Vector__3i32F4 broadcast_point) -> bool` | `bool` | Dispatches a broadcast entity spawn. Set `broadcast_point` to `VECTOR__3i32F4__OUT_OF_BOUNDS` for global broadcast. |

## 1.6. Agentic Workflow

### 1.6.1. Targeted vs Broadcast

- **Targeted**: `dispatch_game_action__entity__spawn` sends to the server
  for authoritative processing.
- **Broadcast**: `broadcast_game_action__entity__spawn` sets the broadcast
  flag and broadcast point, causing the server to forward the spawn to
  all clients near the broadcast point.

### 1.6.2. Preconditions

- The entity kind must be a valid `Entity_Kind` (not `Entity_Kind__Unknown`).
- For broadcast, the broadcast point determines which clients receive the
  action. Use `VECTOR__3i32F4__OUT_OF_BOUNDS` for global broadcast.

### 1.6.3. Postconditions

- The server processes the spawn request and creates the entity.
- In broadcast mode, all relevant clients are notified.
