# System Overview: Core Engine Architecture

## Purpose

The core engine provides a platform-agnostic game framework built around
a central `Game` struct that owns or references every major subsystem.
The engine is designed for deterministic, fixed-point arithmetic on
constrained hardware (no floating-point dependency), with a pluggable
platform abstraction layer that allows backends to provide rendering,
audio, file I/O, input, and networking implementations.

## Architecture

### Top-Level Object Graph

    Game
    ├── Gfx_Context
    │   ├── Graphics_Window_Manager
    │   │   └── Graphics_Window[] ──→ PLATFORM_Graphics_Window
    │   ├── Aliased_Texture_Manager (+ Repeatable_Psuedo_Random)
    │   ├── UI_Context
    │   │   └── UI_Manager
    │   │       ├── UI_Element[] (pooled)
    │   │       └── Repeatable_Psuedo_Random
    │   ├── UI_Tile_Map_Manager
    │   ├── Font_Manager
    │   ├── Sprite_Context
    │   └── PLATFORM_Gfx_Context* ──→ (platform-specific)
    │
    ├── Hitbox_Context
    │   ├── Hitbox_Manager_Instance[] (opaque manager pool)
    │   ├── Hitbox_Manager_Instance__Invocation_Table[] (per type)
    │   └── Hitbox_Manager_Registration_Record[] (per type)
    │
    ├── World* (pM_world, heap-allocated)
    │   ├── Collision_Node_Pool
    │   │   ├── Collision_Node[] (chunk-aligned spatial buckets)
    │   │   └── Collision_Node_Entry[] (hitbox references)
    │   ├── Global_Space_Manager
    │   │   └── Global_Space[] ──→ Collision_Node
    │   ├── Entity_Manager (+ Repeatable_Psuedo_Random)
    │   ├── Inventory_Manager
    │   ├── Item_Manager
    │   ├── Chunk_Generator_Table
    │   └── Repeatable_Psuedo_Random (world generation)
    │
    ├── Process_Manager (+ Repeatable_Psuedo_Random)
    ├── Scene_Manager
    ├── Sort_List_Manager
    ├── Path_List_Manager
    │
    ├── Client[] (pM_clients, pooled)
    │   ├── Game_Action_Manager (inbound, + Repeatable_Psuedo_Random)
    │   ├── Game_Action_Manager (outbound, + Repeatable_Psuedo_Random)
    │   ├── Local_Space_Manager
    │   ├── Input
    │   └── Client_Flags__u16
    │
    ├── TCP_Socket_Manager* ──→ PLATFORM_TCP_Context
    ├── Session_Token
    ├── Game_Action_Logic_Table
    ├── Log (global, local, system)
    ├── Timer__u32 (tick, seconds, nanoseconds)
    ├── Input (fallback, used when no client pool)
    │
    ├── PLATFORM_Audio_Context* ──→ (platform-specific)
    └── PLATFORM_File_System_Context* ──→ (platform-specific)

### Key Subsystem Roles

| Subsystem | Owner | Role |
|-----------|-------|------|
| `Gfx_Context` | `Game` | All rendering state: windows, textures, sprites, UI, fonts. |
| `Hitbox_Context` | `Game` | Collision system: hitbox manager registration, allocation, and opaque access. |
| `World` | `Game` (heap) | World state: chunks, entities, inventories, items, spatial partitioning, collision nodes. |
| `Process_Manager` | `Game` | Cooperative process scheduler for async operations (loading, saving, teleporting). |
| `Scene_Manager` | `Game` | Scene lifecycle (enter/exit/update handlers). |
| `Client` pool | `Game` | Connected player state: input, game action queues, local space tracking. |
| `TCP_Socket_Manager` | `Game` (optional) | Multiplayer networking via platform TCP. |
| `PLATFORM_*` contexts | `Game` (pointers) | Platform-specific backends for graphics, audio, file I/O, networking. |

## Type System

### Fixed-Point Arithmetic

The engine avoids floating-point entirely. All spatial calculations use
fixed-point types:

| Type | Format | Primary Use |
|------|--------|-------------|
| `i32F4` | 28.4 signed | Positions, velocities, general spatial math. |
| `i32F8` | 24.8 signed | Higher-precision intermediates, acceleration. |
| `i32F20` | 12.20 signed | Ray casting, high-precision angles. |
| `u32F20` | 12.20 unsigned | Elapsed time. |
| `i16F4` | 12.4 signed | Compact positions. |
| `i16F8` | 8.8 signed | Compact acceleration (e.g. gravity). |

Conversions between formats use arithmetic shifts via macros
(`ARITHMETRIC_R_SHIFT`, `ARITHMETRIC_L_SHIFT`) that preserve sign
correctness for negative values.

### Vector Types

| Type | Components | Primary Use |
|------|------------|-------------|
| `Vector__3i32` | `x__i32, y__i32, z__i32` | Tile/chunk coordinates, integer positions. |
| `Vector__3i32F4` | `x__i32F4, y__i32F4, z__i32F4` | Entity positions, velocities. |
| `Vector__3i32F20` | `x__i32F20, y__i32F20, z__i32F20` | Ray casting, high-precision spatial math. |
| `Vector__3i16F8` | `x__i16F8, y__i16F8, z__i16F8` | Compact acceleration (gravity). |
| `Vector__3u8` | `x__u8, y__u8, z__u8` | Local tile coordinates within a chunk. |

Out-of-bounds sentinel vectors use `BIT(31)` for each component and are
checked via `is_vectors_3*__out_of_bounds`.

### Identifier and Pooling

Most engine objects use `Serialization_Header` for pool management:

    typedef struct Serialization_Header_t {
        Quantity__u32   size_of__struct;
        Identifier__u32 uuid;
    } Serialization_Header;

UUIDs are generated by per-subsystem `Repeatable_Psuedo_Random` instances,
ensuring deterministic allocation across subsystems:

| PRNG Instance | Location | Generates UUIDs For |
|---------------|----------|---------------------|
| `Entity_Manager.randomizer` | `World` | Entities |
| `World.repeatable_pseudo_random` | `World` | World generation seeds |
| `Game_Action_Manager.repeatable_pseudo_random` | `Client` (×2) | Game actions |
| `UI_Manager.randomizer` | `Gfx_Context` | UI elements |
| `Aliased_Texture_Manager.repeatable_psuedo_random_for__texture_uuid` | `Gfx_Context` | Textures |
| `Process_Manager.repeatable_psuedo_random_for__process_uuid` | `Game` | Processes |

### Angle System

Angles use `Degree__u9`, a 9-bit unsigned integer (0–511) representing
360° in 512 discrete steps (~0.703° resolution). Conversion between
angles and `Direction__u8` compass directions is provided by the degree
subsystem.

### Timer System

Three timer widths (`Timer__u8`, `Timer__u16`, `Timer__u32`) provide
countdown timers used for animation frames, UI notifications, process
scheduling, and game tick management. All timers count down from a
`start` value toward zero.

## Platform Abstraction

### Contract

`platform.h` declares all `PLATFORM_*` function signatures. Each backend
must implement every function. The engine never calls platform-specific
code directly — all platform interaction goes through this interface.

### Platform Contexts

| Context | Provided By | Used For |
|---------|-------------|----------|
| `PLATFORM_Gfx_Context` | Backend | Window management, texture/sprite allocation, rendering. |
| `PLATFORM_Audio_Context` | Backend | Audio effect playback, streaming. |
| `PLATFORM_File_System_Context` | Backend | File I/O, serialization request pooling. |
| `PLATFORM_TCP_Context` | Backend | TCP socket management for multiplayer. |

### Configuration

`platform_defaults.h` provides default compile-time constants (tile sizes,
chunk dimensions, entity limits, rendering dimensions, etc.). Backends
override specific values in their `platform_defines.h` before
`platform_defaults.h` is included. The `#ifndef` guard pattern ensures
backend values take precedence.

### Include Order

    platform_defines.h  → backend-specific PLATFORM_* struct definitions
         ↓
    platform_defaults.h → compile-time constants with #ifndef defaults
         ↓
    platform.h          → PLATFORM_* function declarations
         ↓
    defines_weak.h      → forward declarations for all engine types
         ↓
    defines.h           → full type definitions

## Game Lifecycle

### Initialization

    PLATFORM_initialize_game(p_game)
         │
    initialize_game(p_game)
         │  ├── initializes all owned subsystems
         │  ├── pM_world = NULL
         │  └── client pool not allocated
         │
    (optional) allocate_world_for__game(p_game)
         │
    (optional) allocate_client_pool_for__game(p_game, quantity)

### Main Loop

    run_game(p_game)
         │
         ├──→ manage_game__pre_render(p_game)
         │       ├── PLATFORM_poll_input
         │       ├── poll_multiplayer (if multiplayer)
         │       ├── process_manager polls
         │       └── scene enter handler
         │
         ├──→ PLATFORM_pre_render(p_game)
         │
         ├──→ (rendering via Gfx_Context / PLATFORM_* calls)
         │
         ├──→ PLATFORM_post_render(p_game)
         │
         ├──→ manage_game__post_render(p_game)
         │       ├── reset__game_tick_timer
         │       └── audio polling
         │
         └──→ (loop)

### Shutdown

    save_all__clients(p_game)
         │
    release_client_pool_from__game(p_game)
         │
    stop_multiplayer_for__game(p_game)  (if multiplayer)
         │
    PLATFORM_close_game(p_game)

## Client System

### Client Lifecycle

    [Unallocated]
         │
    allocate_client_from__game(p_game, uuid)
         │
    initialize_client(p_client, uuid, position)
         │
    [Initialized, Inactive]
         │
    (load from disk or create fresh)
         │
    set_client_as__active
         │
    [Active]
         │  ├── dispatch/receive game actions each frame
         │  ├── input polling via get_p_input_from__game
         │  └── teleport_client for position changes
         │
    set_client_as__saving → [Saving]
         │
    (serialization process completes)
         │
    release_client_from__game
         │
    [Unallocated]

### Game Action Flow

Each client has two `Game_Action_Manager` instances:

**Outbound** (client → server/network):

    allocate_game_action_from__client
         → populate fields
         → dispatch_game_action_for__client
         → (sent via TCP or processed locally)

**Inbound** (server/network → client):

    (received from network)
         → receive_game_action_for__client
         → (processed via game_action_logic_table)
         → release_game_action_from__client

### Input Routing

When `max_quantity_of__clients > 0`, input is routed through the local
client (`pM_ptr_array_of__clients[0]`). Otherwise, the fallback
`Game.input` is used. This is transparent via `get_p_input_from__game`.

## Multiplayer

    begin_multiplayer_for__game(p_game, poll_handler)
         │
    allocate_client_pool_for__game(p_game, quantity)
         │
    (main loop: poll_multiplayer each frame)
         │  ├── PLATFORM_tcp_poll_accept (server)
         │  ├── PLATFORM_tcp_recieve
         │  └── PLATFORM_tcp_send
         │
    save_all__clients
         │
    release_client_pool_from__game
         │
    stop_multiplayer_for__game

TCP operations are fully delegated to the platform via `PLATFORM_tcp_*`
functions. The engine manages socket state through `TCP_Socket_Manager`
and dispatches game actions through the client system.

## Collision System

The collision system spans two owners:

- **`Hitbox_Context`** (owned by `Game`): Manages hitbox type
  registration, hitbox manager allocation, and opaque hitbox access.
  Supports multiple hitbox manager types (AABB, etc.) via an invocation
  table pattern.

- **`Collision_Node_Pool`** (owned by `World`): Provides chunk-aligned
  spatial partitioning. Each loaded chunk's `Global_Space` references a
  `Collision_Node` containing a linked list of `Collision_Node_Entry`
  records that reference hitboxes by UUID.

See `docs/specs/collisions/system_overview__collision_node.md` and
`docs/specs/collisions/system_overview__collision.md` for detailed
collision system documentation.

## Audio System

Audio is managed through the platform abstraction:

- `PLATFORM_Audio_Context` holds platform-specific audio state.
- `Audio_Effect` structs represent individual sound effects, each with
  a timer, effect kind, flags, and platform instance handle.
- `PLATFORM_allocate_audio_effect` / `PLATFORM_play_audio_effect` /
  `PLATFORM_poll_audio_effects` manage the effect lifecycle.
- `PLATFORM_play_audio__stream` / `PLATFORM_is_audio__streaming`
  handle streaming audio.
- The convenience function `play_audio_effect_and__forget` allocates,
  configures, and plays an effect in one call.

## Serialization

### File System

All file I/O goes through `PLATFORM_*` functions:

- `PLATFORM_open_file` / `PLATFORM_close_file`
- `PLATFORM_read_file` / `PLATFORM_write_file`
- `PLATFORM_allocate_serialization_request` / `PLATFORM_release_serialization_request`

`Serialization_Request` is the engine's file handle abstraction, pooled
by `PLATFORM_File_System_Context`. Each request carries a data pointer,
a serialization header, and a platform file handler.

### Path Construction

File paths use the fixed-size `IO_path` type (`char[MAX_LENGTH_OF__IO_PATH]`).
Paths are built incrementally using `strncpy_returns__strlen` which
returns the copied length for index tracking:

    IO_path path;
    Index__u32 index = 0;
    index += strncpy_returns__strlen(path + index, "/saves/", max - index);
    index += strncpy_returns__strlen(path + index, world_name, max - index);

### Client Serialization

Client save/load is process-driven:

    dispatch_handler_process_to__load_client(p_game, path, uuid)
         → spawns Process with m_process__deserialize_client handler
         → process reads file via PLATFORM_* calls
         → set_client_as__loaded on completion

    dispatch_handler_process_to__save_client(p_game, path, p_client)
         → set_client_as__saving
         → spawns Process with m_process__serialize_client handler
         → process writes file via PLATFORM_* calls
         → set_client_as__NOT_saving on completion

## Utility Systems

### Numeric Utilities (numerics.h)

- Fixed-point conversion functions between all `i32F*` formats.
- Safe arithmetic: clamped add/subtract/multiply, no-overflow variants.
  Each clamped function uses the correct width-specific maximum for
  overflow detection (`MAX__U8` for u8, `MAX__U16` for u16, `MAX__U32`
  for u32).
- Right-shift clamped functions check against the correct bit width
  (`>= 8` for u8, `>= 16` for u16, `>= 32` for u32).
- Min/max, clamping, modular arithmetic.
- Fixed-point multiplication and division.
- Linear interpolation (1D and 2D bilinear) in F4 and F8.

### Vector Utilities (vectors.h)

- Construction, comparison, arithmetic for all vector types.
- Conversion chain: `Vector__3i32F20` ↔ `Vector__3i32F4` ↔ `Vector__3i32` ↔ `Vector__3u8`.
- Distance calculations (squared, Manhattan, Hamming).
- Direction-based offset operations.

### Angle Utilities (degree.h)

- Angle computation between vectors.
- Angle ↔ direction conversion.
- Angle arithmetic with circular wrapping.
- Offset vector generation from angles (F4 for short range, F20 for ray casting).

### Random Number Generation (random.h)

- Deterministic PRNG via `Repeatable_Psuedo_Random`.
- Intrusive queries (advance state) for sequential generation.
- Non-intrusive queries (preserve state) for position-based lookups.
- Each subsystem maintains its own PRNG instance for isolation.

### String Utilities

- `strncpy_returns__strlen` (core_string.h): bounded copy with length
  return for path building.
- `cstr_to_i32__limit_n` / `cstr_to_u32__limit_n` (lav_string.h): safe
  string-to-integer parsing with length limits.
- Narrowing wrappers (`cstr_to_i16__limit_n`, `cstr_to_i8__limit_n`,
  `cstr_to_u16__limit_n`, `cstr_to_u8__limit_n`) cast the return value
  to the target width, convert to bool, and only write the output on
  success.

### Memory Alignment (align.h)

- `ALIGN(alignment, type, name)`: stack-allocates an aligned buffer for
  platform operations requiring specific byte alignment (e.g. DMA).

## Spatial Utilities

### Entity-Tile Queries (game_util.h)

Composes entity, world, and tile subsystems:

    Entity facing direction
         → get_vector_3i32F4_thats__infront_of_this__entity (entity_util.h)
         → vector_3i32F4_to__tile_vector (tile_vectors.h)
         → get_p_tile_from__chunk_manager_with__tile_vector_3i32 (chunk_manager.h)

This enables queries like "what tile is in front of this entity?" for
interaction, pathfinding, and AI systems.

## Known Issues

- `Client.is_client__failed_to_load` has a side effect: it calls
  `set_client_as__inactive` before checking the flag, meaning querying
  failure status also deactivates the client.
- `multiply__i32F4` overflows silently if inputs exceed `BIT(12)` magnitude.
- `lav_string.h` narrowing wrappers do not check for overflow when
  narrowing from 32-bit to smaller types — values are silently truncated.

## Extension Points

### Platform-Overridable Types

Types can be overridden by backends via `types/implemented/*.h` headers
using the pattern:

    #include <types/implemented/entity_kind.h>
    #ifndef DEFINE_ENTITY_KIND
    typedef enum Entity_Kind { ... } Entity_Kind;
    #endif

Overridable types include: `Entity_Data`, `Entity_Functions`,
`Entity_Kind`, `Tile`, `Tile_Kind`, `Item_Data`, `Item_Kind`,
`UI_Element_Data`, `UI_Element_Kind`, `Scene_Kind`,
`Graphics_Window_Kind`, `Sprite_Kind`, `Sprite_Animation_Kind`,
`Audio_Effect_Kind`, `Audio_Stream_Kind`, `Chunk_Generator_Kind`,
`Hitbox_Manager_Type`, and others.

### Compile-Time Configuration

All engine limits are configurable via `platform_defaults.h` constants,
overridable by backends:

| Category | Key Constants |
|----------|---------------|
| Entities | `MAX_QUANTITY_OF__ENTITIES` |
| Rendering | `MAX_QUANTITY_OF__TEXTURES`, `GFX_CONTEXT__RENDERING_*__IN_CHUNKS` |
| Tiles/Chunks | `CHUNK__WIDTH`, `CHUNK__DEPTH`, `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` |
| Networking | `MAX_QUANTITY_OF__TCP_SOCKETS`, `MAX_SIZE_OF__TCP_PACKET` |
| Clients | `MAX_QUANTITY_OF__CLIENTS` |
| Sprites | `MAX_QUANTITY_OF__SPRITES`, `MAX_QUANTITY_OF__SPRITE_MANAGERS` |
| UI | `UI_TILE_MAP__*__MAX_QUANTITY_OF`, `UI_TILE_MAP__*__WIDTH/HEIGHT` |
