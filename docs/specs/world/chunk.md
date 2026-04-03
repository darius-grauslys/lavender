# Chunk Specification

## File
`core/include/world/chunk.h`

## Purpose
Defines operations on `Chunk` — a fixed-size 3D grid of tiles that forms
the basic unit of world storage and serialization. Chunks are identified by
64-bit UUIDs derived from their position.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Chunk`, `Tile`, `Chunk_Flags`, `Local_Tile_Vector__3u8` |
| `numerics.h` | `mod__i8_into__u8`I now have all the dependencies I need. Let me produce the spec documents for all world headers.

docs/specs/world/tile.md
