# 1 System Overview: Utility Subsystem

## 1.1 Purpose

The utility subsystem provides foundational generic data structures used
throughout the engine. These are macro-generated, type-safe containers
and algorithms that avoid runtime polymorphism in favor of compile-time
code generation. The three active utility modules are:

- **Bitmap** — Fixed-size bit arrays with optional heap-accelerated
  first-set-bit queries.
- **Enum Map** — Fixed-size arrays indexed by engine enum types for O(1)
  registration and lookup.
- **Hash Map (UUID Mapped Pool)** — Fixed-size pools of
  `Serialization_Header`-bearing elements with UUID-based O(1) allocation,
  deallocation, and lookup.

A fourth module, **Getter**, exists as an empty placeholder reserved for
future getter utility functions.

## 1.2 Architecture

### 1.2.1 Module Hierarchy

    core/include/util/
    ├── bitmap/
    │   └── bitmap.h          — Flat and heap-accelerated bitmap utilities
    ├── enum_map/
    │   └── enum_map.h        — Macro-generated enum-to-value maps
    ├── hash_map/
    │   └── hash_map.h        — Macro-generated UUID-mapped pools
    └── getter/
        └── getter.h          — Reserved placeholder (empty)

### 1.2.2 Relationship Between Modules

The three active modules are independent of each other. None depends on
another util module. Their shared dependencies are limited to core engine
types:

| Module | Key Dependencies |
|--------|-----------------|
| Bitmap | `debug/debug.h`, `defines_weak.h` (`u8`, `Quantity__u32`, `Index__u32`, `BIT`, `MASK`) |
| Enum Map | `debug/debug.h`, `defines_weak.h`, `<string.h>` |
| Hash Map | `defines.h` (`Serialization_Pool`, `Serialization_Header`, `Identifier__u32`), `serialization/hashing.h` (`DEHASH`) |

### 1.2.3 Design Principles

1. **Macro-generated type safety.** Each instantiation of `ENUM_MAP`,
   `UUID_MAPPED__POOL`, `BITMAP`, or `BITMAP_AND_HEAP` produces
   dedicated types and functions. There is no `void*`-based generic
   container at runtime.

2. **Fixed-size allocation.** All containers are statically sized. There
   is no dynamic memory allocation. Pool sizes and bitmap widths are
   compile-time constants.

3. **Debug-build validation.** In debug builds (`NDEBUG` not defined),
   bounds checks and key-range checks emit `debug_error` and fall back
   to safe behavior. In release builds, no validation is performed.

4. **No thread safety.** All utility containers assume cooperative
   single-threaded access consistent with the engine's scheduling model.

## 1.3 Module Summaries

### 1.3.1 Bitmap (`util/bitmap/`)

Provides two bitmap variants:

| Variant | Macro | Lookup Complexity | Use Case |
|---------|-------|-------------------|----------|
| Flat | `BITMAP(name, N)` | O(N) scan | Small bitmaps or set/get only |
| Heap-accelerated | `BITMAP_AND_HEAP(name, N)` | O(log₈ N) first-set-bit | Large bitmaps with frequent first-set-bit queries |

The heap-accelerated variant layers a hierarchical summary on top of the
flat bitmap. Each heap level summarizes 8 entries from the level below
into a single byte, enabling fast top-down traversal to find the first
set bit.

Bitmaps are used for allocation tracking, serialization state,
collision presence, and per-element boolean flags throughout the engine.

See: `docs/specs/util/bitmap/bitmap.h.spec.md`

### 1.3.2 Enum Map (`util/enum_map/`)

Provides O(1) enum-keyed lookup via a fixed-size array indexed by enum
value. The key enum must follow the engine convention with `__None` (0)
and `__Unknown` (sentinel/count) entries.

Three functions are generated per instantiation:

- `initialize_enum_map__<name>` — zeroes all slots.
- `register_<type_value>_into__<name>` — stores a value at an enum key.
- `get_<type_value>_from__<name>` — retrieves a value by enum key.
- `get_p_<type_value>_by__enum_key_from__<name>` — retrieves a pointer
  to a value slot (static inline).

Enum maps are used for function dispatch tables, configuration records,
and any association between an enum discriminator and a runtime value.

See: `docs/specs/util/enum_map/enum_map.h.spec.md`

### 1.3.3 Hash Map / UUID Mapped Pool (`util/hash_map/`)

Provides fixed-size pools of UUID-identified elements with O(1)
allocation, deallocation, and UUID-based dehashing. Elements must begin
with a `Serialization_Header` containing `size_of__struct` and `uuid`
fields.

Four functions are generated per instantiation (all `static inline`):

- `initialize_<name>` — configures the `Serialization_Pool` header.
- `allocate_<type_value>_from__<name>` — allocates the next free element.
- `release_<type_value>_from__<name>` — returns an element to the pool.
- `dehash_p_<type_value>_from__<name>` — looks up an element by UUID.

UUID-mapped pools are the engine's primary mechanism for managing
entities, inventories, game actions, and other UUID-identified resources.

See: `docs/specs/util/hash_map/hash_map.h.spec.md`

### 1.3.4 Getter (`util/getter/`)

Empty placeholder. No types, functions, or macros are defined. Reserved
for future getter utility functions following the same macro-generation
pattern.

See: `docs/specs/util/getter/getter.h.spec.md`

## 1.4 Cross-System Usage

The utility modules are consumed by many engine systems. Key consumers
include:

| Consumer System | Bitmap | Enum Map | UUID Mapped Pool |
|----------------|--------|----------|-----------------|
| Collision Node Pool | Allocation tracking | — | Node pool management |
| Region | Serialized chunk tracking, site presence | — | — |
| Entity Manager | — | Entity function dispatch | Entity pool |
| Hitbox Context | — | Hitbox manager invocation tables | Hitbox manager instances |
| TCP Delivery | Packet fragment tracking | — | — |
| Graphics Window Manager | — | — | Window pool |
| UI Manager | — | — | UI element pool |

## 1.5 Capacity and Performance

| Module | Time Complexity | Space Overhead |
|--------|----------------|----------------|
| Bitmap (flat) | O(1) set/get, O(N) first-set-bit | N/8 bytes |
| Bitmap (heap) | O(1) set/get, O(log₈ N) first-set-bit | ~N/7 bytes (bitmap + heap levels) |
| Enum Map | O(1) all operations | `sizeof(type_value) × enum_count` |
| UUID Mapped Pool | O(1) allocate/release/dehash (amortized) | `sizeof(Serialization_Pool) + sizeof(type_value) × pool_size` |

## 1.6 Error Handling Summary

| Module | Debug Build Behavior | Release Build Behavior |
|--------|---------------------|----------------------|
| Bitmap | `debug_error` on out-of-bounds; safe fallback | No validation; undefined behavior on out-of-bounds |
| Enum Map | `debug_error` on invalid key; returns `__None` slot or no-op | No validation; undefined behavior on invalid key |
| UUID Mapped Pool | Returns null on pool exhaustion | Returns null on pool exhaustion (no additional validation) |
