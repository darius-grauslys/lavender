# Specification: core/include/ui/ui_tile.h

## Overview

Defines initialization and manipulation operations on individual `UI_Tile`
values — the smallest visual unit in the tile-based UI composition system.
A `UI_Tile` pairs a `UI_Tile_Kind` (10-bit tile index into a tileset) with
`UI_Tile_Flags` (6-bit flags controlling rendering: flipping, scaling).

## Dependencies

- `defines.h` (for `UI_Tile`, `UI_Tile_Kind`, `UI_Tile_Flags`, `UI_Tile_Raw`, flag macros)

## Types

### UI_Tile (struct)

    typedef struct UI_Tile_t {
        UI_Tile_Kind the_kind_of__ui_tile   :10;
        UI_Tile_Flags ui_tile_flags         :6;
    } UI_Tile;

| Field | Type | Description |
|-------|------|-------------|
| `the_kind_of__ui_tile` | `UI_Tile_Kind` (10 bits) | Index identifying which tile graphic to use. |
| `ui_tile_flags` | `UI_Tile_Flags` (6 bits) | Rendering flags. |

### UI_Tile_Raw (u16)

    typedef u16 UI_Tile_Raw;

A packed 16-bit representation of a `UI_Tile`, suitable for tile map storage.
Layout: bits `[0..9]` = tile kind, bits `[10..15]` = flags (unless
`UI_TILE__IS_NOT__SAVING_FLAGS_TO__RAW` is defined).

### UI_Tile_Flags (u16)

| Flag | Bit | Description |
|------|-----|-------------|
| `UI_TILE_FLAG__SCALE_VERTICAL` | 0 | Tile scales vertically. |
| `UI_TILE_FLAG__SCALE_HORIZONTAL` | 1 | Tile scales horizontally. |
| `UI_TILE_FLAG__FLIPPED_VERTICAL` | 2 | Tile is flipped vertically. |
| `UI_TILE_FLAG__FLIPPED_HORIZONTAL` | 3 | Tile is flipped horizontally. |
| `UI_TILE_FLAG__GENERAL_1` | 4 | General purpose flag 1. |
| `UI_TILE_FLAG__GENERAL_2` | 5 | General purpose flag 2. |

### Compile-Time Configuration

| Macro | Effect |
|-------|--------|
| `UI_TILE__IS_NOT__SAVING_FLAGS_TO__RAW` | If defined, `get_ui_tile_raw_from__ui_tile` omits flags from the raw value. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_ui_tile_as__empty` | `(UI_Tile*) -> void` | Initializes tile to `UI_Tile_Kind__None` with no flags. |
| `initialize_ui_tile` | `(UI_Tile*, UI_Tile_Kind, UI_Tile_Flags) -> void` | Initializes tile with specific kind and flags. |

### Conversion (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_ui_tile_raw_from__ui_tile` | `(const UI_Tile*) -> UI_Tile_Raw` | `UI_Tile_Raw` | Packs tile into 16-bit raw form. Bits `[0..9]` = kind, `[10..15]` = flags. |
| `set_ui_tile_to__ui_tile_raw` | `(UI_Tile*, UI_Tile_Raw*) -> void` | `void` | Writes packed raw representation into `*p_ui_tile_raw`. |

### Flip Mutations (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_ui_tile_as__flipped_horizontally` | `(UI_Tile*) -> void` | Sets `UI_TILE_FLAG__FLIPPED_HORIZONTAL`. |
| `set_ui_tile_as__flipped_vertically` | `(UI_Tile*) -> void` | Sets `UI_TILE_FLAG__FLIPPED_VERTICAL`. |
| `set_ui_tile_as__unflipped_horizontally` | `(UI_Tile*) -> void` | Clears `UI_TILE_FLAG__FLIPPED_HORIZONTAL`. |
| `set_ui_tile_as__unflipped_vertically` | `(UI_Tile*) -> void` | Clears `UI_TILE_FLAG__FLIPPED_VERTICAL`. |

### Scale Mutations (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_ui_tile_as__scaling_horizontally` | `(UI_Tile*) -> void` | Sets `UI_TILE_FLAG__SCALE_HORIZONTAL`. |
| `set_ui_tile_as__scaling_vertically` | `(UI_Tile*) -> void` | Sets `UI_TILE_FLAG__SCALE_VERTICAL`. |
| `set_ui_tile_as__not_scaling_horizontally` | `(UI_Tile*) -> void` | Clears `UI_TILE_FLAG__SCALE_HORIZONTAL`. |
| `set_ui_tile_as__not_scaling_vertically` | `(UI_Tile*) -> void` | Clears `UI_TILE_FLAG__SCALE_VERTICAL`. |

## Agentic Workflow

### Usage Pattern

`UI_Tile` is the atomic element stored in `UI_Tile_Map__Wrapper` (via
`UI_Tile_Raw`). `UI_Tile_Span` (see `ui_tile_span.h`) composes multiple
`UI_Tile` values to describe a 9-slice UI panel. Platform compose functions
read `UI_Tile_Raw` arrays from tile maps to render UI windows.

### Preconditions

- All functions require non-null `p_ui_tile`.

### Postconditions

- Flag mutation functions modify only the targeted bit, preserving all others.

## Header Guard

`UI_TILE_H`
