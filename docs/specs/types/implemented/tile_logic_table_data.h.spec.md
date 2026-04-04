# Specification: core/include/types/implemented/tile_logic_table_data.h

## Overview

Template header that defines the `Tile_Logic_Table_Data` struct — the
storage backing for the `Tile_Logic_Table`. By default this is a simple
array of `Tile_Logic_Record` indexed by `Tile_Kind`. This file is copied
to the game project directory by `tools/lav_new_project` and is meant to
be extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_TILE_LOGIC_TABLE_DATA` is not defined
after the `#include`, `defines.h` falls back to a built-in default.

## Dependencies

- `defines_weak.h` (for `Tile_Logic_Record`, `Tile_Kind`)

## Types

### Tile_Logic_Table_Data (struct)

    typedef struct Tile_Logic_Table_Data_t {
        Tile_Logic_Record tile_logic_record__tile_kind[
            Tile_Kind__Unknown];
    } Tile_Logic_Table_Data;

| Field | Type | Description |
|-------|------|-------------|
| `tile_logic_record__tile_kind` | `Tile_Logic_Record[Tile_Kind__Unknown]` | Array of logic records indexed by `Tile_Kind`. |

## Injection Mechanism

In `defines.h`:

    #include <types/implemented/tile_logic_table_data.h>
    #ifndef DEFINE_TILE_LOGIC_TABLE_DATA
    typedef struct Tile_Logic_Table_Data_t { ... } Tile_Logic_Table_Data;
    #endif

## Agentic Workflow

### Extension Pattern

Replace the simple array with a more complex structure if needed:

    typedef struct Tile_Logic_Table_Data_t {
        Tile_Logic_Record tile_logic_record__tile_kind[
            Tile_Kind__Unknown];
        Tile_Logic_Record tile_logic_record__biome_overrides[
            Chunk_Generator_Kind__Unknown][Tile_Kind__Unknown];
    } Tile_Logic_Table_Data;

### Constraints

- Embedded in `Tile_Logic_Table` (at `tile_logic_table.tile_logic_table_data`).
- If you change the structure, you must also provide a custom
  `m_Tile_Logic_Table__Get_Tile_Logic_Record` callback.
- The `#define DEFINE_TILE_LOGIC_TABLE_DATA` line must not be removed.

## Header Guard

`IMPL_TILE_LOGIC_RECORD_DATA_H`
