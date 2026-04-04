# Specification: core/include/platform_defaults.h

## Overview

Provides default values for all compile-time configuration constants used
by the engine. Each constant is guarded by `#ifndef`, allowing backends
to override any value by defining it in their `platform_defines.h` or
build system before this file is included.

This file is the central configuration registry for the engine's
compile-time parameters.

## Dependencies

- `config/implemented/engine_config.h` (for project-level overrides)
- `platform_defines.h` (backend-specific overrides)

## Configuration Constants

### File System

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_LENGTH_OF__IO_PATH` | 128 | Maximum length of a file path in characters. |
| `PATH_SEPERATOR` | `'/'` | Path separator character. |

### Networking

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_QUANTITY_OF__TCP_SOCKETS` | 1 | Maximum number of TCP sockets. |
| `MAX_SIZE_OF__TCP_PACKET` | `BIT(9)` (512) | Maximum TCP packet size. **Must** be a power of 2. |
| `MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET` | `BIT(8)` (256) | Maximum queued packets per socket. **Must** be a power of 2. |
| `TCP_ERROR__DESTINATION_OVERFLOW` | -1 | Error code for destination buffer overflow. |
| `TCP_ERROR__QUEUE_FULL` | -2 | Error code for full socket queue. |

### Camera

| Constant | Default | Description |
|----------|---------|-------------|
| `CAMERA_FULCRUM__WIDTH` | 256 | Camera view width in pixels. |
| `CAMERA_FULCRUM__HEIGHT` | 196 | Camera view height in pixels. |

### Rendering

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_QUANTITY_OF__TEXTURES` | 128 | Maximum number of textures. |
| `GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS` | 4 | Rendering width in chunks. |
| `GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS` | 3 | Rendering height in chunks. |
| `GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS` | 1 | Rendering depth in chunks. |
| `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` | 1 | Maximum platform graphics windows. |

### Tiles and Chunks

| Constant | Default | Description |
|----------|---------|-------------|
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | 3 | Tile size = `BIT(3)` = 8 pixels. |
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | 8 | Tile size in pixels. |
| `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` | 3 | Chunk width/height = `BIT(3)` = 8 tiles. |
| `CHUNK__DEPTH__BIT_SHIFT` | 1 | Chunk depth = `BIT(1)` = 2 layers. |
| `CHUNK__WIDTH` | 8 | Chunk width in tiles. |
| `CHUNK__DEPTH` | 2 | Chunk depth in layers. |
| `CHUNK__QUANTITY_OF__TILES` | `WIDTH * HEIGHT * DEPTH` | Total tiles per chunk. |

### Local Space

| Constant | Default | Description |
|----------|---------|-------------|
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` | 3 | Local space tile size shift. |
| `LOCAL_SPACE_MANAGER__WIDTH` | 8 | Local space manager width in chunks. |
| `LOCAL_SPACE_MANAGER__HEIGHT` | 8 | Local space manager height in chunks. |
| `LOCAL_SPACE_MANAGER__DEPTH` | 1 | Local space manager depth in chunks. |
| `VOLUME_OF__LOCAL_SPACE_MANAGER` | `W * H * D` | Total local spaces. |

### Clients and Entities

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_QUANTITY_OF__CLIENTS` | 4 | Maximum number of clients. |
| `QUANTITY_OF__GLOBAL_SPACE` | `VOLUME * CLIENTS` | Total global spaces. |
| `MAX_QUANTITY_OF__ENTITIES` | 128 | Maximum number of entities. |

### Sprites

| Constant | Default | Description |
|----------|---------|-------------|
| `MAX_QUANTITY_OF__SPRITES` | 256 | Maximum number of sprites. |
| `MAX_QUANTITY_OF__SPRITE_MANAGERS` | 4 | Maximum number of sprite managers. |

### Input

| Constant | Default | Description |
|----------|---------|-------------|
| `QUANTITY_OF__INPUTS` | 14 | Number of input codes. |
| `MAX_QUANTITY_OF__SYMBOLS_IN__INPUT_WRITING_BUFFER` | 8 | Writing buffer size. |

Input codes (`INPUT_CODE_*`) and input flags (`INPUT_*`) are defined
here unless `PLATFORM_INPUT` is defined by the backend.

### UI Tile Maps

| Constant | Default | Description |
|----------|---------|-------------|
| `UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | 3 | UI tile size shift (8 pixels). |
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` | 32 | Max small tile maps. |
| `UI_TILE_MAP__SMALL__WIDTH/HEIGHT` | 8 | Small tile map dimensions. |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | 16 | Max medium tile maps. |
| `UI_TILE_MAP__MEDIUM__WIDTH/HEIGHT` | 16 | Medium tile map dimensions. |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | 8 | Max large tile maps. |
| `UI_TILE_MAP__LARGE__WIDTH/HEIGHT` | 32 | Large tile map dimensions. |

## Compile-Time Validation

The file includes `#error` directives to validate:

- `LOCAL_SPACE_MANAGER__WIDTH >= GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS`
- `LOCAL_SPACE_MANAGER__HEIGHT >= GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS`
- `LOCAL_SPACE_MANAGER__DEPTH >= GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS`

## Agentic Workflow

### Role in the Engine

`platform_defaults.h` provides sensible defaults for all compile-time
configuration. Backends override specific values to match their hardware
constraints (e.g. NDS has different rendering dimensions than SDL).

### Override Pattern

In a backend's `platform_defines.h`:

    #define MAX_QUANTITY_OF__ENTITIES 64  // NDS has less RAM
    #define CAMERA_FULCRUM__WIDTH 256
    #define CAMERA_FULCRUM__HEIGHT 192

Then `platform_defaults.h` will skip those definitions due to `#ifndef`.

### Preconditions

- `platform_defines.h` must be included before this file.
- `config/implemented/engine_config.h` must exist (may be empty).

### Error Handling

- Compile-time `#error` directives enforce dimensional constraints.
- `MAX_SIZE_OF__TCP_PACKET` must be a power of 2 or TCP delivery will
  fail silently at runtime (documented in comments but not enforced at
  compile time).
