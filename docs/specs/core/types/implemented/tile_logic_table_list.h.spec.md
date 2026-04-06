# 1 Specification: core/include/types/implemented/tile_logic_table_list.h

## 1.1 Overview

Template header that defines the `MAX_QUANTITY_OF__TILE_LOGIC_TABLES`
constant — the maximum number of tile logic tables that can be registered.
This file is copied to the game project directory by `tools/lav_new_project`
and is meant to be modified by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_TILE_LOGIC_TABLE_LIST` is not defined
after the `#include`, the including code falls back to a built-in default.

## 1.3 Dependencies

- `defines_weak.h` (for forward declarations)

## 1.4 Constants

| Macro | Value | Description |
|-------|-------|-------------|
| `MAX_QUANTITY_OF__TILE_LOGIC_TABLES` | `8` | Maximum number of tile logic tables. |

## 1.5 Injection Mechanism

    #include "types/implemented/tile_logic_table_list.h"
    #ifndef DEFINE_TILE_LOGIC_TABLE_LIST
    #define MAX_QUANTITY_OF__TILE_LOGIC_TABLES 8
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

Increase the limit if your game needs more tile logic tables:

    #define MAX_QUANTITY_OF__TILE_LOGIC_TABLES 16

### 1.6.2 Constraints

- The `#define DEFINE_TILE_LOGIC_TABLE_LIST` line must not be removed.

## 1.7 Header Guard

`IMPL_TILE_LOGIC_TABLE_LIST_H`
