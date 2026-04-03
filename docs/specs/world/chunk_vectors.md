# Chunk Vectors Specification

## File
`core/include/world/chunk_vectors.h`

## Purpose
Provides inline conversion functions between pixel-space vectors, tile-space
vectors, and chunk-space vectors (`Chunk_Vector__3i32`). Chunk vectors
represent positions in chunk coordinates where each chunk spans
`LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS` pixels.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Chunk_Vector__3i32`, `Tile_Vector__3i32`, vector types |
| `numerics.h` | `ARITHMETRIC_R_SHIFT`, `ARITHMETRIC_L_SHIFT`, fixed-point conversions |
| `platform_defaults.h` | `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT`, `TILE__WIDTH_AND__HEIGHT__BIT_SHIFT` |
| `platform_defines.h` | Platform overrides |
| `vectors.h` | Vector constructors and accessors |

## Key Constants
| Macro | Default | Description |
|-------|---------|-------------|
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__TILES__BIT_SHIFT` | `3` | log2(tiles per chunk edge) |
| `LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT` | `6` | log2(pixels per chunk edge) = tile_shift + chunk_shift |

## Functions

All functions are `static inline`.

### Normalization

#### `normalize_xyz_i32_to__chunk_xyz_i32`
