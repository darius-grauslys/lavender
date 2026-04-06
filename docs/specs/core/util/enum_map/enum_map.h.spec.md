# 1 Specification: core/include/util/enum_map/enum_map.h

## 1.1 Overview

Provides a generic, macro-based enum-to-value map data structure. An
`ENUM_MAP` is a fixed-size array indexed by an enum type, supporting
O(1) registration and lookup of values by enum key. This is the engine's
primary mechanism for associating runtime data (function pointers,
configuration records, etc.) with enum-typed discriminators.

The entire API is generated via preprocessor macros, producing
type-safe structs and functions for each instantiation.

## 1.2 Dependencies

- `debug/debug.h` (for `debug_error` in debug builds)
- `defines_weak.h` (for base types)
- `<string.h>` (for `memset`, used in generated `initialize` function)

## 1.3 Types

### 1.3.1 ENUM_MAP (macro — struct definition)

    #define ENUM_MAP(name, type_enum, type_value) \
        typedef struct name##_t { \
            type_value _values[type_enum##__Unknown]; \
        } name;

Defines a struct named `name` containing a fixed-size array of
`type_value` elements, indexed by `type_enum`. The array size is
`type_enum##__Unknown`, which by convention is the sentinel/count
value at the end of every engine enum.

| Parameter | Type | Description |
|-----------|------|-------------|
| `name` | identifier | The name of the generated struct typedef. |
| `type_enum` | enum type name | The enum type used as the key. Must have a `__Unknown` sentinel. |
| `type_value` | type name | The value type stored in the map. |

**Example instantiation**:

    ENUM_MAP(Entity_Function_Map, Entity_Kind, Entity_Functions)

Produces:

    typedef struct Entity_Function_Map_t {
        Entity_Functions _values[Entity_Kind__Unknown];
    } Entity_Function_Map;

### 1.3.2 Generated Functions

#### 1.3.2.1 DECLARE_API__ENUM_MAP (macro — header declarations)

    #define DECLARE_API__ENUM_MAP(name, type_enum, type_value)

Declares the following function prototypes:

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_enum_map__<name>` | `(<name>*) -> void` | Zeroes the entire map. |
| `register_<type_value>_into__<name>` | `(<name>*, type_enum enum_key, type_value value) -> void` | Stores `value` at `enum_key`. |
| `get_<type_value>_from__<name>` | `(<name>*, type_enum enum_key) -> type_value` | Returns the value at `enum_key`. |

#### 1.3.2.2 DEFINE_API__ENUM_MAP (macro — source definitions)

    #define DEFINE_API__ENUM_MAP(name, type_enum, type_value)

Defines the implementations of the three functions declared by
`DECLARE_API__ENUM_MAP`, plus a static inline helper:

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_enum_map__<name>` | `(<name>*) -> void` | `void` | `memset`s the entire struct to zero. |
| `register_<type_value>_into__<name>` | `(<name>*, type_enum, type_value) -> void` | `void` | Stores the value. Debug builds validate the key range. |
| `get_<type_value>_from__<name>` | `(<name>*, type_enum) -> type_value` | `type_value` | Returns the stored value. Debug builds validate the key range and return `_values[<type_enum>__None]` on error. |
| `get_p_<type_value>_by__enum_key_from__<name>` | `(<name>*, type_enum) -> type_value*` | `type_value*` | (static inline) Returns a pointer to the value slot. Debug builds validate the key range and return `0` on error. |

## 1.4 Agentic Workflow

### 1.4.1 When to Use

Use `ENUM_MAP` when:

- You need to associate a value (struct, function pointer, config record)
  with each variant of an engine enum.
- The enum has a `__None` and `__Unknown` sentinel following engine
  convention.
- O(1) lookup by enum key is required.

Do **not** use `ENUM_MAP` when:

- The key space is sparse or very large. Use a hash map instead.
- The key is not an enum (e.g. UUID). Use `UUID_MAPPED__POOL` instead.

### 1.4.2 Instantiation Pattern

**In a header file** (e.g. `my_system.h`):

    #include "util/enum_map/enum_map.h"

    ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)
    DECLARE_API__ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)

**In a source file** (e.g. `my_system.c`):

    #include "my_system.h"

    DEFINE_API__ENUM_MAP(My_Map, My_Enum_Kind, My_Value_Type)

### 1.4.3 Initialization

    My_Map my_map;
    initialize_enum_map__My_Map(&my_map);

After initialization, all slots are zeroed. For pointer-containing value
types, this means all pointers are null. For numeric types, all values
are zero.

### 1.4.4 Registration and Lookup

    // Register
    My_Value_Type value = { ... };
    register_My_Value_Type_into__My_Map(
            &my_map,
            My_Enum_Kind__Foo,
            value);

    // Lookup (by value)
    My_Value_Type result =
        get_My_Value_Type_from__My_Map(
                &my_map,
                My_Enum_Kind__Foo);

    // Lookup (by pointer, for mutation)
    My_Value_Type *p_result =
        get_p_My_Value_Type_by__enum_key_from__My_Map(
                &my_map,
                My_Enum_Kind__Foo);

### 1.4.5 Enum Convention Requirements

The key enum **must** follow the engine convention:

    typedef enum My_Enum_Kind {
        My_Enum_Kind__None = 0,
        My_Enum_Kind__Foo,
        My_Enum_Kind__Bar,
        // ...
        My_Enum_Kind__Unknown   // <-- sentinel, used as array size
    } My_Enum_Kind;

- `__None` (value 0) is the default/empty slot.
- `__Unknown` is the count sentinel and must be the last entry.
- All values between `__None` and `__Unknown` are valid keys.

### 1.4.6 Preconditions

- `initialize_enum_map__<name>`: pointer must be non-null.
- `register_<type_value>_into__<name>`: `enum_key` must be in range
  `[0, type_enum__Unknown)`. Debug builds emit `debug_error` and
  return early on invalid keys.
- `get_<type_value>_from__<name>`: `enum_key` must be in range
  `[0, type_enum__Unknown)`. Debug builds emit `debug_error` and
  return the `__None` slot value on invalid keys.

### 1.4.7 Postconditions

- After `initialize_enum_map__<name>`: all slots are zeroed.
- After `register_<type_value>_into__<name>`: the value at `enum_key`
  is set to the provided value. No other slots are modified.
- `get_<type_value>_from__<name>`: returns the value at `enum_key`
  without modifying the map.

### 1.4.8 Error Handling

- **Debug builds** (`NDEBUG` not defined): All generated functions
  validate the enum key range. Out-of-range keys trigger `debug_error`
  and result in safe fallback behavior (return `0` for pointer getters,
  return `_values[__None]` for value getters, no-op for register).
- **Release builds** (`NDEBUG` defined): No validation is performed.
  Out-of-range keys result in undefined behavior (array out-of-bounds
  access).

### 1.4.9 Thread Safety

None. Enum maps are not thread-safe. In the cooperative scheduling
model, this is acceptable since only one process handler runs at a time.

### 1.4.10 Memory Layout

The generated struct is a simple wrapper around a fixed-size array:

    struct <name>_t {
        <type_value> _values[<type_enum>__Unknown];
    };

Total size: `sizeof(type_value) * type_enum__Unknown`.
