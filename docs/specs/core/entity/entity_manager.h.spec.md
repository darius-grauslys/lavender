# 1 Specification: core/include/entity/entity_manager.h

## 1.1 Overview

Provides pool-based allocation, deallocation, function table registration,
and lookup utilities for `Entity` instances. The `Entity_Manager` owns a
fixed-size array of `Entity` structs and a parallel pointer array for
indexed access. It is the sole mechanism for creating and destroying
entities in the engine.

The `Entity_Manager` also maintains a per-`Entity_Kind` function table
registry. When an entity is allocated or deserialized, its function table
is populated from this registry via `sanitize_entity_functions`.

## 1.2 Dependencies

- `defines.h` (for `Entity`, `Entity_Manager`, `Entity_Kind`,
  `Entity_Functions`, `Identifier__u32`, `MAX_QUANTITY_OF__ENTITIES`)
- `defines_weak.h` (forward declarations for `Game`, `World`)
- `entity/entity.h` (for `get_kind_of__entity`)
- `platform_defines.h` (for platform-specific limits)
- `serialization/hashing.h` (for `dehash_identitier_u32_in__contigious_array`)
- `debug/debug.h` (for `debug_error`, `debug_abort` in debug builds)

Note: This header unconditionally includes `debug/debug.h`, unlike most
headers which only include it via `defines.h` when `NDEBUG` is not defined.
The debug guards within the inline functions still use `#ifndef NDEBUG`.

## 1.3 Types

### 1.3.1 Entity_Manager (struct)

Defined in `defines.h`:

    typedef struct Entity_Manager_t {
        Entity entities[MAX_QUANTITY_OF__ENTITIES];
        Entity *ptr_array_of__entities[MAX_QUANTITY_OF__ENTITIES];
        Entity_Functions entity_functions[Entity_Kind__Unknown];
        Repeatable_Psuedo_Random randomizer;
        Entity **p_ptr_entity__next_in_ptr_array;
        f_Entity_Initializer f_entity_initializer;
    } Entity_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `entities` | `Entity[MAX_QUANTITY_OF__ENTITIES]` | Fixed-size pool of entity instances. |
| `ptr_array_of__entities` | `Entity*[MAX_QUANTITY_OF__ENTITIES]` | Pointer array for indexed iteration. Compacted as entities are allocated and released. |
| `entity_functions` | `Entity_Functions[Entity_Kind__Unknown]` | Per-kind function table registry. Indexed by `Entity_Kind`. |
| `randomizer` | `Repeatable_Psuedo_Random` | PRNG for UUID generation during allocation. |
| `p_ptr_entity__next_in_ptr_array` | `Entity**` | Points to the next available slot in `ptr_array_of__entities`. |
| `f_entity_initializer` | `f_Entity_Initializer` | Game-provided callback invoked after allocation to perform game-specific entity setup. |

### 1.3.2 f_Entity_Initializer (function pointer)

    typedef void (*f_Entity_Initializer)(
            Game *p_game,
            World *p_world,
            Entity *p_entity);

Called after an entity is allocated and its function table is set.
Used by game projects to perform kind-specific initialization (e.g.
setting up hitboxes, sprites, AI state).

### 1.3.3 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__ENTITIES` | Platform-defined | Maximum number of entities in the pool. Defined in `platform_defines.h`. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_entity_manager` | `(Entity_Manager*) -> void` | Initializes the entity pool, pointer array, randomizer, and clears all registered function tables. |

### 1.4.2 Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_entity_into__entity_manager` | `(Entity_Manager*, Entity_Kind, Entity_Functions) -> void` | Registers a function table for the given `Entity_Kind`. All subsequently allocated entities of this kind will receive this function table. |
| `sanitize_entity_functions` | `(Entity_Manager*, Entity*) -> void` | Copies the registered function table for the entity's kind into the entity instance. Called on allocation and deserialization to ensure the entity has correct handlers. |

### 1.4.3 Default Initializer

| Function | Signature | Description |
|----------|-----------|-------------|
| `f_entity_initializer__default` | `(Game*, World*, Entity*) -> void` | Default entity initializer. Used when no game-specific initializer is set. |

### 1.4.4 Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_entity_in__entity_manager` | `(Game*, World*, Entity_Manager*, Entity_Kind) -> Entity*` | `Entity*` or null | Allocates an entity from the pool with an auto-generated UUID. Returns null on pool exhaustion. Calls `sanitize_entity_functions` and `f_entity_initializer`. |
| `allocate_entity_with__this_uuid_in__entity_manager` | `(Game*, World*, Entity_Manager*, Entity_Kind, Identifier__u32) -> Entity*` | `Entity*` or null | Allocates an entity with a specific UUID. Used during deserialization to restore entities with their original identifiers. |

### 1.4.5 Deallocation

| Function | Signature | Description |
|----------|-----------|-------------|
| `release_entity_from__entity_manager` | `(Game*, World*, Entity_Manager*, Entity*) -> void` | Releases an entity back to the pool. Invokes `m_entity_dispose_handler` before deallocation. |

### 1.4.6 Lookup (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_entity_by__uuid_from__entity_manager` | `(Entity_Manager*, Identifier__u32) -> Entity*` | `Entity*` or null | Looks up an entity by UUID using `dehash_identitier_u32_in__contigious_array` over the contiguous `entities[]` pool. |
| `get_p_entity_by__index_from__entity_manager` | `(Entity_Manager*, Index__u32) -> Entity*` | `Entity*` or null | Returns the entity at the given index in the pointer array. Bounds-checked in debug builds. |

### 1.4.7 Configuration (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_entity_initializer_in__entity_manager` | `(Entity_Manager*, f_Entity_Initializer) -> void` | Sets the game-specific entity initializer callback. |
| `set_entity_functions` | `(Entity_Manager*, Entity*) -> void` | Copies the registered function table for the entity's kind into the entity. Debug builds validate that the entity kind is less than `Entity_Kind__Unknown`. |

## 1.5 Agentic Workflow

### 1.5.1 Entity Registration Pattern

At game startup, register function tables for every `Entity_Kind`:

    Entity_Functions player_functions = {
        .m_entity_dispose_handler = m_player_dispose,
        .m_entity_update_handler  = m_player_update,
        .m_entity_enable_handler  = m_player_enable,
        .m_entity_disable_handler = m_player_disable,
        .m_entity_serialize_handler   = m_player_serialize,
        .m_entity_deserialize_handler = m_player_deserialize,
    };
    register_entity_into__entity_manager(
            &p_world->entity_manager,
            Entity_Kind__Player,
            player_functions);

    set_entity_initializer_in__entity_manager(
            &p_world->entity_manager,
            my_game__entity_initializer);

### 1.5.2 Allocation Flow

    allocate_entity_in__entity_manager(game, world, manager, kind)
        1. Find free slot in entities[] pool
        2. Generate UUID via randomizer
        3. initialize_entity(p_entity, kind)
        4. sanitize_entity_functions(manager, p_entity)
           -> copies entity_functions[kind] into p_entity
        5. f_entity_initializer(game, world, p_entity)
           -> game-specific setup (hitbox, sprite, etc.)
        6. Insert into ptr_array_of__entities
        7. Return p_entity

### 1.5.3 Deallocation Flow

    release_entity_from__entity_manager(game, world, manager, entity)
        1. Invoke entity->entity_functions.m_entity_dispose_handler
        2. Deallocate serialization header (marks slot as free)
        3. Remove from ptr_array_of__entities (compact)

### 1.5.4 UUID Lookup Pattern

Entities are identified by UUID throughout the engine. To find an entity:

    Entity *p_entity = get_p_entity_by__uuid_from__entity_manager(
            &p_world->entity_manager,
            target_uuid);
    if (!p_entity) {
        debug_warning("Entity not found: %d", target_uuid);
        return;
    }

This uses `dehash_identitier_u32_in__contigious_array` which performs
a hash-based lookup over the contiguous `entities[]` array.

### 1.5.5 Index Iteration Pattern

To iterate over all active entities:

    for (Index__u32 i = 0; i < MAX_QUANTITY_OF__ENTITIES; i++) {
        Entity *p_entity = get_p_entity_by__index_from__entity_manager(
                &p_world->entity_manager, i);
        if (!is_entity__allocated(p_entity)) continue;
        if (!is_entity__enabled(p_entity)) continue;
        // ... process entity ...
    }

**Warning**: The entity at a given index may change between frames.
Do not cache index-based references. Use UUIDs for persistent references.

### 1.5.6 Deserialization Pattern

When loading entities from storage, use the UUID-specific allocator
to preserve identity:

    Entity *p_entity = allocate_entity_with__this_uuid_in__entity_manager(
            p_game, p_world, p_entity_manager,
            deserialized_kind,
            deserialized_uuid);
    // sanitize_entity_functions is called internally
    // then deserialize remaining entity state...

### 1.5.7 Debug Guard Pattern

The `entity_manager.h` inline functions use `debug_error` (not
`debug_abort`) for most error conditions, allowing graceful degradation
rather than halting execution:

    // In set_entity_functions:
    #ifndef NDEBUG
        if (get_kind_of__entity(p_entity)
                >= Entity_Kind__Unknown) {
            debug_error("set_entity_functions, invalid entity kind.");
            return;
        }
    #endif

    // In get_p_entity_by__index_from__entity_manager:
    #ifndef NDEBUG
        if (!p_entity_manager) {
            debug_error("p_entity_manager == 0.");
            return 0;
        }
        if (index_of__entity >= MAX_QUANTITY_OF__ENTITIES) {
            debug_error("get_p_entity_by__index_from__entity_manager, index out of bounds.");
            return 0;
        }
    #endif

This differs from `process.h` which uses `debug_abort` for null pointer
guards. The entity manager prefers `debug_error` to allow continued
execution where possible.

### 1.5.8 Relationship to World

The `Entity_Manager` is owned by `World`:

    typedef struct World_t {
        ...
        Entity_Manager entity_manager;
        ...
    } World;

The higher-level `allocate_entity_into__world` function (declared in
`world/world.h`) wraps `allocate_entity_in__entity_manager` with
world-level bookkeeping.

### 1.5.9 Preconditions

- `initialize_entity_manager`: `p_entity_manager` must be non-null.
- `register_entity_into__entity_manager`: `the_kind_of__entity` must
  be less than `Entity_Kind__Unknown`.
- `allocate_entity_in__entity_manager`: pool must have available slots.
- `release_entity_from__entity_manager`: `p_entity` must be a valid,
  allocated entity from this manager's pool.
- `get_p_entity_by__index_from__entity_manager`: `index_of__entity`
  must be less than `MAX_QUANTITY_OF__ENTITIES` (debug-checked).
- `set_entity_functions`: entity kind must be less than
  `Entity_Kind__Unknown` (debug-checked).

### 1.5.10 Postconditions

- After `allocate_entity_in__entity_manager`: returned entity is
  initialized, has correct function table, and `is_entity__allocated`
  returns true. Returns null on failure.
- After `release_entity_from__entity_manager`: entity slot is free,
  `is_entity__allocated` returns false, dispose handler has been called.
- After `sanitize_entity_functions` / `set_entity_functions`: entity's
  `entity_functions` matches the registered table for its kind.

### 1.5.11 Error Handling

- Pool exhaustion: `allocate_entity_in__entity_manager` returns null.
- Invalid kind: `set_entity_functions` calls `debug_error` and returns
  without modifying the entity.
- Null manager: `get_p_entity_by__index_from__entity_manager` calls
  `debug_error` and returns null.
- Out of bounds index: `get_p_entity_by__index_from__entity_manager`
  calls `debug_error` and returns null.

### 1.5.12 Thread Safety

Entity operations are **not** thread-safe. The engine's cooperative
scheduling model (see `process.h` specification) ensures all entity
operations occur on a single thread.
