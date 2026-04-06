# 1. System Overview: World Game Actions (World and Client Loading)

## 1.1. Purpose

The world game actions manage the initialization of the game world and
the loading of client persistent data. Two actions cover these concerns:
loading the world for a specific client (initializing their local space
manager and beginning chunk loading), and loading a client's persistent
data from disk.

## 1.2. Architecture

### 1.2.1. Action Kinds

| Kind | Direction | Description |
|------|-----------|-------------|
| `Game_Action_Kind__World__Load_World` | Client → Server | Requests world initialization for a specific client. |
| `Game_Action_Kind__World__Load_Client` | Client → Server | Requests loading of a client's persistent data from disk. |

### 1.2.2. Payload Summary

| Kind | Key Fields |
|------|------------|
| `World__Load_World` | `Identifier__u32` client UUID. |
| `World__Load_Client` | `Identifier__u32` client UUID. |

## 1.3. World Loading Sequence

The world and client loading actions are typically dispatched in sequence
during the connection/startup phase:

    1. Client connects (or game starts in offline mode).
    2. dispatch_game_action__world__load_client(p_game, client_uuid)
       -> Loads client persistent data from disk.
    3. dispatch_game_action__world__load_world(p_game, client_uuid)
       -> Initializes local space manager.
       -> Begins chunk loading around client position.
    4. Chunk requests (Global_Space__Request) are dispatched.
    5. Chunks are loaded/resolved.
    6. Client can begin gameplay.

### 1.3.1. Sequence Diagram

    Client                              Server
      |                                   |
      |-- (connection accepted) --------->|
      |                                   |
      |-- World__Load_Client ------------>|
      |   (client_uuid)                   |
      |                                   |-- (loads from disk via
      |                                   |    PLATFORM_File_System_Context)
      |                                   |
      |                                   |-- (success: set_client_as__loaded)
      |                                   |-- (failure: set_client_as__failed_to_load
      |                                   |    -> create fresh client)
      |                                   |
      |-- World__Load_World ------------->|
      |   (client_uuid)                   |
      |                                   |-- (initializes local space manager)
      |                                   |-- (dispatches Global_Space__Requests
      |                                   |    for surrounding chunks)
      |                                   |
      |<-- Global_Space__Request/Resolve -|
      |   (chunk loading begins)          |
      |                                   |
      |   [Gameplay ready]                |

## 1.4. World__Load_Client Details

### 1.4.1. Process

1. The process handler invokes `dispatch_handler_process_to__load_client`.
2. Client persistent data is loaded from disk via the platform file system
   context (`PLATFORM_File_System_Context`).
3. On success, the client is marked as loaded (`set_client_as__loaded`).
4. On failure, the client is marked as failed (`set_client_as__failed_to_load`),
   and a fresh client may be created instead.

### 1.4.2. Registration

| Function | Mode |
|----------|------|
| `register_game_action__world__load_client` | All modes |

## 1.5. World__Load_World Details

### 1.5.1. Process

1. The process handler initializes the client's local space manager.
2. Chunk requests are dispatched for the area surrounding the client's
   position.
3. The world must already be allocated for the game
   (`is_world_allocated_for__game`).

### 1.5.2. Registration

| Function | Mode |
|----------|------|
| `register_game_action__world__load_world` | All modes |

## 1.6. Integration with Other Systems

### 1.6.1. Global Space Actions

`World__Load_World` triggers `Global_Space__Request` actions for chunks
around the client. These requests follow the chunk lifecycle described
in the global space system overview.

### 1.6.2. Client Management

Both actions operate on `Client` instances identified by UUID. The client
must be allocated before either action is dispatched.

### 1.6.3. Platform File System

`World__Load_Client` depends on the platform file system context
(`PLATFORM_File_System_Context`) for reading client data from disk.
The specific file format and I/O operations are handled by platform
implementations.

## 1.7. Preconditions and Postconditions

### 1.7.1. World__Load_Client

**Preconditions:**
- The client must be allocated.
- The game's file system context must be initialized.

**Postconditions:**
- The client's persistent data is loaded from disk.
- The client's flags reflect the load result (loaded or failed).

### 1.7.2. World__Load_World

**Preconditions:**
- The client must be allocated and active.
- The world must be allocated for the game.

**Postconditions:**
- The client's local space manager is initialized.
- Chunk loading begins for the client's surrounding area.

## 1.8. Error Handling

- If client data cannot be loaded from disk, the client is marked as
  failed and a fresh client may be created.
- If the world is not allocated, the process handler should fail via
  `fail_process`.
- If the `Process_Manager` is full, dispatch returns NULL.
