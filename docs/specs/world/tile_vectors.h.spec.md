# Specification: core/include/world/tile_vectors.h

## Overview

Provides `static inline` conversion functions between pixel-space vectors
(`Vector__3i32`, `Vector__3i32F4`, `Vector__3i32F20`), tile-space vectors
(`Tile_Vector__3i32`), and local tile indices (`Local_Tile_Vector__3u8`).
Tile vectors represent positions in tile coordinates where each tile is
`TILE__WIDTH_AND__HEIGHT_IN__PIXELS` (default 8) pixels wide/tall.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Tile_Vector__3i32`, `Local_Tile_Vector__3u8`, `Ray__3i32F20`)
- `numerics.h` (for `ARITHMETRIC_MASK`, `ARITHMETRIC_R_SHIFT`, fixed-point conversions)
- `platform_defaults.h` (for `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`, `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`)
- `platform_defines.h` (platform overrides)
- `vectors.h` (vector constructors and accessors)
- `world/chunk_vectors.h` (chunk vector conversions)

## Types

### Tile_Vector__3i32

    typedef struct Vector__3i32_t Tile_Vector__3i32;

A `Vector__3i32` where each component is a tile index (not pixels).

### Local_Tile_Vector__3u8

    typedef Vector__3u8 Local_Tile_Vector__3u8;

A tile position local to a single chunk. Each component is in range
`[0, CHUNK__WIDTH)`.

### Key Constants

| Macro | Default | Description |
|-------|---------|-------------|
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(tile size in pixels) = 8px. |
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `8` | Tile size in pixels. |
| `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(tiles per chunk edge) = 8 tiles. |

## Functions

All functions are `static inline`.

### Pixel-to-Tile Normalization

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `normalize_xyz_i32_to__tile_xyz_i32` | `(i32) -> i32` | `i32` | Converts a pixel coordinate to a tile coordinate via right-shift. |
| `normalize_xyz_i32F4_to__tile_xyz_i32` | `(i32F4) -> i32` | `i32` | Converts i32F4 pixel coordinate to tile coordinate. |
| `normalize_xyz_i32F20_to__tile_xyz_i32` | `(i32F20) -> i32` | `i32` | Converts i32F20 pixel coordinate to tile coordinate. |
| `normalize_i32__to_tile_u8` | `(Signed_Index__i32) -> Index__u8` | `Index__u8` | Converts pixel coordinate to local tile index (0-7). Handles negatives. |
| `normalize_i32F4__to_tile_u8` | `(i32F4) -> Index__u8` | `Index__u8` | Same as above for i32F4 input. |

### Component Extraction

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_tile_x_u8_from__vector_3i32F4` | `(Vector__3i32F4) -> Index__u8` | `Index__u8` | Extracts local tile X index from pixel vector. |
| `get_tile_y_u8_from__vector_3i32F4` | `(Vector__3i32F4) -> Index__u8` | `Index__u8` | Extracts local tile Y index from pixel vector. |
| `get_tile_z_u8_from__vector_3i32F4` | `(Vector__3i32F4) -> Index__u8` | `Index__u8` | Extracts local tile Z index from pixel vector. |

### Tile Vector Construction

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_tile_vector` | `(i32, i32, i32) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Constructs from tile indices directly. |
| `get_tile_vector_using__i32F4` | `(i32F4, i32F4, i32F4) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Constructs from i32F4 pixel coordinates. |
| `get_tile_vector_using__3i32F4` | `(Vector__3i32F4) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Constructs from a pixel vector. |

### Vector-to-Tile Conversions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `vector_3i32_to__tile_vector` | `(Vector__3i32F4) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Converts pixel i32 vector to tile vector. **Note:** parameter type is `Vector__3i32F4` despite the name. |
| `vector_3i32F4_to__tile_vector` | `(Vector__3i32F4) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Converts i32F4 pixel vector to tile vector. |
| `vector_3i32F20_to__tile_vector` | `(Vector__3i32F20) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Converts i32F20 pixel vector to tile vector. |
| `get_ray_endpoint_as__tile_vector` | `(Ray__3i32F20*) -> Tile_Vector__3i32` | `Tile_Vector__3i32` | Returns ray's current position as tile vector. |

### Tile-to-Pixel Conversions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `tile_vector_3i32_to__vector_3i32` | `(Tile_Vector__3i32) -> Vector__3i32` | `Vector__3i32` | Converts tile vector to pixel vector. |
| `tile_vector_3i32_to__vector_3i32F4` | `(Tile_Vector__3i32) -> Vector__3i32F4` | `Vector__3i32F4` | Converts tile vector to i32F4 pixel vector. |

### Tile-to-Local Conversions

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `tile_vector_3i32_to__local_tile_vector_3u8` | `(Tile_Vector__3i32) -> Local_Tile_Vector__3u8` | `Local_Tile_Vector__3u8` | Extracts chunk-local tile position from global tile vector. |
| `vector_3i32F4_to__local_tile_vector_3u8` | `(Vector__3i32F4) -> Local_Tile_Vector__3u8` | `Local_Tile_Vector__3u8` | Converts pixel vector directly to local tile vector. |

## Agentic Workflow

### Coordinate System

The engine uses three coordinate spaces for world positions:

1. **Pixel space** (`Vector__3i32`, `Vector__3i32F4`, `Vector__3i32F20`) — absolute positions.
2. **Tile space** (`Tile_Vector__3i32`) — each unit = one tile = 8 pixels.
3. **Chunk-local tile space** (`Local_Tile_Vector__3u8`) — tile index within a chunk (0-7 per axis).

Conversion chain: `pixel → tile → chunk-local tile`.

### Negative Coordinate Handling

All normalization functions handle negative coordinates correctly using
`ARITHMETRIC_MASK` and `ARITHMETRIC_R_SHIFT` which are defined to produce
consistent results for negative values (unlike C's implementation-defined
behavior for right-shift on negatives).

### Preconditions

- `get_ray_endpoint_as__tile_vector` requires a non-null `p_ray`.
- All other functions are pure value transformations with no preconditions.

## Header Guard

`TILE_VECTORS_H`
