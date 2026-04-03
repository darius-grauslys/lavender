# Tile Vectors Specification

## File
`core/include/world/tile_vectors.h`

## Purpose
Provides inline conversion functions between pixel-space vectors
(`Vector__3i32`, `Vector__3i32F4`, `Vector__3i32F20`), tile-space vectors
(`Tile_Vector__3i32`), and local tile indices (`Local_Tile_Vector__3u8`).
Tile vectors represent positions in tile coordinates where each tile is
`TILE__WIDTH_AND__HEIGHT_IN__PIXELS` pixels wide/tall.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines_weak.h` | Forward declarations |
| `defines.h` | `Tile_Vector__3i32`, `Local_Tile_Vector__3u8`, `Ray__3i32F20` |
| `numerics.h` | `ARITHMETRIC_MASK`, `ARITHMETRIC_R_SHIFT`, fixed-point conversions |
| `platform_defaults.h` | `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`, `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT` |
| `platform_defines.h` | Platform overrides |
| `vectors.h` | Vector constructors and accessors |
| `world/chunk_vectors.h` | Chunk vector conversions |

## Key Constants
| Macro | Default | Description |
|-------|---------|-------------|
| `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` | `3` | log2(tile size in pixels) = 8px |
| `TILE__WIDTH_AND__HEIGHT_IN__PIXELS` | `8` | Tile size in pixels |

## Types Used
- `Tile_Vector__3i32` — alias for `Vector__3i32`, positions in tile coordinates.
- `Local_Tile_Vector__3u8` — alias for `Vector__3u8`, tile indices local to a chunk.

## Functions

All functions are `static inline`.

### Normalization (pixel → tile)

#### `normalize_xyz_i32_to__tile_xyz_i32`
