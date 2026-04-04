# Specification: core/include/entity/entity.h

## Overview

Provides initialization, lifecycle handlers, serialization, and flag/state
query utilities for the `Entity` struct — the engine's fundamental game
object. Every game object (player, NPC, projectile, container, etc.) is
represented as an `Entity` allocated from the `Entity_Manager` pool.

Entities follow a component-like architecture where `Entity_Data` holds
per-instance state (kind, flags, and game-specific fields) and
`Entity_Functions` holds the function table (update, dispose, enable,
disable, serialize, deserialize). The `Entity_Data` and `Entity_Functions`
types are both implementable — game projects override them via
`types/implemented/entity_data.h` and `types/implemented/entity_functions.h`.

## Dependencies

- `defines.h` (for `Entity`, `Entity_Kind`, `Entity_Flags__u32`,
  `Entity_Data`, `Entity_Functions`, `Serialization_Header`,
  `PLATFORM_Write_File_Error`, `PLATFORM_Read_File_Error`,
  `Serialization_Request`, `PLATFORM_File_System_Context`)
- `defines_weak.h` (forward declarations for `Game`, `World`, `Entity`)
- `serialization/serialization_header.h` (for `is_serialized_struct__deallocated`)

## Types

### Entity (struct)

Defined in `defines.h`:

    typedef struct Entity_t {
        Serialization_Header            _serialization_header;
        Entity_Data                     entity_data;
        Entity_Functions                entity_functions;
    } Entity;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management. Used by `Entity_Manager` for allocation/deallocation tracking. |
| `entity_data` | `Entity_Data` | Per-instance state. Contains at minimum `the_kind_of__entity` and `entity_flags`. Game projects extend this via `types/implemented/entity_data.h`. |
| `entity_functions` | `Entity_Functions` | Function table for this entity instance. Populated from `Entity_Manager`'s registered functions on allocation or deserialization. |

### Entity_Data (struct, implementable)

Default definition (overridden by `types/implemented/entity_data.h` when
`DEFINE_ENTITY_DATA` is set):

    typedef struct Entity_Data_t {
        Entity_Kind the_kind_of__entity;
    } Entity_Data;

The provided implementable version adds `entity_flags`:

    typedef struct Entity_Data_t {
        Entity_Flags__u32               entity_flags;
        Entity_Kind                     the_kind_of__entity;
    } Entity_Data;

Game projects extend this with additional fields (hitbox references,
inventory references, health, AI state, etc.). The `the_kind_of__entity`
field must always be present.

### Entity_Functions (struct, implementable)

Default definition (overridden by `types/implemented/entity_functions.h`
when `DEFINE_ENTITY_FUNCTIONS` is set):

    typedef struct Entity_Functions_t {
        m_Entity_Handler                m_entity_dispose_handler;
        m_Entity_Handler                m_entity_update_handler;
        m_Entity_Handler                m_entity_enable_handler;
        m_Entity_Handler                m_entity_disable_handler;
        m_Entity_Serialization_Handler  m_entity_serialize_handler;
        m_Entity_Deserialization_Handler m_entity_deserialize_handler;
    } Entity_Functions;

The provided implementable version reorders and uses the same fields:

    typedef struct Entity_Functions_t {
        m_Entity_Handler    m_entity_dispose_handler;
        m_Entity_Handler    m_entity_update_handler;
        m_Entity_Handler    m_entity_disable_handler;
        m_Entity_Handler    m_entity_enable_handler;
        m_Entity_Serialization_Handler  m_entity_serialize_handler;
        m_Entity_Deserialization_Handler  m_entity_deserialize_handler;
    } Entity_Functions;

Game projects may extend this struct with additional function pointer
fields. **All fields MUST be function pointers** — undefined behavior
will occur otherwise.

| Field | Type | Signature | Description |
|-------|------|-----------|-------------|
| `m_entity_dispose_handler` | `m_Entity_Handler` | `(Entity*, Game*, World*) -> void` | Called when entity is released from pool. |
| `m_entity_update_handler` | `m_Entity_Handler` | `(Entity*, Game*, World*) -> void` | Called each game tick for active entities. |
| `m_entity_disable_handler` | `m_Entity_Handler` | `(Entity*, Game*, World*) -> void` | Called when entity transitions to disabled. |
| `m_entity_enable_handler` | `m_Entity_Handler` | `(Entity*, Game*, World*) -> void` | Called when entity transitions to enabled. |
| `m_entity_serialize_handler` | `m_Entity_Serialization_Handler` | `(Entity*, Game*, PLATFORM_File_System_Context*, World*, Serialization_Request*) -> PLATFORM_Write_File_Error` | Writes entity state to storage. |
| `m_entity_deserialize_handler` | `m_Entity_Deserialization_Handler` | `(Entity*, Game*, PLATFORM_File_System_Context*, World*, Serialization_Request*) -> PLATFORM_Read_File_Error` | Reads entity state from storage. |

### Entity_Kind (enum, implementable)

Default definition (overridden by `types/implemented/entity_kind.h` when
`DEFINE_ENTITY_KIND` is set):

    typedef enum Entity_Kind {
        Entity_Kind__None,
        Entity_Kind__Unknown
    } Entity_Kind;

`Entity_Kind__Unknown` serves as the sentinel/count value. Game projects
populate this enum with all entity types (e.g. `Entity_Kind__Player`,
`Entity_Kind__Skeleton`, etc.).

### Entity_Flags__u32 (u32)

| Flag | Bit | Description |
|------|-----|-------------|
| `ENTITY_FLAG__IS_ENABLED` | 0 | Entity is active and receiving updates. |
| `ENTITY_FLAG__IS_NOT_UPDATING_POSITION` | 1 | Skip position updates. |
| `ENTITY_FLAG__IS_NOT_UPDATING_GRAPHICS` | 2 | Skip graphics updates. |
| `ENTITY_FLAG__IS_COLLIDING` | 3 | Entity is currently colliding. |
| `ENTITY_FLAG__IS_UNLOADED` | 4 | Entity exists but is not in active memory. |
| `ENTITY_FLAG__IS_HIDDEN` | 5 | Entity is not rendered. |
| `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` | 6 | IO flag: entity has hitbox data to serialize. |
| `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` | 7 | IO flag: entity has inventory data to serialize. |
| `ENTITY_FLAG__RESERVED_0` through `ENTITY_FLAG__RESERVED_7` | 8–15 | Reserved for future engine use. |
| `ENTITY_FLAG__CUSTOM_0` through `ENTITY_FLAG__CUSTOM_15` | 16–31 | Available for game-specific use. |

Note: `IS_WITH_HITBOX__SERIALIZATION` and `IS_WITH_INVENTORY__SERIALIZATION`
are **not** reliable runtime indicators. They are only meaningful during
serialization/deserialization.

### Handler Signatures

    typedef void (*m_Entity_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            World *p_world);

    typedef PLATFORM_Write_File_Error (*m_Entity_Serialization_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
            World *p_world,
            Serialization_Request *p_serialization_request);

    typedef PLATFORM_Read_File_Error (*m_Entity_Deserialization_Handler)(
            Entity *p_entity_self,
            Game *p_game,
            PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
            World *p_world,
            Serialization_Request *p_serialization_request);

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_entity` | `(Entity*, Entity_Kind) -> void` | Initializes entity with the given kind. Sets up serialization header and entity data. |

### Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_entity_dispose_handler__default` | `(Entity*, Game*, World*) -> void` | Default dispose handler. Performs base cleanup. |
| `m_entity_enable_handler__default` | `(Entity*, Game*, World*) -> void` | Default enable handler. Sets `ENTITY_FLAG__IS_ENABLED`. |
| `m_entity_disable_handler__default` | `(Entity*, Game*, World*) -> void` | Default disable handler. Clears `ENTITY_FLAG__IS_ENABLED`. |
| `m_entity_serialization_handler__default` | `(Entity*, Game*, PLATFORM_File_System_Context*, World*, Serialization_Request*) -> PLATFORM_Write_File_Error` | Default serialization handler. Writes base entity state. |
| `m_entity_deserialization_handler__default` | `(Entity*, Game*, PLATFORM_File_System_Context*, World*, Serialization_Request*) -> PLATFORM_Read_File_Error` | Default deserialization handler. Reads base entity state. |

### Serialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `serialize_entity` | `(Game*, Serialization_Request*, Entity*) -> PLATFORM_Write_File_Error` | Writes entity to storage via the serialization request. |
| `deserialize_entity` | `(Game*, Serialization_Request*, Entity*) -> PLATFORM_Read_File_Error` | Reads entity from storage via the serialization request. |

### State Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_entity__allocated` | `(Entity*) -> bool` | `bool` | True if entity pointer is non-null and serialization header is not deallocated. |
| `is_entity__enabled` | `(Entity*) -> bool` | `bool` | True if `ENTITY_FLAG__IS_ENABLED` is set in `entity_data.entity_flags`. |
| `is_entity__serialized_with__hitbox` | `(Entity*) -> bool` | `bool` | True if `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` is set. |
| `is_entity__serialized_with__inventory` | `(Entity*) -> bool` | `bool` | True if `ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` is set. |

### State Mutation (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_entity_as__enabled` | `(Entity*) -> void` | Sets `ENTITY_FLAG__IS_ENABLED` in `entity_data.entity_flags`. |
| `set_entity_as__disabled` | `(Entity*) -> void` | Clears `ENTITY_FLAG__IS_ENABLED` in `entity_data.entity_flags`. |

### Kind Query (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_kind_of__entity` | `(Entity*) -> Entity_Kind` | `Entity_Kind` | Returns `entity_data.the_kind_of__entity`. |

### Handler Mutation (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_m_entity_update_handler_for__entity` | `(Entity*, m_Entity_Handler) -> void` | Overrides the update handler for a specific entity instance. |

## Agentic Workflow

### Entity Lifecycle

    [Deallocated] --> allocate_entity_in__entity_manager
                          |
                    initialize_entity(kind)
                    sanitize_entity_functions()
                    f_entity_initializer(game, world, entity)
                          |
                      [Allocated, Disabled]
                          |
                    m_entity_enable_handler
                          |
                      [Enabled]
                          |
                    m_entity_update_handler (each tick)
                          |
                    m_entity_disable_handler
                          |
                      [Disabled]
                          |
                    release_entity_from__entity_manager
                          |
                    m_entity_dispose_handler
                          |
                      [Deallocated]

### Allocation Pattern

Entities are never created directly. They are always allocated through
`Entity_Manager`:

    Entity *p_entity = allocate_entity_in__entity_manager(
            p_game, p_world, p_entity_manager,
            Entity_Kind__Player);
    if (!p_entity) {
        debug_error("Failed to allocate entity.");
        return;
    }

### Function Table Pattern

Entity behavior is determined by the function table registered per
`Entity_Kind` in the `Entity_Manager`. When an entity is allocated,
`sanitize_entity_functions` copies the registered function table into
the entity instance. This means:

1. Register functions once at startup via
   `register_entity_into__entity_manager`.
2. All entities of the same kind share the same initial function table.
3. Individual entities can override specific handlers after allocation
   (e.g. `set_m_entity_update_handler_for__entity`).

### Implementable Types Pattern

`Entity_Data`, `Entity_Functions`, and `Entity_Kind` are all
**implementable types**. The engine provides minimal defaults, and game
projects override them by:

1. Creating a file at `types/implemented/entity_data.h` (or
   `entity_functions.h`, `entity_kind.h`).
2. Defining the guard macro (`DEFINE_ENTITY_DATA`, `DEFINE_ENTITY_FUNCTIONS`,
   `DEFINE_ENTITY_KIND`) before the struct/enum definition.
3. The `#ifndef DEFINE_ENTITY_DATA` guard in `defines.h` skips the
   default and uses the game project's definition.

For `Entity_Functions`, the implementable header notes:

> NOTE: All fields MUST be function pointers — undefined behavior will
> occur otherwise!

This constraint exists because the engine may perform bulk operations
on the function table assuming uniform pointer-sized fields.

### Serialization IO Flags

The `ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION` and
`ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION` flags are **only**
meaningful during IO operations. They tell the serialization system
which optional components to read/write. They are **not** reliable
indicators of whether an entity currently has a hitbox or inventory
at runtime.

### Preconditions

- `is_entity__allocated`: `p_entity` may be null (returns false).
- All other `static inline` functions: `p_entity` must be non-null.
  No debug guards are present in these functions — the caller is
  responsible for null checks.
- `initialize_entity`: `p_entity` must point to valid memory (typically
  from the `Entity_Manager` pool).

### Postconditions

- After `initialize_entity`: entity has the given kind set, flags are
  cleared, serialization header is initialized.
- After `set_entity_as__enabled`: `is_entity__enabled` returns true.
- After `set_entity_as__disabled`: `is_entity__enabled` returns false.

### Error Handling

- `is_entity__allocated` gracefully handles null by returning false.
- Serialization functions return `PLATFORM_Write_File_Error` or
  `PLATFORM_Read_File_Error` enums to indicate success or failure.
- No `debug_abort` calls in `entity.h` inline functions. Null pointer
  protection is the caller's responsibility (typically done in
  `entity_manager.h`).
