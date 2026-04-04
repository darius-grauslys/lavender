# Specification: core/include/types/implemented/tile_logic_table_list.h

## Overview

Template header that defines the `MAX_QUANTITY_OF__TILE_LOGIC_TABLES`
constant — the maximum number of tile logic tables that can be registered.
This file is copied to the game project directory by `tools/lav_new_project`
and is meant to be modified by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_TILE_LOGIC_TABLE_LIST` is not defined
after the `#include`, the including code falls back to a built-in default.

## Dependencies

- `defines_weak.h` (for forward declarations)

## Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__TILE_LOGIC_TABLES` | `8` | Maximum number of tile logic tables. |

## Injection Mechanism

    #include "types/implemented/tile_logic_table_list.h"
    #ifndef DEFINE_TILE_LOGIC_TABLE_LIST
    #define MAX_QUANTITY_OF__TILE_LOGIC_TABLES 8
    #endif

## Agentic Workflow

### Extension Pattern

Increase the limit if your game needs more tile logic tables:

    #define MAX_QUANTITY_OF__TILE_LOGIC_TABLES 16

### Constraints

- The `#define DEFINE_TILE_LOGIC_TABLE_LIST` line must not be removed.

## Header Guard

`IMPL_TILE_LOGIC_TABLE_LIST_H`
