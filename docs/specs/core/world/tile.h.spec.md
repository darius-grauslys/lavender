# 1 Specification: core/include/world/tile.h

## 1.1 Overview

Provides `static inline` helper functions for querying and mutating `Tile`
and `Tile_Flags__u8` values. Tiles are the atomic world-building unit — each
chunk contains a fixed grid of tiles. This header contains no non-inline
functions.

## 1.2 Dependencies

- `defines_weak.h` (for `Tile_Flags__u8`, `Tile_Kind`, flag macros)
- `defines.h` (for `Tile` struct)

## 1.3 Types

### 1.3.1 Tile (struct)

    typedef struct Tile_t {
        Tile_Kind the_kind_of__tile;
    } Tile;

**Note:** This is the default definition. Games may override via
`types/implemented/tile.h` with `#define DEFINE_TILE`.

| Field | Type | Description |
|-------|------|-------------|
| `the_kind_of__tile` | `Tile_Kind` | Enum identifying the tile type. |

### 1.3.2 Tile_Kind (enum)

    typedef enum Tile_Kind {
        Tile_Kind__None = 0,
        Tile_Kind__Unknown
    } Tile_Kind;

Games extend this enum in their `implemented/` copy.

### 1.3.3 Tile_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `TILE_FLAGS__BIT_IS_SIGHT_BLOCKING` | 0 | Tile blocks line of sight. |
| `TILE_FLAGS__BIT_IS_UNPASSABLE` | 1 | Tile blocks movement. |
| `TILE_FLAGS__BIT_IS_CONTAINER` | 2 | Tile has an inventory. |
| `TILE_FLAGS__BIT_GENERAL_PURPOSE_DATA_BIT` | 3 | General purpose flag. |

## 1.4 Functions

### 1.4.1 Flag Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_tile__unpassable` | `(Tile_Flags__u8) -> bool` | `bool` | True if `TILE_FLAGS__BIT_IS_UNPASSABLE` is set. |
| `is_tile__sight_blocking` | `(Tile_Flags__u8) -> bool` | `bool` | True if `TILE_FLAGS__BIT_IS_SIGHT_BLOCKING` is set. |

### 1.4.2 Flag Mutations (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_tile__is_unpassable` | `(Tile_Flags__u8*, bool) -> void` | Sets or clears the unpassable flag. |
| `set_tile__is_sight_blocking` | `(Tile_Flags__u8*, bool) -> void` | Sets or clears the sight blocking flag. |
| `set_tile__sight_blocking` | `(Tile_Flags__u8*, bool) -> void` | Alias for `set_tile__is_sight_blocking`. |

### 1.4.3 Kind Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_tile_kind_of__tile` | `(Tile*, Tile_Kind) -> void` | `void` | Sets the tile's kind. |
| `get_tile_kind_from__tile` | `(Tile*) -> Tile_Kind` | `Tile_Kind` | Returns the tile's kind. |
| `is_tile_of__this_kind` | `(Tile*, Tile_Kind) -> bool` | `bool` | True if the tile matches the given kind. |
| `is_tile_kind__illegal` | `(Tile_Kind) -> bool` | `bool` | True if kind is outside `[Tile_Kind__None, Tile_Kind__Unknown)`. |

## 1.5 Agentic Workflow

### 1.5.1 Usage Pattern

Tiles are accessed from chunks via `get_p_tile_from__chunk` (see `chunk.h`).
Logic properties (passability, height) are looked up via `Tile_Logic_Table`
(see `tile_logic_table.h`), not from the tile directly. The `Tile_Flags__u8`
type is used in serialization contexts and legacy code; prefer
`Tile_Logic_Record` queries for runtime logic.

### 1.5.2 Preconditions

- All functions taking `Tile*` require a non-null pointer.
- `is_tile_kind__illegal` can be called with any value.

### 1.5.3 Postconditions

- Flag mutation functions modify only the targeted bit, preserving all others.

## 1.6 Header Guard

`TILE_H`
