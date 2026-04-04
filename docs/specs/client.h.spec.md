# Specification: core/include/client.h

## Overview

Provides initialization, lifecycle management, game action dispatch/receive,
and flag manipulation for the `Client` struct. A `Client` represents a
connected player (local or remote) with inbound/outbound game action
queues, a local space manager for world visibility, and input state.

Clients are pooled and managed by the `Game` struct. Each client has its
own pair of `Game_Action_Manager` instances for bidirectional communication
and a `Local_Space_Manager` for tracking which chunks are loaded around
the client's position.

## Dependencies

- `defines.h` (for `Client`, `Client_Flags__u16`, `Game_Action_Manager`,
  `Local_Space_Manager`, `Input`, `Identifier__u32`,
  `Global_Space_Vector__3i32`, `Vector__3i32F4`)
- `defines_weak.h` (forward declarations for `Game`, `Process`,
  `TCP_Socket_Manager`, `Game_Action`)
- `game_action/game_action_manager.h`
- `serialization/serialized_field.h`

## Types

### Client (struct)

    typedef struct Client_t {
        Serialization_Header _serialization_header;
        Game_Action_Manager game_action_manager__inbound;
        Game_Action_Manager game_action_manager__outbound;
        Local_Space_Manager local_space_manager;
        Input input_of__client;
        Client_Flags__u16 client_flags__u16;
    } Client;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management. |
| `game_action_manager__inbound` | `Game_Action_Manager` | Queue for game actions received from the network or server. |
| `game_action_manager__outbound` | `Game_Action_Manager` | Queue for game actions to be sent to the network or server. |
| `local_space_manager` | `Local_Space_Manager` | Tracks loaded chunks around this client's position. |
| `input_of__client` | `Input` | Current input state for this client. |
| `client_flags__u16` | `Client_Flags__u16` | Lifecycle and status flags. |

### Client_Flags__u16

| Flag | Bit | Description |
|------|-----|-------------|
| `CLIENT_FLAGS__NONE` | 0 | No flags set. |
| `CLIENT_FLAG__IS_ACTIVE` | 0 | Client is actively connected and participating. |
| `CLIENT_FLAG__IS_LOADED` | 1 | Client data has been deserialized from disk. |
| `CLIENT_FLAG__IS_FAILED_TO_LOAD` | 2 | Client data failed to load. |
| `CLIENT_FLAG__IS_SAVING` | 3 | Client is currently being serialized. |
| `CLIENT_FLAG__IS_FRESH` | 4 | Client was freshly created (not loaded from disk). |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_client` | `(Client*, Identifier__u32 uuid, Global_Space_Vector__3i32) -> void` | Initializes a client with the given UUID and starting position. |

### Game Action Dispatch and Receive

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action_for__client` | `(Client*, Game*, TCP_Socket_Manager*, Game_Action*) -> bool` | `bool` | Logically handles an outbound allocated game action. Returns true on success. |
| `receive_game_action_for__client` | `(Client*, Game*, Game_Action*) -> bool` | `bool` | Logically handles an inbound allocated game action. Returns true on success. |
| `release_game_action_from__client` | `(Client*, Game_Action*) -> bool` | `bool` | Releases a game action back to the client's pool. |
| `allocate_game_action_from__client` | `(Client*, Game_Action_Flags) -> Game_Action*` | `Game_Action*` | Allocates a game action from the client's outbound manager. Returns null on failure. |

### Teleportation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `teleport_client` | `(Game*, Client*, Vector__3i32F4) -> Process*` | `Process*` | Initiates a teleport process for the client to the given position. Returns the process handle. |

### Entity Binding

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_entity_of__client` | `(Client*, Entity*) -> void` | Associates an entity with this client. |

### Serialization Processes

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__deserialize_client__default` | `(Process*, Game*) -> void` | Default process handler for deserializing a client from disk. |
| `m_process__serialize_client__default` | `(Process*, Game*) -> void` | Default process handler for serializing a client to disk. |

### Accessor Functions (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_game_action_manager__inbound_from__client` | `(Client*) -> Game_Action_Manager*` | `Game_Action_Manager*` | Returns the inbound game action manager. Null-safe. |
| `get_p_game_action_manager__outbound_from__client` | `(Client*) -> Game_Action_Manager*` | `Game_Action_Manager*` | Returns the outbound game action manager. Null-safe. |
| `get_p_local_space_manager_from__client` | `(Client*) -> Local_Space_Manager*` | `Local_Space_Manager*` | Returns the local space manager. Null-safe. |
| `get_p_input_of__client` | `(Client*) -> Input*` | `Input*` | Returns the input state. Debug builds return null on null client. |
| `copy_input_into__client` | `(Client*, Input*) -> void` | `void` | Copies input state into the client. Debug builds no-op on null. |

### Flag Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_client_as__inactive` | `(Client*) -> void` | `void` | Clears `IS_ACTIVE` flag. |
| `is_client__failed_to_load` | `(Client*) -> bool` | `bool` | Returns true if `IS_FAILED_TO_LOAD` is set. **Note**: also calls `set_client_as__inactive` as a side effect — see Known Issues. |
| `set_client_as__failed_to_load` | `(Client*) -> void` | `void` | Clears all flags, then sets `IS_FAILED_TO_LOAD`. |
| `set_client_as__NOT_failed_to_load` | `(Client*) -> void` | `void` | Clears `IS_FAILED_TO_LOAD` flag. |
| `is_client__loaded` | `(Client*) -> bool` | `bool` | Returns true if `IS_LOADED` is set. Null-safe. |
| `set_client_as__loaded` | `(Client*) -> void` | `void` | Clears failed-to-load, sets `IS_LOADED`. |
| `set_client_as__NOT_loaded` | `(Client*) -> void` | `void` | Clears `IS_LOADED` flag. |
| `is_client__active` | `(Client*) -> bool` | `bool` | Returns true if `IS_ACTIVE` is set. Null-safe. |
| `is_client__saving` | `(Client*) -> bool` | `bool` | Returns true if `IS_SAVING` is set. Null-safe. |
| `set_client_as__saving` | `(Client*) -> void` | `void` | Sets `IS_SAVING` flag. |
| `set_client_as__NOT_saving` | `(Client*) -> void` | `void` | Clears `IS_SAVING` flag. |
| `set_client_as__active` | `(Client*) -> void` | `void` | Clears failed-to-load, loaded, and saving flags, then sets `IS_ACTIVE`. |

## Agentic Workflow

### Client Lifecycle

    [Unallocated]
         |
    allocate_client_from__game (in game.h)
         |
    initialize_client
         |
    [Initialized, Inactive]
         |
    (load from disk or create fresh)
         |
    set_client_as__loaded / set_client_as__active
         |
    [Active]
         |
    (dispatch/receive game actions each frame)
    (teleport, input polling, etc.)
         |
    set_client_as__saving -> [Saving]
         |
    (serialization process completes)
         |
    set_client_as__NOT_saving
         |
    release_client_from__game
         |
    [Unallocated]

### Game Action Flow

**Outbound** (client -> server/network):

    allocate_game_action_from__client
         |
    (populate game action fields)
         |
    dispatch_game_action_for__client
         |
    (sent over TCP or processed locally)

**Inbound** (server/network -> client):

    (game action received from network)
         |
    receive_game_action_for__client
         |
    (processed by game action logic table)
         |
    release_game_action_from__client

### Known Issues

- `is_client__failed_to_load` has a side effect: it calls
  `set_client_as__inactive` before checking the flag. This means
  querying whether a client failed to load will also deactivate it.
  This is likely a bug.

### Preconditions

- All functions require a non-null `p_client` unless documented as
  null-safe.
- `dispatch_game_action_for__client`: `p_game_action` must have been
  allocated from the client's outbound manager.
- `teleport_client`: the game's process manager must have available
  process slots.

### Postconditions

- After `initialize_client`: all fields are initialized, flags are
  `CLIENT_FLAGS__NONE`.
- After `set_client_as__active`: `IS_ACTIVE` is set; `IS_FAILED_TO_LOAD`,
  `IS_LOADED`, and `IS_SAVING` are cleared.

### Error Handling

- Null-safe accessors (`get_p_game_action_manager__inbound_from__client`,
  etc.) return `0` on null input.
- Debug builds guard `get_p_input_of__client` and `copy_input_into__client`
  with null checks.
- `allocate_game_action_from__client` returns null if the outbound
  game action pool is exhausted.
