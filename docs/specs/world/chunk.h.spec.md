# Specification: core/include/world/chunk.h

## Overview

Defines operations on `Chunk` — a fixed-size 3D grid of tiles that forms
the basic unit of world storage and serialization. Chunks are identified
by 64-bit UUIDs derived from their position. Provides tile access by local
coordinates, flag management, and serialization process handlers.

## Dependencies

- `defines.h` (for `Chunk`, `Tile`, `Chunk_Flags`, `Local_Tile_Vector__3u8`, `Identifier__u64`)
- `numerics.h` (for `mod__i8_into__u8`)
- `platform_defines.h` (platform overrides)
- `tile.h` (for `Tile` type)
- `vectors.h` (for vector types)

## Types

### Chunk (struct)

    typedef struct Chunk_t {
        Serialization_Header__UUID_64 _serialization_header;
        Chunk_Flags chunk_flags;
        union {
            Tile tiles[CHUNK__QUANTITY_OF__TILES];
            Chunk_Data chunk_data;
        };
    } Chunk;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header__UUID_64` | 64-bit UUID for position-based identification. |
| `chunk_flags` | `Chunk_Flags` | State flags (active, serializing, updated, etc.). |
| `tiles` | `Tile[CHUNK__QUANTITY_OF__TILES]` | Flat array of tiles. |
| `chunk_data` | `Chunk_Data` | Union alias for the tile array. |

### Chunk_Flags (u16)

| Flag | Bit | Description |
|------|-----|-------------|
| `CHUNK_FLAG__IS_ACTIVE` | 0 | Chunk is ready for rendering and updates. |
| `CHUNK_FLAG__IS_AWAITING_SERIALIZATION` | 1 | Chunk is being serialized. |
| `CHUNK_FLAG__IS_AWAITING_DESERIALIZATION` | 2 | Chunk is being deserialized. |
| `CHUNK_FLAG__IS_UPDATED` | 3 | Tile data changed, needs save. |
| `CHUNK_FLAG__IS_VISUALLY_UPDATED` | 4 | Visual change only, no save needed. |
| `CHUNK_FLAG__MODDABLE_3` through `CHUNK_FLAG__MODDABLE_0` | 9-12 | Available for game use. |

### Chunk Dimensions

| Macro | Default | Description |
|-------|---------|-------------|
| `CHUNK__WIDTH` | `8` | Tiles per chunk (X). |
| `CHUNK__HEIGHT` | `8` | Tiles per chunk (Y). |
| `CHUNK__DEPTH` | `2` | Tile layers (Z). |
| `CHUNK__QUANTITY_OF__TILES` | `128` | Total tiles per chunk. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_chunk` | `(Chunk*, Identifier__u64) -> void` | Initializes a chunk with the given UUID. |

### Serialization Process Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__serialize_chunk` | `(Process*, Game*) -> void` | Process handler for chunk serialization. |
| `m_process__deserialize_chunk` | `(Process*, Game*) -> void` | Process handler for chunk deserialization. |

### Tile Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_uuid__chunk` | `(Chunk*) -> Identifier__u64` | `Identifier__u64` | Returns the chunk's UUID. |
| `set_tile_of__chunk` | `(Chunk*, Local_Tile_Vector__3u8, Tile*) -> void` | `void` | Sets a tile at the given local position. |
| `get_p_tile_from__chunk` | `(Chunk*, Local_Tile_Vector__3u8) -> Tile*` | `Tile*` | Returns pointer to tile at local position. Returns null if chunk is null. Debug builds bounds-check. |
| `try_get_p_tile_from__chunk` | `(Chunk*, Local_Tile_Vector__3u8) -> Tile*` | `Tile*` | Same as above but returns null on out-of-bounds instead of debug error. |
| `get_p_tile_from__chunk_neighborhood` | `(Chunk*, Chunk*[8], i8, i8, u8) -> Tile*` | `Tile*` | Accesses tiles across chunk boundaries using an 8-neighbor array. |
| `get_p_tile_from__chunk_using__u8` | `(Chunk*, u8, u8, u8) -> Tile*` | `Tile*` | Direct u8 index access without `Local_Tile_Vector__3u8`. |

### Tile Index Layout

Tiles are stored in row-major order with Y inverted:

    index = x + ((CHUNK__HEIGHT - 1 - y) * CHUNK__WIDTH) + (CHUNK__WIDTH * CHUNK__HEIGHT * z)

### Flag Management (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `clear_chunk_flags` | `(Chunk*) -> void` | Clears all flags. **Warning:** drops `IS_UPDATED`. |
| `set_chunk_as__awaiting_serialization` | `(Chunk*) -> void` | Sets serialization flag, clears deserialization and active. |
| `set_chunk_as__awaiting_deserialization` | `(Chunk*) -> void` | Sets deserialization flag, clears serialization and active. |
| `set_chunk_as__active` | `(Chunk*) -> void` | Sets active, clears serialization/deserialization. |
| `set_chunk_as__inactive` | `(Chunk*) -> void` | Clears active flag. |
| `set_chunk_as__updated` | `(Chunk*) -> void` | Sets updated flag. Once set, not cleared automatically. |
| `set_chunk_as__visually_updated` | `(Chunk*) -> void` | Sets visual update flag. |
| `set_chunk_as__visually_committed` | `(Chunk*) -> void` | Clears visual update flag. |

### Flag Queries (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `is_chunk__awaiting_serialization` | `bool` | True if serialization flag set. |
| `is_chunk__awaiting_deserialization` | `bool` | True if deserialization flag set. |
| `is_chunk__active` | `bool` | True if active flag set. |
| `is_chunk__inactive` | `bool` | True if active flag NOT set. |
| `is_chunk__updated` | `bool` | True if updated flag set. |
| `is_chunk__visually_updated` | `bool` | True if visual update flag set. |

## Agentic Workflow

### Chunk Neighborhood Array Layout

The 8-neighbor array for `get_p_tile_from__chunk_neighborhood` is indexed:

    [0] = south-west    [1] = south     [2] = south-east
    [3] = west           (self)         [4] = east
    [5] = north-west    [6] = north     [7] = north-east

### Serialization State Machine

Chunks transition through states:

    [inactive] → set_chunk_as__awaiting_deserialization → [deserializing]
    [deserializing] → set_chunk_as__active → [active]
    [active] → set_chunk_as__awaiting_serialization → [serializing]
    [serializing] → set_chunk_as__inactive → [inactive]

### Preconditions

- `get_p_tile_from__chunk`: debug builds abort if local coordinates exceed `CHUNK__WIDTH`.
- `set_tile_of__chunk`: no bounds checking in release builds.

## Header Guard

`CHUNK_H`
