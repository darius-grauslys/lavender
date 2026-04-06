# 1 System Overview: Enum Map Utilities

## 1.1 Purpose

The enum map module provides a generic, macro-based mechanism for
associating runtime values with engine enum types. An `ENUM_MAP` is a
fixed-size array indexed by enum value, supporting O(1) registration
and lookup. This is the engine's primary pattern for function dispatch
tables, configuration records, and any enum-keyed association.

## 1.2 Architecture

### 1.2.1 Data Structure

    ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)

    Produces:
    +--------------------------------------------------+
    | My_Map                                           |
    | +----------------------------------------------+ |
    | | _values[0]          (My_Enum_Kind__None)     | |
    | | _values[1]          (My_Enum_Kind__Foo)      | |
    | | _values[2]          (My_Enum_Kind__Bar)      | |
    | | ...                                          | |
    | | _values[N-1]        (last valid variant)     | |
    | +----------------------------------------------+ |
    +--------------------------------------------------+
    Array size = My_Enum_Kind__Unknown (sentinel value)

### 1.2.2 Enum Convention

The key enum **must** follow the engine convention:

    typedef enum My_Enum_Kind {
        My_Enum_Kind__None = 0,     // default/empty slot
        My_Enum_Kind__Foo,
        My_Enum_Kind__Bar,
        // ...
        My_Enum_Kind__Unknown       // sentinel, used as array size
    } My_Enum_Kind;

- `__None` (value 0) is the default/empty slot. On lookup errors in
  debug builds, the `__None` slot value is returned as a safe fallback.
- `__Unknown` is the count sentinel and must be the last entry. It
  determines the array size and is never a valid key.
- All values between `__None` and `__Unknown` are valid keys.

### 1.2.3 Generated API

For each instantiation `ENUM_MAP(Name, Enum, Value)`, the following
functions are generated:

| Function | Kind | Description |
|----------|------|-------------|
| `initialize_enum_map__Name` | Defined via `DEFINE_API` | `memset`s the entire struct to zero |
| `register_Value_into__Name` | Defined via `DEFINE_API` | Stores a value at an enum key |
| `get_Value_from__Name` | Defined via `DEFINE_API` | Returns the value at an enum key |
| `get_p_Value_by__enum_key_from__Name` | Static inline | Returns a pointer to the value slot |

## 1.3 Lifecycle

### 1.3.1 Instantiation

**Header file**:

    #include "util/enum_map/enum_map.h"

    ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)
    DECLARE_API__ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)

**Source file**:

    #include "my_header.h"

    DEFINE_API__ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)

The `ENUM_MAP` macro defines the struct type. `DECLARE_API__ENUM_MAP`
declares function prototypes. `DEFINE_API__ENUM_MAP` defines the
function implementations.

### 1.3.2 Initialization

    My_Map my_map;
    initialize_enum_map__My_Map(&my_map);

After initialization, all slots are zeroed. For pointer-containing
value types, all pointers are null. For numeric types, all values are
zero.

### 1.3.3 Registration

    My_Value_Type value = { ... };
    register_My_Value_Type_into__My_Map(
            &my_map,
            My_Enum_Kind__Foo,
            value);

Stores `value` at the slot indexed by `My_Enum_Kind__Foo`. Only the
specified slot is modified.

### 1.3.4 Lookup

    // By value (copy)
    My_Value_Type result =
        get_My_Value_Type_from__My_Map(
                &my_map,
                My_Enum_Kind__Foo);

    // By pointer (for mutation)
    My_Value_Type *p_result =
        get_p_My_Value_Type_by__enum_key_from__My_Map(
                &my_map,
                My_Enum_Kind__Foo);

## 1.4 Usage in the Engine

Enum maps are used wherever an enum discriminator must be associated
with a runtime value:

| Consumer | Enum Type | Value Type | Purpose |
|----------|-----------|------------|---------|
| Hitbox Context | `Hitbox_Manager_Type` | Invocation table | Dispatch hitbox manager operations by type |
| Entity System | Entity kind enum | Entity function records | Dispatch entity behavior by kind |
| Sprite System | `Sprite_Animation_Kind` | Animation data | Map animation kinds to animation parameters |
| Hitbox System | `Hitbox_Kind` | Hitbox registration records | Map hitbox kinds to component metadata |

## 1.5 Error Handling

| Condition | Debug Build | Release Build |
|-----------|------------|---------------|
| `register` with out-of-range key | `debug_error`, no-op | Undefined behavior |
| `get` (by value) with out-of-range key | `debug_error`, returns `_values[__None]` | Undefined behavior |
| `get_p` (by pointer) with out-of-range key | `debug_error`, returns `0` (null) | Undefined behavior |

## 1.6 Preconditions and Postconditions

### 1.6.1 Preconditions

- `initialize_enum_map__<name>`: pointer must be non-null.
- `register_<type_value>_into__<name>`: `enum_key` must be in range
  `[0, type_enum__Unknown)`.
- `get_<type_value>_from__<name>`: `enum_key` must be in range
  `[0, type_enum__Unknown)`.

### 1.6.2 Postconditions

- After `initialize_enum_map__<name>`: all slots are zeroed.
- After `register_<type_value>_into__<name>`: the value at `enum_key`
  is set. No other slots are modified.
- `get_<type_value>_from__<name>`: returns the value without modifying
  the map.

## 1.7 Memory Layout

    struct <name>_t {
        <type_value> _values[<type_enum>__Unknown];
    };

Total size: `sizeof(type_value) × type_enum__Unknown`.

The struct is a simple wrapper around a fixed-size array with no
additional metadata, pointers, or allocation state.
