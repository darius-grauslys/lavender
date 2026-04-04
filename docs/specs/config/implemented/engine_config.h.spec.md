# Specification: core/include/config/implemented/engine_config.h

## Overview

Template header that allows game projects to override engine compile-time
configuration constants before `platform_defaults.h` applies its fallback
values. This file is the **first** include in `platform_defaults.h` and
serves as the primary mechanism for tuning engine parameters (pool sizes,
dimensions, input codes, network settings, etc.) without modifying core
engine files.

All overrides are commented out by default. Uncommenting a `#define` in
this file will prevent `platform_defaults.h` from applying its default
value for that constant, because `platform_defaults.h` wraps every default
in `#ifndef`.

This file is a **template** — it is copied to the game project directory
by `tools/lav_new_project` and is meant to be modified by the engine user.

## Template Behavior

This file resides in `core/include/config/implemented/` and is copied to
the game project's corresponding `config/implemented/` directory by the
`lav_new_project` script. The game developer uncomments and modifies the
values they wish to override. The original in core serves as the
default/template where everything is commented out.

The `implemented/` directory is NOT in the core include path — it is only
in the game project's include path. The game project's copy takes
precedence because the game's include path is searched before core's.

## Dependencies

- `platform_defines.h` (included first, provides platform-specific overrides
  from the backend such as NDS, SDL, or no_gui)

## Include Chain

    platform_defaults.h
        └── config/implemented/engine_config.h  (this file, game copy)
                └── platform_defines.h          (backend-specific)

`platform_defaults.h` includes this file first, then applies `#ifndef`
guarded defaults for every constant. If this file (or `platform_defines.h`)
has already defined a constant, the default is skipped.

## Configurable Constants

All constants below are commented out in the template. Uncomment to override.

### Filesystem

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_LENGTH_OF__IO_PATH` | `128` | Maximum length of filesystem paths. |
| `PATH_SEPERATOR` | `'/'` | Path separator character. |

### Process System

| Macro | Default | Description |
|-------|---------|-------------|
| `PROCESS_MAX_QUANTITY_OF` | `512` | Maximum number of concurrent processes. |

### Game Actions

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__GAME_ACTIONS` | `512` | Maximum number of game actions in the pool. |

### Networking / TCP

| Macro | Default | Constraints | Description |
|-------|---------|-------------|-------------|
| `MAX_QUANTITY_OF__TCP_SOCKETS` | `1` | — | Maximum concurrent TCP sockets. |
| `MAX_SIZE_OF__TCP_PACKET` | `BIT(9)` | **MUST** be `BIT(n)` | Maximum TCP packet size in bytes. Non-power-of-2 values will break `MASK(n)` logic in `game_action__tcp_delivery`. |
| `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` | `BIT(8)` | **MUST** be power of 2 | Maximum queued packets per socket. |
| `TCP_ERROR__DESTINATION_OVERFLOW` | `-1` | — | Error code: destination buffer overflow. |
| `TCP_ERROR__QUEUE_FULL` | `-2` | — | Error code: socket queue full. |

### Camera

| Macro | Default | Description |
|-------|---------|-------------|
| `CAMERA_FULCRUM__WIDTH` | `256` | Default camera viewport width in pixels. |
| `CAMERA_FULCRUM__HEIGHT` | `196` | Default camera viewport height in pixels. |

### Textures

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__TEXTURES` | `128` | Maximum textures in the texture pool. |

### Rendering Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS` | `4` | Visible width in chunks. |
| `GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS` | `3` | Visible height in chunks. |
| `GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS` | `1` | Visible depth in chunk layers. |

### Tile Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(tile size in pixels) = 8px. |
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)` | Tile size in pixels. Derived from bit shift. |

### Chunk Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(tiles per chunk edge) = 8 tiles. |
| `CHUNK__DEPTH__BIT_SHIFT` | `1` | log2(chunk depth) = 2 layers. |
| `CHUNK__WIDTH` | `BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)` | Tiles per chunk (X). |
| `CHUNK__HEIGHT` | `BIT(CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT)` | Tiles per chunk (Y). |
| `CHUNK__DEPTH` | `BIT(CHUNK__DEPTH__BIT_SHIFT)` | Tile layers (Z). |
| `CHUNK__QUANTITY_OF__TILES` | `CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH` | Total tiles per chunk. |

### Local Space

| Macro | Default | Description |
|-------|---------|-------------|
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` | `3` | log2(tiles per local space edge). |
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT` | `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` | log2(pixels per local space edge). Derived. |

### Local Space Manager

| Macro | Default | Constraints | Description |
|-------|---------|-------------|-------------|
| `LOCAL_SPACE_MANAGER__WIDTH` | `8` | Must be >= `GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS` | Grid width in chunks. |
| `LOCAL_SPACE_MANAGER__HEIGHT` | `8` | Must be >= `GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS` | Grid height in chunks. |
| `LOCAL_SPACE_MANAGER__DEPTH` | `1` | Must be >= `GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS` | Grid depth in chunk layers. |
| `VOLUME_OF__LOCAL_SPACE_MANAGER` | `WIDTH * HEIGHT * DEPTH` | Derived | Total local spaces. |

### Multiplayer

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__CLIENTS` | `4` | Maximum concurrent clients. |
| `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS` | Total global spaces in pool. Derived. |

### Entities

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__ENTITIES` | `128` | Maximum entities in the entity pool. |

### Sprites

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__SPRITES` | `256` | Maximum sprites in the sprite pool. |

### Input

| Macro | Default | Description |
|-------|---------|-------------|
| `QUANTITY_OF__INPUTS` | `14` | Number of input codes. |
| `INPUT_CODE_*` | Sequential from 0 | Input code constants (FORWARD, LEFT, RIGHT, etc.). |
| `INPUT_*` | Bit flags from `BIT(0)` | Input flag constants for bitfield operations. |

### UI Tile Maps

| Macro | Default | Description |
|-------|---------|-------------|
| `UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(UI tile size in pixels) = 8px. |
| `UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `BIT(UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)` | UI tile size in pixels. Derived. |
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` | `32` | Max small tile maps. |
| `UI_TILE_MAP__SMALL__WIDTH` | `8` | Small tile map width. |
| `UI_TILE_MAP__SMALL__HEIGHT` | `8` | Small tile map height. |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | `16` | Max medium tile maps. |
| `UI_TILE_MAP__MEDIUM__WIDTH` | `16` | Medium tile map width. |
| `UI_TILE_MAP__MEDIUM__HEIGHT` | `16` | Medium tile map height. |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `8` | Max large tile maps. |
| `UI_TILE_MAP__LARGE__WIDTH` | `32` | Large tile map width. |
| `UI_TILE_MAP__LARGE__HEIGHT` | `32` | Large tile map height. |

### Graphics Windows

| Macro | Default | Description |
|-------|---------|-------------|
| `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` | `1` | Maximum platform-provided graphics windows. |

## Agentic Workflow

### Override Pattern

To override a constant, uncomment the `#define` line and set the desired
value:

    // Before (default):
    //#define MAX_QUANTITY_OF__ENTITIES 128

    // After (override):
    #define MAX_QUANTITY_OF__ENTITIES 256

### Override Precedence

The override chain is (highest priority first):

1. `platform_defines.h` (backend-specific, e.g. NDS memory constraints)
2. `config/implemented/engine_config.h` (this file, game-specific)
3. `platform_defaults.h` (engine defaults, lowest priority)

If `platform_defines.h` defines a constant, neither this file nor
`platform_defaults.h` can override it (unless the platform uses `#ifndef`
guards too).

### Compile-Time Validation

`platform_defaults.h` enforces the following constraints at compile time:

- `LOCAL_SPACE_MANAGER__WIDTH >= GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS`
- `LOCAL_SPACE_MANAGER__HEIGHT >= GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS`
- `LOCAL_SPACE_MANAGER__DEPTH >= GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS`

Violating these produces `#error` at compile time.

### Derived Constants

Several constants are derived from others. If you override a base constant,
the derived constants will automatically update unless you also override
them explicitly:

- `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` ← `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`
- `CHUNK__WIDTH` ← `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`
- `CHUNK__QUANTITY_OF__TILES` ← `CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH`
- `VOLUME_OF__LOCAL_SPACE_MANAGER` ← `WIDTH * HEIGHT * DEPTH`
- `QUANTITY_OF__GLOBAL_SPACE` ← `VOLUME_OF__LOCAL_SPACE_MANAGER * MAX_QUANTITY_OF__CLIENTS`

### TCP Packet Size Constraint

**CRITICAL:** `MAX_SIZE_OF__TCP_PACKET` **MUST** be expressed as `BIT(n)`.
Non-power-of-2 values will cause `game_action__tcp_delivery` to fail
silently due to broken `MASK(n)` logic. All TCP-dependent systems
(global space delivery, inventory sync, entity sync) will be unreliable.

### Memory Impact

Many of these constants directly control pool sizes that are allocated
statically or at initialization. Increasing pool sizes increases memory
usage proportionally. On memory-constrained platforms (e.g. Nintendo DS),
be conservative with:

- `MAX_QUANTITY_OF__ENTITIES` (each entity contains `Entity_Data`)
- `QUANTITY_OF__GLOBAL_SPACE` (each contains a full `Chunk`)
- `MAX_QUANTITY_OF__GAME_ACTIONS` (each is a large union)
- `UI_TILE_MAP__*__MAX_QUANTITY_OF` (tile map backing storage)

### Preconditions

- This file must be included before `platform_defaults.h` applies its
  defaults (this is guaranteed by the include chain).
- `platform_defines.h` must exist and define `PLATFORM_DEFINES_H`.

## Header Guard

`ENGINE_CONFIG_H`
