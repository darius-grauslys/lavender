# Specification: tests/templates/include/platform_defines.h

## Overview

Default values for all platform-specific `#define` constants required by the
engine when building tests without a real platform backend. All definitions
use `#ifndef` guards allowing override.

## Include Guard

    #ifndef PLATFORM_DEFINES_H
    #define PLATFORM_DEFINES_H

## Constants

### File System

| Macro | Default |
|-------|---------|
| `MAX_LENGTH_OF__IO_PATH` | `1024` |
| `PATH_SEPERATOR` | `'\\'` (Windows) or `'/'` (other) |

### Camera

| Macro | Default |
|-------|---------|
| `CAMERA_FULCRUM__WIDTH` | `256` |
| `CAMERA_FULCRUM__HEIGHT` | `196` |

### Textures

| Macro | Default |
|-------|---------|
| `MAX_QUANTITY_OF__TEXTURES` | `128` |

### Chunks

| Macro | Default |
|-------|---------|
| `GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS` | `4` |
| `GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS` | `3` |
| `GFX_CONTEXT__RENDERING_DEPTH__IN_CHUNKS` | `1` |
| `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` |
| `CHUNK__DEPTH__BIT_SHIFT` | `1` |
| `CHUNK__WIDTH` | `BIT(3)` = 8 |
| `CHUNK__HEIGHT` | `BIT(3)` = 8 |
| `CHUNK__DEPTH` | `BIT(1)` = 2 |
| `CHUNK__QUANTITY_OF__TILES` | 128 |

### Tiles

| Macro | Default |
|-------|---------|
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` |
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `BIT(3)` = 8 |

### Local Space Manager

| Macro | Default |
|-------|---------|
| `LOCAL_SPACE_MANAGER__WIDTH` | `8` |
| `LOCAL_SPACE_MANAGER__HEIGHT` | `8` |
| `LOCAL_SPACE_MANAGER__DEPTH` | `1` |
| `VOLUME_OF__LOCAL_SPACE_MANAGER` | 64 |

### Multiplayer / Global Space

| Macro | Default |
|-------|---------|
| `MAX_QUANTITY_OF__CLIENTS` | `4` |
| `QUANTITY_OF__GLOBAL_SPACE` | 256 |

### Entities

| Macro | Default |
|-------|---------|
| `MAX_QUANTITY_OF__ENTITIES` | `128` |

### Input

| Macro | Default |
|-------|---------|
| `SDL_QUANTITY_OF__INPUTS` | `QUANTITY_OF__INPUTS + 1` |
| `SDL_INPUT_CODE_EQUIP` | `QUANTITY_OF__INPUTS` |
| `SDL_INPUT_EQUIP` | `BIT(QUANTITY_OF__INPUTS)` |

### UI Tile Maps

| Macro | Default |
|-------|---------|
| `UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` |
| `UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | 8 |
| `UI_TILE_MAP__SMALL__MAX_QUANTITY_OF` | `32` |
| `UI_TILE_MAP__SMALL__WIDTH` | `8` |
| `UI_TILE_MAP__SMALL__HEIGHT` | `8` |
| `UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF` | `16` |
| `UI_TILE_MAP__MEDIUM__WIDTH` | `16` |
| `UI_TILE_MAP__MEDIUM__HEIGHT` | `16` |
| `UI_TILE_MAP__LARGE__MAX_QUANTITY_OF` | `8` |
| `UI_TILE_MAP__LARGE__WIDTH` | `32` |
| `UI_TILE_MAP__LARGE__HEIGHT` | `32` |

### Texture Formats

| Macro | Value |
|-------|-------|
| `TEXTURE_FLAG__FORMAT__RGB888` | `TEXTURE_FLAG__FORMAT__1` |
| `TEXTURE_FLAG__FORMAT__RGBA8888` | `TEXTURE_FLAG__FORMAT__2` |
| `TEXTURE_FLAG__SDL_FLAGS__BIT_COUNT` | `8` |
| `TEXTURE_FLAG__BIT_SHIFT__SDL_FLAGS` | `TEXTURE_FLAG__BIT_SHIFT__GENERAL_FLAGS` |

### Graphics Windows

| Macro | Default |
|-------|---------|
| `PLATFORM__GFX_WINDOW__MAX_QUANTITY_OF` | `128` |

## External Dependencies

Values reference `BIT()`, `QUANTITY_OF__INPUTS`, `TEXTURE_FLAG__FORMAT__1`,
`TEXTURE_FLAG__FORMAT__2`, `TEXTURE_FLAG__BIT_SHIFT__GENERAL_FLAGS` which
must be defined elsewhere (typically `defines.h`).
