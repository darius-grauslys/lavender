# Specification: core/include/game.h

## Overview

Provides initialization, main loop management, client management,
multiplayer control, and accessor functions for the `Game` struct — the
top-level container for all engine state. The `Game` struct owns or
references every major subsystem: world, processes, sorting, rendering,
audio, file system, networking, input, scenes, and clients.

This is the primary entry point for engine lifecycle management.

## Dependencies

- `defines.h` (for `Game` and all subsystem types)
- `defines_weak.h` (forward declarations)
- `client.h`, `log/log.h`, `log/message.h`
- `multiplayer/session_token.h`, `multiplayer/tcp_socket_manager.h`
- `platform.h`, `random.h`, `timer.h`
- `world/world.h`

## Types

### Game (struct)

The `Game` struct is the root of the engine's object graph. Key fields:

| Field | Type | Description |
|-------|------|-------------|
| `input` | `Input` | Fallback input state (used when no client pool). |
| `scene_manager` | `Scene_Manager` | Active scene management. |
| `hitbox_context` | `Hitbox_Context` | Collision system state. |
| `pM_world` | `World*` | Pointer to the active world (null if not loaded). |
| `process_manager` | `Process_Manager` | Cooperative process scheduler. |
| `sort_list_manager` | `Sort_List_Manager` | Sort list pool. |
| `path_list_manager` | `Path_List_Manager` | Pathfinding state. |
| `log__global/local/system` | `Log` | Three log channels. |
| `gfx_context` | `Gfx_Context` | Graphics context (textures, sprites, UI, fonts). |
| `p_PLATFORM_audio_context` | `PLATFORM_Audio_Context*` | Platform audio state. |
| `p_PLATFORM_file_system_context` | `PLATFORM_File_System_Context*` | Platform file system state. |
| `game_action_logic_table` | `Game_Action_Logic_Table` | Dispatch table for game action processing. |
| `session_token` | `Session_Token` | Current player session. |
| `tick__timer_u32` | `Timer__u32` | Game tick timer. |
| `time__seconds__u32` / `time__nanoseconds__u32` | `Timer__u32` | Wall clock timers. |
| `max_quantity_of__clients` | `Quantity__u32` | Client pool capacity (0 = single-player without pool). |
| `pM_clients` | `Client*` | Client pool array. |
| `pM_ptr_array_of__clients` | `Client**` | Sorted pointer array into client pool. |
| `pM_tcp_socket_manager` | `TCP_Socket_Manager*` | Networking state (null if not multiplayer). |
| `m_game_action_handler__dispatch/receive/resolve` | `m_Game_Action_Handler` | Pluggable game action handlers. |
| `m_process__serialize/deserialize/create_client` | `m_Process` | Pluggable client lifecycle process handlers. |
| `game_flags__u32` | `Game_Flags__u32` | Global game flags. |

### Game_Flags__u32

| Flag | Bit | Description |
|------|-----|-------------|
| `GAME_FLAG__IS_SERVER_OR__CLIENT` | 0 | If set, this game instance is a server; otherwise client. |

## Functions

### Initialization and Main Loop

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game` | `(Game*) -> void` | Initializes all game subsystems. |
| `run_game` | `(Game*) -> int` | Main game loop entry point. Returns exit code. |
| `manage_game` | `(Game*) -> void` | Single frame management (pre + post render). |
| `manage_game__pre_render` | `(Game*) -> void` | Pre-render frame management (input, processes, logic). |
| `manage_game__post_render` | `(Game*) -> void` | Post-render frame management (cleanup, tick reset). |

### Time Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_elapsed_time__u32F20_of__game` | `(Game*) -> u32F20` | `u32F20` | Returns elapsed time since last poll. |
| `poll__game_tick_timer` | `(Game*) -> Quantity__u32` | `Quantity__u32` | Returns elapsed game ticks since last reset. |
| `reset__game_tick_timer` | `(Game*) -> void` | `void` | Resets the tick timer. Called after `manage_game__post_render`. |

### Multiplayer

| Function | Signature | Description |
|----------|-----------|-------------|
| `begin_multiplayer_for__game` | `(Game*, m_Poll_TCP_Socket_Manager) -> void` | Initializes TCP networking with the given poll handler. |
| `stop_multiplayer_for__game` | `(Game*) -> void` | Shuts down TCP networking. |
| `poll_multiplayer` | `(Game*) -> void` | Polls all TCP sockets for incoming data. |

### Client Pool Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_client_pool_for__game` | `(Game*, Quantity__u32) -> bool` | `bool` | Allocates a client pool of the given size. |
| `allocate_client_from__game` | `(Game*, Identifier__u32 uuid) -> Client*` | `Client*` | Allocates a client with the given UUID. |
| `release_client_from__game` | `(Game*, Client*) -> void` | `void` | Releases a client back to the pool. |
| `release_client_pool_from__game` | `(Game*) -> bool` | `bool` | Releases the entire client pool. Returns false if clients are still active. |
| `get_p_client_by__uuid_from__game` | `(Game*, Identifier__u32) -> Client*` | `Client*` | Looks up a client by UUID. |

### Client Lifecycle Processes

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_handler_process_to__create_client` | `(Game*, Identifier__u32) -> Process*` | `Process*` | Spawns a process to create a new client. |
| `dispatch_handler_process_to__load_client` | `(Game*, IO_path, Identifier__u32) -> Process*` | `Process*` | Spawns a process to load a client from disk. |
| `dispatch_handler_process_to__save_client` | `(Game*, IO_path, Client*) -> Process*` | `Process*` | Spawns a process to save a client to disk. |
| `load_client` | `(Game*, Identifier__u32) -> Process*` | `Process*` | High-level client load. |
| `save_client` | `(Game*, Client*) -> Process*` | `Process*` | High-level client save. |
| `save_all__clients` | `(Game*) -> void` | `void` | Saves all active clients. |

### World Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `allocate_world_for__game` | `(Game*) -> void` | Allocates and initializes the world. |

### Local Space

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_local_space_manager_thats__closest_to__this_position` | `(Game*, Vector__3i32) -> Local_Space_Manager*` | `Local_Space_Manager*` | Returns the local space manager closest to the given position. |

### Accessor Functions (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `get_p_world_from__game` | `World*` | Returns `pM_world`. |
| `get_p_hitbox_context_from__game` | `Hitbox_Context*` | Returns hitbox context. |
| `get_p_global_space_manager_from__game` | `Global_Space_Manager*` | Via world. |
| `get_p_aliased_texture_manager_from__game` | `Aliased_Texture_Manager*` | Via gfx context. |
| `get_p_process_manager_from__game` | `Process_Manager*` | Returns process manager. |
| `get_p_sort_list_manager_from__game` | `Sort_List_Manager*` | Returns sort list manager. |
| `get_p_path_list_manager_from__game` | `Path_List_Manager*` | Returns path list manager. |
| `get_p_inventory_manager_from__game` | `Inventory_Manager*` | Via world. |
| `get_p_item_manager_from__game` | `Item_Manager*` | Via world. |
| `get_p_scene_manager_from__game` | `Scene_Manager*` | Returns scene manager. |
| `get_p_entity_manager_from__game` | `Entity_Manager*` | Via world. |
| `get_p_chunk_generation_table_from__game` | `Chunk_Generator_Table*` | Via world. |
| `get_p_PLATFORM_file_system_context_from__game` | `PLATFORM_File_System_Context*` | Returns platform file system. |
| `get_p_PLATFORM_audio_context_from__game` | `PLATFORM_Audio_Context*` | Returns platform audio. |
| `get_p_gfx_context_from__game` | `Gfx_Context*` | Returns gfx context. |
| `get_p_PLATFORM_gfx_context_from__game` | `PLATFORM_Gfx_Context*` | Via gfx context. |
| `get_p_tcp_socket_manager_from__game` | `TCP_Socket_Manager*` | Returns TCP socket manager. |
| `get_p_PLATFORM_tcp_context_from__game` | `PLATFORM_TCP_Context*` | Via TCP socket manager. Null-safe. |
| `get_p_game_action_logic_table_from__game` | `Game_Action_Logic_Table*` | Returns game action logic table. |
| `get_p_input_from__game` | `Input*` | Returns local client input or fallback input. |
| `get_p_local_client_by__from__game` | `Client*` | Returns first client in ptr array (local player). |
| `get_p_client_by__index_from__game` | `Client*` | Returns client at index. Debug bounds-checked. |

### Game Action Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action` | `(Game*, Identifier__u32 client_uuid, Game_Action*) -> bool` | `bool` | Dispatches a game action to a specific client. |
| `dispatch_game_action_to__server` | `(Game*, Game_Action*) -> bool` | `bool` | Dispatches a game action to the local client (server-bound). |
| `receive_game_action` | `(Game*, Identifier__u32, Game_Action*) -> bool` | `bool` | Receives a game action for a specific client. |
| `resolve_game_action` | `(Game*, Identifier__u32, Game_Action*) -> bool` | `bool` | Resolves a game action for a specific client. |

### Logging

| Function | Returns | Description |
|----------|---------|-------------|
| `get_p_log__global_from__game` | `Log*` | Returns global log. (static inline) |
| `get_p_log__local_from__game` | `Log*` | Returns local log. (static inline) |
| `get_p_log__system_from__game` | `Log*` | Returns system log. (static inline) |
| `clear_log__global` | `void` | Clears global log (core + platform). (static inline) |
| `clear_log__local` | `void` | Clears local log (core + platform). (static inline) |
| `clear_log__system` | `void` | Clears system log (core + platform). (static inline) |
| `print_log__global` | `bool` | Prints to global log. |
| `print_log__local` | `bool` | Prints to local log. |
| `print_log__system` | `bool` | Prints to system log. |

### Queries (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `get_ticks_elapsed__game` | `Quantity__u32` | Ticks elapsed (obsolete, inaccurate). |
| `get_elapsed_time__u32F20_of__game` | `u32F20` | Cached elapsed time. |
| `get_elapsed_ticks__u32F20_of__game` | `u32F20` | Tick accumulator shifted. |
| `is_world_allocated_for__game` | `bool` | True if `pM_world` is non-null. |
| `is_game__multiplayer` | `bool` | True if TCP socket manager is non-null. |
| `is_game__server_or__client` | `bool` | True if server flag is set. |
| `get_max_quantity_of__clients_for__game` | `Quantity__u32` | Max client pool size. |
| `get_quantity_of__clients_connect_to__game` | `Quantity__u32` | Current connected client count. |
| `get_session_token_from__game` | `Session_Token` | Current session token. |
| `get_raw_uuid_u32_of__player_from__game_session_token` | `Identifier__u32` | Local player UUID from session. |

### Handler Setters (static inline)

| Function | Description |
|----------|-------------|
| `set_dispatch_handler_process_for__create_client` | Sets `m_process__create_client`. |
| `set_dispatch_handler_process_for__load_client` | Sets `m_process__deserialize_client`. |
| `set_dispatch_handler_process_for__save_client` | Sets `m_process__serialize_client`. |

## Agentic Workflow

### Game Lifecycle

    PLATFORM_initialize_game(p_game)
         |
    initialize_game(p_game)
         |
    run_game(p_game)
         |
    ┌─── manage_game__pre_render ───┐
    │    PLATFORM_poll_input         │
    │    poll_multiplayer (if MP)    │
    │    process_manager polls       │
    │    scene enter handler         │
    └───────────────────────────────┘
         |
    PLATFORM_pre_render
         |
    (rendering)
         |
    PLATFORM_post_render
         |
    ┌─── manage_game__post_render ──┐
    │    reset__game_tick_timer      │
    │    audio polling               │
    └───────────────────────────────┘
         |
    (loop back to pre_render)
         |
    PLATFORM_close_game(p_game)

### Input Routing

If `max_quantity_of__clients > 0`, input is routed through the local
client (`pM_ptr_array_of__clients[0]`). Otherwise, the fallback
`p_game->input` is used. This is handled transparently by
`get_p_input_from__game`.

### Multiplayer Flow

    begin_multiplayer_for__game(p_game, poll_handler)
         |
    allocate_client_pool_for__game(p_game, quantity)
         |
    (game loop: poll_multiplayer each frame)
         |
    save_all__clients(p_game)
         |
    release_client_pool_from__game(p_game)
         |
    stop_multiplayer_for__game(p_game)

### Preconditions

- `initialize_game` must be called before any other game functions.
- `allocate_world_for__game` must be called before accessing world
  subsystems.
- `allocate_client_pool_for__game` must be called before allocating
  individual clients.
- `release_client_pool_from__game` requires all clients to be inactive.

### Postconditions

- After `initialize_game`: all subsystems are initialized, `pM_world`
  is null, client pool is not allocated.
- After `allocate_world_for__game`: `pM_world` is non-null and
  initialized.

### Error Handling

- `get_p_client_by__index_from__game`: debug builds check for null
  client pool (`debug_warning` + `debug_abort`) and out-of-bounds index
  (`debug_error`).
- `get_p_PLATFORM_tcp_context_from__game`: returns null if TCP socket
  manager is not allocated.
- `release_client_pool_from__game`: returns false if clients are still
  active, preventing premature deallocation.
