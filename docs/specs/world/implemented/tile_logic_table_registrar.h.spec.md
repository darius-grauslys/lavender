# Specification: core/include/world/implemented/tile_logic_table_registrar.h

## Overview

Declares the game-specific function that registers all tile logic records
into the `Tile_Logic_Table`. This file is a **template** — it is copied
to the game project directory by `lav_new_project` and is meant to be
modified by the engine user.

## Template Behavior

This file resides in `core/include/world/implemented/` and is copied to
the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the
original in core serves as the default/template. The `implemented/`
directory is NOT in the core include path — it is only in the game
project's include path.

## Dependencies

- `defines.h` (for `Game`, `Tile_Logic_Table`)

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_tile_logic_tables` | `(Game*, Tile_Logic_Table*) -> void` | Registers all game-specific tile logic records (passability, sight blocking, height, etc.) for each `Tile_Kind`. |

## Agentic Workflow

### Implementation Notes

- Must be implemented by the game project.
- Called during game/world initialization.
- Populates the `Tile_Logic_Table` with `Tile_Logic_Record` entries for
  each `Tile_Kind` the game defines.
- The `Tile_Kind` enum must be extended in the game's
  `types/implemented/tile_kind.h`.

## Header Guard

`TILE_LOGIC_TABLE_REGISTRAR_H`
