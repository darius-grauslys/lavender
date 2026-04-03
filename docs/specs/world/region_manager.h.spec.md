# Specification: core/include/world/region_manager.h

## Overview

Manages a fixed-size pool of `Region` instances. Provides initialization
and centering operations for tracking which regions are active around the
player.

## Dependencies

- `defines.h` (for `Region_Manager`, `Region`, `Region_Vector__3i32`, `Game`)

## Types

### Region_Manager (struct)

    typedef struct Region_Manager_t {
        Region regions[REGION_MAX_QUANTITY_OF];
        Region_Vector__3i32 center_of__region_manager;
    } Region_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `regions` | `Region[REGION_MAX_QUANTITY_OF]` | Fixed pool of region instances. |
| `center_of__region_manager` | `Region_Vector__3i32` | Current center region coordinate. |

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `REGION_MAX_QUANTITY_OF` | `4` | Maximum concurrent regions. |

## Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_region_manager` | `(Region_Manager*) -> void` | Initializes all regions as deallocated. |
| `set_center_of__region_manager` | `(Game*, Region_Manager*, Region_Vector__3i32) -> void` | Sets the center region, loading/unloading regions as needed. |

## Agentic Workflow

### Ownership

Owned by `World` (at `world.region_manager`).

## Header Guard

`REGION_MANAGER_H`
