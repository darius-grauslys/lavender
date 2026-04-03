# Specification: core/include/world/chunk_vectors.h

## Overview

Provides `static inline` conversion functions between pixel-space vectors,
tile-space vectors, and chunk-space vectors (`Chunk_Vector__3i32`). Chunk
vectors represent positions in chunk coordinates where each chunk spans
`BIT(LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT)` (default 64)
pixels per edge.

## Dependencies

- `defines.h` (for `Chunk_Vector__3i32`, `Tile_Vector__3i32`, vector types)
- `numerics.h` (for `ARITHMETRIC_R_SHIFT`, `ARITHMETRIC_L_SHIFT`, fixed-point conversions)
- `platform_defaults.h` (for `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT`, `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`)
- `platform_defines.h` (platform overrides)
- `vectors.h` (vector constructors and accessors)

## Types

### Chunk_Vector__3i32

    typedef struct Vector__3i32_t Chunk_Vector__3i32;

A `Vector__3i32` where each component is a chunk index.

### Key Constants

| Macro | Default | Description |
|-------|---------|-------------|
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` | `3` | log2(tiles per chunk edge). |
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT` | `6` | log2(pixels per chunk edge) = 64px. |

## Functions

All functions are `static inline`.

### Pixel/Tile-to-Chunk Normalization

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `normalize_xyz_i32_to__chunk_xyz_i32` | `(i32) -> i32` | `i32` | Converts pixel coordinate to chunk coordinate. Subtracts 1 for negatives. |
| `normalize_xyz_tile_i32_to__chunk_xyz_i32` | `(i32) -> i32` | `i32` | Converts tile coordinate to chunk coordinate. |
| `normalize_xyz_i32F4_to__chunk_xyz_i32` | `(i32F4) -> i32` | `i32` | Converts i32F4 pixel coordinate to chunk coordinate. |

### Component Extraction from Pixel Vectors

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_chunk_x_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Extracts chunk X from pixel vector. |
| `get_chunk_y_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Extracts chunk Y from pixel vector. |
| `get_chunk_z_i32_from__vector_3i32F4` | `(Vector__3i32F4) -> i32` | `i32` | Extracts chunk Z from pixel vector. |

### Component Extraction from Tile Vectors

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_chunk_x_i32_from__tile_vector_3i32` | `(Tile_Vector__3i32) -> i32` | `i32` | Extracts chunk X from tile vector. |
| `get_chunk_y_i32_from__tile_vector_3i32` | `(Tile_Vector__3i32) -> i32` | `i32` | Extracts chunk Y from tile vector. |
| `get_chunk_z_i32_from__tile_vector_3i32` | `(Tile_Vector__3i32) -> i32` | `i32` | Extracts chunk Z from tile vector. |

### Constructors

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_chunk_vector__3i32` | `(i32, i32, i32) -> Chunk_Vector__3i32` | `Chunk_Vector__3i32` | Constructs from chunk indices directly. |
| `get_chunk_vector__3i32_with__i32F4` | `(i32F4, i32F4, i32F4) -> Chunk_Vector__3i32` | `Chunk_Vector__3i32` | Constructs from i32F4 pixel coordinates. |

### Cross-Space Conversions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `tile_vector_3i32_to__chunk_vector_3i32` | `(Tile_Vector__3i32) -> Chunk_Vector__3i32` | `Chunk_Vector__3i32` | Tile vector to chunk vector. |
| `vector_3i32F4_to__chunk_vector_3i32` | `(Vector__3i32F4) -> Chunk_Vector__3i32` | `Chunk_Vector__3i32` | Pixel vector to chunk vector. |
| `vector_3i32_to__chunk_vector_3i32` | `(Vector__3i32) -> Chunk_Vector__3i32` | `Chunk_Vector__3i32` | Integer pixel vector to chunk vector. |
| `chunk_vector_3i32_to__tile_vector_3i32` | `(Chunk_Vector__3i32) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Chunk vector to tile vector of its origin. |
| `chunk_vector_3i32_to__vector_3i32` | `(Chunk_Vector__3i32) -> Vector__3i32` | `Vector__3i32` | Chunk vector to pixel vector. |
| `chunk_vector_3i32_to__vector_3i32F4` | `(Chunk_Vector__3i32) -> Vector__3i32F4` | `Vector__3i32F4` | Chunk vector to i32F4 pixel vector. |

## Agentic Workflow

### Negative Coordinate Handling

`normalize_xyz_i32_to__chunk_xyz_i32` subtracts 1 for negative pixel values
to ensure correct floor-division behavior. This is critical for world
coordinates that span negative space.

### Preconditions

- All functions are pure value transformations with no preconditions.

## Header Guard

`CHUNK_VECTORS_H`
