# 1. Specification: core/include/game_action/core/entity/game_action__entity__get.h

## 1.1. Overview

Provides initialization, registration, and dispatch for an entity data
request game action. This action requests entity data from the server,
typically used when a client needs to synchronize an entity it doesn't
have locally.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u32`)
- `game.h` (for `dispatch_game_action_to__server`)

## 1.3. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__entity__uuid` | `Identifier__u32` | UUID of the entity to request data for. |
| `ga_kind__entity__get__entity_data_payload_bitmap` | `TCP_PAYLOAD_BITMAP(Entity, ...)` | Bitmap tracking which payload fragments have been received (for multi-packet entity data). |

## 1.4. Functions

### 1.4.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__entity__get_for__server` | `(Game_Action_Logic_Table*) -> void` | Registers entity get for server-side processing. |
| `register_game_action__entity__get_for__client` | `(Game_Action_Logic_Table*) -> void` | Registers entity get for client-side processing. |

### 1.4.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__entity__get` | `(Game_Action*, Identifier__u32 target_uuid) -> void` | Initializes an entity get request for the specified entity UUID. |

### 1.4.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__entity__get` | `(Game*, Identifier__u32 target_uuid) -> bool` | `bool` | Dispatches an entity get request to the server. |

## 1.5. Agentic Workflow

### 1.5.1. Entity Synchronization Pattern

1. Client discovers an entity UUID it doesn't have data for.
2. Client calls `dispatch_game_action__entity__get(p_game, uuid)`.
3. Server receives the request and sends entity data back via
   `TCP_Delivery` fragments.
4. Client reassembles the entity data using the payload bitmap.

### 1.5.2. Preconditions

- The target UUID must be a valid entity UUID known to the server.

### 1.5.3. Postconditions

- The server sends entity data back to the requesting client.
