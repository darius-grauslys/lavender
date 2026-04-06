# 1 Specification: core/include/world/tile_logic_table.h

## 1.1 Overview

Manages the logic properties associated with tile kinds — passability,
sight blocking, ground presence, and tile height. The table maps `Tile_Kind`
values to `Tile_Logic_Record` entries, enabling efficient per-tile physics
and collision queries.

## 1.2 Dependencies

- `defines.h` (for `Tile_Logic_Table`, `Tile_Logic_Record`, `Tile`)
- `defines_weak.h` (forward declarations, flag macros)

## 1.3 Types

### 1.3.1 Tile_Logic_Record (struct)

    typedef struct Tile_Logic_Record_t {
        Tile_Logic_Flags__u16 tile_logic_flags__u8;
        i32F4 tile_height__i32F4;
    } Tile_Logic_Record;

| Field | Type | Description |
|-------|------|-------------|
| `tile_logic_flags__u8` | `Tile_Logic_Flags__u16` | Bitfield of logic properties. Name is legacy (`__u8`). |
| `tile_height__i32F4` | `i32F4` | Tile height in fixed-point `[0, 1 + 15/16]`. |

### 1.3.2 Tile_Logic_Flags__u16 (u16)

| Flag | Bit | Description |
|------|-----|-------------|
| `TILE_LOGIC_FLAG__IS_UNPASSABLE` | 0 | Blocks movement. |
| `TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING` | 1 | Blocks line of sight. |
| `TILE_LOGIC_FLAG__IS_WITHOUT_GROUND` | 2 | No ground (e.g. pits). |
| `TILE_LOGIC_FLAG__RESERVED_1` through `TILE_LOGIC_FLAG__RESERVED_5` | 3-7 | Reserved for engine use. |
| `TILE_LOGIC_FLAG__CUSTOM_0` through `TILE_LOGIC_FLAG__CUSTOM_7` | 8-15 | Available for game use. |

### 1.3.3 Tile_Logic_Table (struct)

    typedef struct Tile_Logic_Table_t {
        Tile_Logic_Table_Data tile_logic_table_data;
        m_Tile_Logic_Table__Get_Tile_Logic_Record m_get_tile_logic_record;
        Quantity__u32 quantity_of__records;
    } Tile_Logic_Table;

| Field | Type | Description |
|-------|------|-------------|
| `tile_logic_table_data` | `Tile_Logic_Table_Data` | Storage for records. Default: array indexed by `Tile_Kind`. |
| `m_get_tile_logic_record` | `m_Tile_Logic_Table__Get_Tile_Logic_Record` | Callback to look up a record for a tile. |
| `quantity_of__records` | `Quantity__u32` | Number of registered records. |

### 1.3.4 m_Tile_Logic_Table__Get_Tile_Logic_Record (function pointer)

    typedef void (*m_Tile_Logic_Table__Get_Tile_Logic_Record)(
            Tile_Logic_Table *p_tile_logic_manager,
            Tile_Logic_Record *p_tile_logic_record,
            Tile *p_tile);

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_tile_logic_table` | `(Tile_Logic_Table*) -> void` | Initializes the table to empty state. |

### 1.4.2 Record Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_tile_logic_record_for__this_tile` | `(Tile_Logic_Table*, Tile_Logic_Record*, Tile*) -> bool` | `bool` | Populates the record for the given tile. |

### 1.4.3 Record Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_tile_logic_record__unpassable` | `(Tile_Logic_Record*) -> bool` | `bool` | True if `IS_UNPASSABLE` set. |
| `is_tile_logic_record__sight_blocking` | `(Tile_Logic_Record*) -> bool` | `bool` | True if `IS_SIGHT_BLOCKING` set. |
| `is_tile_logic_record__without_ground` | `(Tile_Logic_Record*) -> bool` | `bool` | True if `IS_WITHOUT_GROUND` set. |

### 1.4.4 Convenience Poll Functions (static inline)

These combine record lookup and query in one call:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll__is_tile__unpassable` | `(Tile_Logic_Table*, Tile*) -> bool` | `bool` | Looks up record then checks unpassable. |
| `poll__is_tile__sight_blocking` | `(Tile_Logic_Table*, Tile*) -> bool` | `bool` | Looks up record then checks sight blocking. |
| `poll__is_tile__without_ground` | `(Tile_Logic_Table*, Tile*) -> bool` | `bool` | Looks up record then checks ground. |
| `poll__tile_height` | `(Tile_Logic_Table*, Tile*) -> i32F4` | `i32F4` | Looks up record then returns height. |

## 1.5 Agentic Workflow

### 1.5.1 Ownership

Owned by `World` (at `world.tile_logic_table`). Accessed via
`get_p_tile_logic_table_from__world`.

### 1.5.2 Registration

Populated by `register_tile_logic_tables` (see
`implemented/tile_logic_table_registrar.h`), which is a game-implemented
template function.

### 1.5.3 Preconditions

- All functions require non-null pointers.
- `poll__*` functions allocate a `Tile_Logic_Record` on the stack.

## 1.6 Header Guard

`TILE_LOGIC_TABLE_MANAGER_H`
