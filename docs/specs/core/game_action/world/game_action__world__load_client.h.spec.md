# 1. Specification: core/include/game_action/core/world/game_action__world__load_client.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
world load client game action. This action requests that a specific
client's persistent data be loaded from disk.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Identifier__u32`)
- `game.h` (for `dispatch_game_action_to__server`)

## 1.3. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__world__load_world__uuid_of__client__u32` | `Identifier__u32` | UUID of the client whose data should be loaded. |

## 1.4. Functions

### 1.4.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__world__load_client` | `(Game_Action_Logic_Table*) -> void` | Registers the world load client action kind. |

### 1.4.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__world__load_client` | `(Game_Action*, Identifier__u32 client_uuid) -> void` | Initializes a load client action for the specified client UUID. |

### 1.4.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__world__load_client` | `(Game*, Identifier__u32 client_uuid) -> bool` | `bool` | Dispatches a load client request to the server. |

## 1.5. Agentic Workflow

### 1.5.1. Client Data Loading

1. A client connects or the game starts.
2. `dispatch_game_action__world__load_client(p_game, client_uuid)`.
3. The server loads the client's persistent data from disk via
   `dispatch_handler_process_to__load_client`.
4. On success, the client is marked as loaded (`set_client_as__loaded`).
5. On failure, the client is marked as failed (`set_client_as__failed_to_load`),
   and a fresh client may be created instead.

### 1.5.2. Preconditions

- The client must be allocated.
- The game's file system context must be initialized.

### 1.5.3. Postconditions

- The client's persistent data is loaded from disk.
- The client's flags reflect the load result.
