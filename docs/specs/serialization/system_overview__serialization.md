# System Overview: Serialization Infrastructure

## Purpose

The serialization system provides the foundational identity, pooling, hashing,
reference-linking, I/O request management, and file persistence mechanisms used
throughout the engine. Every pooled struct in the engine embeds a
`Serialization_Header` (or `Serialization_Header__UUID_64`) as its first field,
enabling uniform UUID-based identification, O(1) average-case lookup via
hashing, and serializable cross-references between objects.

## Architecture

### Data Hierarchy

    Engine
    +-- Serialization_Header / Serialization_Header__UUID_64
    |   (Embedded as first field of every pooled struct)
    |
    +-- Identifiers (UUID generation and validation)
    |   +-- get_random__uuid_u32 / get_random__uuid_u64
    |   +-- is_identifier_u32__invalid / is_identifier_u64__invalid
    |   +-- merge_identifiers_u32
    |
    +-- Hashing (UUID-to-index mapping for contiguous arrays)
    |   +-- poll_for__uuid_collision (linear probing)
    |   +-- dehash_identitier_u32_in__contigious_array (lookup)
    |   +-- allocate_serialization_header* (combined find + allocate)
    |   +-- has_uuid_in__contiguous_array (existence check)
    |
    +-- Serialization_Pool (thin wrapper over contiguous arrays)
    |   +-- initialize_serialization_pool
    |   +-- allocate_from__serialization_pool
    |   +-- release_from__serialization_pool
    |   +-- dehash_from__serialization_pool
    |
    +-- Serialized_Field (soft pointer / deferred reference)
    |   +-- identifier_for__serialized_field (UUID)
    |   +-- p_serialized_field__data (live pointer)
    |   +-- link_serialized_field_against__contiguous_array
    |
    +-- Serialization_Request (in-flight I/O or TCP operation)
    |   +-- p_data, p_file_handler / p_tcp_packet_destination
    |   +-- serialization_request_flags
    |   +-- activate / deactivate lifecycle
    |
    +-- Game_Directory (file system persistence)
        +-- stat_game_data_file
        +-- save_game
        +-- append_path

### Module Relationships

    +-------------------+
    | Serialization     |
    | Header            |<----- Embedded in all pooled structs
    | (32-bit / 64-bit) |       (Entity, Hitbox_AABB, UI_Element,
    +--------+----------+        Chunk, Global_Space, Collision_Node,
             |                   Graphics_Window, Game_Action, etc.)
             |
    +--------v----------+       +-------------------+
    |   Identifiers     |<------| Repeatable_       |
    | (UUID generation) |       | Psuedo_Random     |
    +--------+----------+       +-------------------+
             |
    +--------v----------+
    |     Hashing       |
    | (modular hash +   |
    |  linear probing)  |
    +--------+----------+
             |
    +--------v----------+       +-------------------+
    | Serialization_Pool|       | Serialized_Field  |
    | (pool wrapper)    |       | (soft pointer)    |
    +-------------------+       +--------+----------+
                                         |
                                         | links against
                                         v
                                  contiguous arrays of
                                  Serialization_Header

    +-------------------+       +-------------------+
    | Serialization_    |<------| PLATFORM_File_    |
    | Request           |       | System_Context    |
    | (I/O lifecycle)   |       | (platform pool)   |
    +-------------------+       +-------------------+

    +-------------------+
    | Game_Directory    |-------> PLATFORM_* file I/O
    | (persistence)     |
    +-------------------+

### Key Types

| Type | Role |
|------|------|
| `Serialization_Header` | 32-bit UUID identity header. First field of most pooled structs. Enables UUID-based hashing, allocation tracking, and contiguous array traversal. |
| `Serialization_Header__UUID_64` | 64-bit UUID variant. Used for types requiring larger identity space (chunks, global spaces, collision nodes). |
| `Identifiers` (module) | Generates random 32-bit and 64-bit UUIDs via the engine's deterministic PRNG. Provides validation utilities. |
| `Hashing` (module) | Maps UUIDs to array indices via modular hashing with linear probing. Provides allocation, lookup, and existence checks on contiguous arrays. |
| `Serialization_Pool` | Thin wrapper storing pool metadata (element count, element size, base pointer). Delegates to hashing for UUID operations. |
| `Serialized_Field` | A "soft pointer" storing both a UUID and a data pointer. Enables serializable references between pooled objects with deferred linking. |
| `Serialization_Request` | Represents an in-flight I/O or TCP transfer. Tracks data pointer, file/TCP handler, and state flags. Pooled per-platform. |
| `Serialization_Request_Flags` | 8-bit bitmask tracking request state (allocated, active, read/write, keep-alive, TCP/IO mode). |
| `Game_Directory` (module) | File system utilities for checking, saving, and constructing paths for game data persistence. |

### Limits and Sentinels

| Constant | Value | Description |
|----------|-------|-------------|
| `IDENTIFIER__UNKNOWN__u32` | `(uint32_t)(-1)` | Sentinel for deallocated or invalid 32-bit UUID. |
| `IDENTIFIER__UNKNOWN__u64` | `(uint64_t)(-1)` | Sentinel for deallocated or invalid 64-bit UUID. |
| `MAX_LENGTH_OF__IO_PATH` | 128 (default) | Maximum character length of file system paths. |

## Subsystem: Serialization Header

### Purpose

`Serialization_Header` and `Serialization_Header__UUID_64` are the universal
identity mechanism for pooled structs. By embedding the header as the first
field, any struct pointer can be cast to a header pointer for generic
operations.

### Key Properties

- **`size_of__struct`**: Byte size of the owning struct. Enables pointer
  arithmetic across contiguous arrays (stride = `size_of__struct`).
- **`uuid`**: The struct's unique identifier. `IDENTIFIER__UNKNOWN__u32`
  (or `__u64`) indicates a deallocated slot.

### UUID Branding

UUIDs can encode metadata via branding:

    Bits [31..26]: Lavender_Type (6 bits)
    Bits [25..20]: Index (6 bits)
    Bits [19..0]:  Random / unique portion

This allows type information to be recovered from a UUID without accessing
the struct itself.

### Contiguous Array Model

All pools in the engine are contiguous arrays of identically-sized structs.
The header's `size_of__struct` field enables index-based access:

    Serialization_Header *p_element =
        (Serialization_Header*)((u8*)p_base + index * p_base->size_of__struct);

This model is used by the hashing module, serialization pool, and serialized
field linking.

### Representative Consumers (32-bit)

- `Entity._serialization_header`
- `Hitbox_AABB._serialization_header`
- `Hitbox_Manager_Instance._serialization_header`
- `UI_Element._serialization_header`
- `Graphics_Window._serialization_header`
- `Game_Action._serialiation_header`

### Representative Consumers (64-bit)

- `Chunk._serialization_header`
- `Global_Space._serialization_header`
- `Collision_Node._serialization_header`

## Subsystem: Identifiers

### Purpose

Generates random UUIDs and provides validation. UUIDs are the primary identity
mechanism for all pooled structs.

### UUID Generation Strategy

- **32-bit**: XOR a pseudo-random value with `IDENTIFIER__UNKNOWN__u32`. This
  guarantees the result is never equal to the sentinel. Uses intrusive
  randomization (advances the PRNG seed).
- **64-bit**: Combine two 32-bit pseudo-random values and XOR with
  `IDENTIFIER__UNKNOWN__u64`. Uses non-intrusive randomization (does not
  advance the seed).

### Intrusive vs Non-Intrusive Randomization

| Variant | Function | Seed Effect |
|---------|----------|-------------|
| 32-bit | `get_random__uuid_u32` | Advances seed (intrusive) |
| 64-bit | `get_random__uuid_u64` | Does not advance seed (non-intrusive) |

This distinction matters when deterministic replay or reproducible allocation
order is required.

### Collision Handling

UUID collisions are theoretically possible but unlikely. The XOR with the
sentinel prevents the most common collision (generating the sentinel itself).
For contiguous array placement, collisions are resolved by the hashing module's
linear probing.

## Subsystem: Hashing

### Purpose

Maps UUIDs to array indices for O(1) average-case access to pooled resources.
This is the core lookup and allocation mechanism for contiguous arrays.

### Algorithm

1. **Initial index**: `uuid % array_length`
2. **Collision resolution**: Linear probing. If the slot at the initial index
   is occupied by a different UUID, advance to the next slot (wrapping).
3. **Termination**: Stop when a matching UUID or a deallocated slot is found,
   or when the entire array has been probed.

### Performance

- **O(1) average case** for lookup and allocation when the array is not
  heavily loaded.
- **O(n) worst case** when the array is nearly full.
- Arrays should be sized to avoid high load factors. In practice, pool sizes
  are fixed at compile time and matched to expected usage.

### Function Categories

| Category | Functions | Description |
|----------|-----------|-------------|
| Collision Resolution | `poll_for__uuid_collision`, `__uuid_64` | Linear probe for matching or free slot. |
| UUID Availability | `get_next_available__uuid_in__contiguous_array`, `__uuid_64` | Find a UUID that won't collide. |
| Lookup | `dehash_identitier_u32_in__contigious_array`, `__u64` | Resolve UUID to struct pointer. |
| Allocation (slot only) | `get_next_available__allocation_in__contiguous_array`, `__u64` | Find free slot without setting UUID. |
| Allocation (combined) | `allocate_serialization_header*` variants | Find slot AND set UUID. |
| Random Allocation | `get_next_available__random_uuid_in__contiguous_array` variants | Generate random UUID and resolve. |
| Existence Check | `has_uuid_in__contiguous_array`, `__uuid_64` | Boolean existence test. |
| Index Computation | `bound_uuid_to__contiguous_array`, `__uuid_64` | Compute `uuid % length`. |

### Relationship to Other Subsystems

- **Identifiers**: Hashing uses identifier generation for random allocation
  functions.
- **Serialization Header**: Hashing operates on contiguous arrays of headers,
  using `size_of__struct` for stride and `uuid` for matching.
- **Serialization Pool**: The pool wrapper delegates to hashing for
  `dehash_from__serialization_pool`.

## Subsystem: Serialization Pool

### Purpose

A thin wrapper around contiguous arrays, abstracting pool initialization,
allocation, deallocation, and UUID-based lookup. Stores array metadata
(element count, element size, base pointer) and delegates to the hashing
module.

### Lifecycle

1. **Declare** the backing array and `Serialization_Pool` struct externally.
2. **Initialize** with `initialize_serialization_pool(...)`. All headers are
   set to deallocated.
3. **Allocate** elements with `allocate_from__serialization_pool` (sequential
   scan) or `allocate_by_hash_in__serialization_pool` (hash-based).
4. **Lookup** elements with `dehash_from__serialization_pool`.
5. **Release** elements with `release_from__serialization_pool`.

### When to Use

Use `Serialization_Pool` for generic pool management. Specialized managers
(e.g. `Hitbox_AABB_Manager`, `Entity_Manager`) typically implement their own
pool logic directly rather than using `Serialization_Pool`.

## Subsystem: Serialized Field

### Purpose

Provides a "soft pointer" mechanism for serializable references between pooled
objects. A `Serialized_Field` stores both a UUID and a data pointer, enabling
deferred linking: the UUID is persisted during serialization, and the pointer
is resolved against a contiguous array after deserialization.

### Serialization Pattern

    Save:
        Serialized_Field holds UUID + live pointer.
        Only the UUID is written to disk.

    Load:
        Serialized_Field is initialized as "unlinked" (UUID set, pointer null).

    Resolution:
        link_serialized_field_against__contiguous_array() resolves
        the UUID back to a live pointer by scanning the target pool.

### Typed Aliases

| Alias | Semantic Meaning |
|-------|------------------|
| `Serialized_Item_Stack_Ptr` | References an `Item_Stack` |
| `Serialized_Inventory_Ptr` | References an `Inventory` |
| `Serialized_Entity_Ptr` | References an `Entity` |
| `Serialized_Chunk_Ptr` | References a `Chunk` |

### Validation

- `is_p_serialized_field__linked` checks that the data pointer is non-null,
  the pointed-to struct has a valid UUID, and the UUIDs match.
- `is_serialized_field_matching__serialization_header` compares the field's
  UUID against a given header. Debug-aborts on null in debug builds.

## Subsystem: Serialization Request

### Purpose

Represents an in-flight I/O or TCP transfer operation. A request tracks a data
pointer, a file handler (for disk I/O) or TCP packet destination (for network),
and a set of flags describing its current state.

### Modes

| Mode | Selected By | Key Fields |
|------|-------------|------------|
| File I/O | `SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO` clear | `p_file_handler`, `quantity_of__file_contents` |
| TCP | `SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO` set | `p_tcp_packet_destination`, `pM_packet_bitmap`, `quantity_of__bytes_in__destination`, `quantity_of__tcp_packets__anticipated` |

### Lifecycle

    1. Allocate   -- PLATFORM_allocate_serialization_request
    2. Initialize -- initialize_serialization_request (zeroes all fields)
    3. Configure  -- Set flags (read/write, tcp/io, keep_alive)
    4. Activate   -- activate_serialization_request
                     (for TCP: allocates pM_packet_bitmap)
    5. Use        -- Driven by serialization process or platform I/O
    6. Deactivate -- deactivate_serialization_request
                     (TCP: frees bitmap; I/O: closes file)
    7. Release    -- PLATFORM_release_serialization_request

### Flags

| Flag | Bit | Description |
|------|-----|-------------|
| `IS_ALLOCATED` | 0 | Slot is allocated from platform pool. |
| `IS_ACTIVE` | 1 | Request is currently in-flight. |
| `USE_SERIALIZER_OR_BUFFER` | 2 | Selects serializer vs raw buffer mode. |
| `READ_OR_WRITE` | 3 | Set = reading, clear = writing. |
| `KEEP_ALIVE` | 4 | Set = persists after completion, clear = fire-and-forget. |
| `IS_TCP_OR_IO` | 5 | Set = TCP mode, clear = file I/O mode. |

### Platform Integration

Serialization requests are pooled per-platform in
`PLATFORM_File_System_Context`. Platform functions manage the pool:

- `PLATFORM_allocate_serialization_request`
- `PLATFORM_release_serialization_request`
- `PLATFORM_get_quantity_of__active_serialization_requests`

### Error Handling

- `activate_serialization_request` returns false if TCP bitmap allocation
  fails.
- Calling `activate_serialization_request` twice without an intervening
  `deactivate_serialization_request` causes a memory leak.

## Subsystem: Game Directory

### Purpose

File system utilities for game data persistence. Handles checking for save
files, saving game state, and constructing file paths.

### Functions

| Function | Description |
|----------|-------------|
| `stat_game_data_file` | Checks for existence of the game data file. Returns a status code. |
| `save_game` | Saves current game state. **Must only be called from the main menu.** |
| `append_path` | Concatenates two `IO_path` buffers in-place. |

### Platform Integration

Game directory operations rely on platform-provided file I/O functions:

- `PLATFORM_get_base_directory`
- `PLATFORM_append_base_directory_to__path`
- `PLATFORM_open_file`
- `PLATFORM_write_file`
- `PLATFORM_read_file`
- `PLATFORM_close_file`
- `PLATFORM_access`
- `PLATFORM_mkdir`

The path separator character is defined in `platform_defaults.h` as
`PATH_SEPERATOR` (defaults to `'/'`).

## Cross-Cutting Concerns

### Preconditions (All Subsystems)

- `Serialization_Header` must be the **first field** of any struct that uses
  it. Pointer arithmetic and casting depend on this layout.
- `size_of__struct` must be correctly set in every header before any
  contiguous array operations.
- Contiguous arrays must be initialized with
  `initialize_serialization_header__contiguous_array` before any hashing
  operations.
- UUIDs passed to allocation functions must not be `IDENTIFIER__UNKNOWN__u32`
  (or `__u64`).
- `Repeatable_Psuedo_Random` must be initialized and seeded before UUID
  generation.

### Error Handling Patterns

| Subsystem | Error Condition | Behavior |
|-----------|-----------------|----------|
| Hashing | Array full | Returns `NULL` or `IDENTIFIER__UNKNOWN__u32` |
| Serialization Pool | Pool full | `allocate_from__serialization_pool` returns `NULL` |
| Serialization Pool | UUID not found | `dehash_from__serialization_pool` returns `NULL` |
| Serialized Field | UUID not found in array | `link_serialized_field_against__contiguous_array` returns false |
| Serialized Field | Null argument | `debug_abort` in debug builds |
| Serialization Request | TCP bitmap alloc failure | `activate_serialization_request` returns false |
| Serialization Header | Null pointer | `is_serialized_struct__deallocated` safely returns true |
| Serialization Header | Null pointer | `is_identifier_u32_matching__serialization_header` calls `debug_abort` |

### Thread Safety

The serialization system does not provide internal synchronization. All
operations assume single-threaded access or external synchronization by the
caller.

## Integration with Other Engine Systems

The serialization infrastructure is consumed by virtually every engine
subsystem:

| Consumer | Usage |
|----------|-------|
| Entity system | Entities are pooled with `Serialization_Header`. Entity references use `Serialized_Entity_Ptr`. |
| Collision system | `Collision_Node` and `Global_Space` use `Serialization_Header__UUID_64`. Collision node entries reference hitboxes by UUID. |
| Hitbox system | `Hitbox_AABB` and `Hitbox_Manager_Instance` use `Serialization_Header`. Hitbox pools use hashing for UUID-based lookup. |
| UI system | `UI_Element` uses `Serialization_Header`. UI managers use hashing for element lookup. |
| Graphics system | `Graphics_Window` and `PLATFORM_Texture` use `Serialization_Header`. |
| Inventory system | Inventories and item stacks use `Serialization_Header`. Cross-references use `Serialized_Inventory_Ptr` and `Serialized_Item_Stack_Ptr`. |
| Game Action system | `Game_Action` uses `Serialization_Header`. |
| World persistence | `Game_Directory` and `Serialization_Request` manage save/load operations. |
| Chunk system | Chunks use `Serialization_Header__UUID_64`. Chunk references use `Serialized_Chunk_Ptr`. |
