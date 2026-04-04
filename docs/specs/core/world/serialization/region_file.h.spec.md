# Specification: core/include/world/serialization/region_file.h

## Overview

Provides a blocking filesystem query to check if a region's save data
exists on disk.

## Dependencies

- `defines.h` (for `World`, `Region_Vector__3i32`)

## Functions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_region_in__directory` | `(World*, Region_Vector__3i32) -> bool` | `bool` | Returns true if the region's save data exists on disk. **WARNING:** This function performs blocking filesystem I/O. |

## Agentic Workflow

### Blocking I/O Warning

This function performs synchronous filesystem access. It should NOT be
called from within a cooperative process handler that needs to yield.
Use it only during initialization or from contexts where blocking is
acceptable.

### Preconditions

- `p_world` must be non-null with a valid name set.

## Header Guard

`REGION_FILE_H`
