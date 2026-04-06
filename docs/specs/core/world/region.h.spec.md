# 1 Specification: core/include/world/region.h

## 1.1 Overview

Defines operations on `Region` — a large-scale spatial partition used for
serialization. Regions contain bitmaps tracking which chunks and sites have
been serialized. Provides position queries, serialization process handlers,
and chunk vector truncation.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Region`, `Region_Vector__3i32`, `Structure`, `Global_Space`, `Tile_Vector__3i32`)
- `platform_defaults.h` (for `REGION__WIDTH`, `REGION__HEIGHT`, `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`)

## 1.3 Types

### 1.3.1 Region (struct)

    typedef struct Region_t {
        Serialization_Header _serialization_header;
        u8 bitmap_of__serialized_chunks[
            (REGION__WIDTH_IN__CHUNKS * REGION__HEIGHT_IN__CHUNKS >> 3)];
        u8 bitmap_of__sites[
            SITE_QUANTITY_OF__PER_REGION >> 3];
    } Region;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for serialization. |
| `bitmap_of__serialized_chunks` | `u8[]` | Bitmap tracking which chunks have been serialized. |
| `bitmap_of__sites` | `u8[]` | Bitmap tracking which sites exist. |

### 1.3.2 Region_Vector__3i32

    typedef struct Vector__3i32_t Region_Vector__3i32;

### 1.3.3 Region Dimensions

| Macro | Description |
|-------|-------------|
| `REGION__WIDTH` | `BIT(UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS)` = 2048 tiles. |
| `REGION__HEIGHT` | Same as width. |
| `REGION__WIDTH_IN__CHUNKS` | `REGION__WIDTH >> CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`. |
| `REGION__HEIGHT_IN__CHUNKS` | `REGION__HEIGHT >> CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`. |

## 1.4 Functions

### 1.4.1 Spatial Queries

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_tile_position_within__region` | `(Tile_Vector__3i32, Region_Vector__3i32) -> bool` | `bool` | True if the tile position falls within the region. |
| `is_structure_within__region` | `(Structure*, Region_Vector__3i32) -> bool` | `bool` | True if the structure's bounding box overlaps the region. |
| `get_region_that__this_global_space_is_in` | `(Global_Space*) -> Region_Vector__3i32` | `Region_Vector__3i32` | Returns the region vector containing the given global space. |

### 1.4.2 Serialization Process Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__serialize_region` | `(Process*, Game*) -> void` | Process handler for region serialization. |
| `m_process__deserialize_region` | `(Process*, Game*) -> void` | Process handler for region deserialization. |

### 1.4.3 Chunk Vector Truncation (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `truncate_p_chunk_vector_3i32_to__region` | `(Chunk_Vector__3i32*) -> void` | Masks chunk vector components to fit within a single region. |

## 1.5 Agentic Workflow

### 1.5.1 Region as Serialization Unit

Regions are the top-level serialization unit. Each region file on disk
contains the chunk bitmap and site bitmap. Individual chunks are serialized
as separate files within a region directory.

### 1.5.2 Ownership

Managed by `Region_Manager` (see `region_manager.h`).

## 1.6 Header Guard

`REGION`
