# Specification: core/include/types/implemented/item_data.h

## Overview

Template header that defines the `Item_Data` struct — the game-specific
data payload embedded in every `Item`. This file is copied to the game
project directory by `tools/lav_new_project` and is meant to be extended
by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_ITEM_DATA` is not defined after the
`#include`, `defines.h` falls back to a built-in default (empty struct).

## Dependencies

- `defines_weak.h` (for forward declarations)

## Types

### Item_Data (struct)

    typedef struct Item_Data_t {

    } Item_Data;

The default template is an empty struct. Games extend it with item-specific
fields.

## Injection Mechanism

In `defines.h`:

    #include "types/implemented/item_data.h"
    #ifndef DEFINE_ITEM_DATA
    typedef struct Item_Data_t {
    } Item_Data;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef struct Item_Data_t {
        Quantity__u16 damage;
        Quantity__u16 durability;
        Quantity__u8  weight;
    } Item_Data;

### Constraints

- The struct is embedded in `Item` (at `item.item_data`), which is embedded
  in `Item_Stack`, which is embedded in `Inventory`. Size affects the total
  `Inventory` memory footprint.
- The `#define DEFINE_ITEM_DATA` line must not be removed.

## Header Guard

`ITEM_DATA_H`
