# Entity — Dynamic object abstraction with vtable dispatch

**Sources:** `core/source/entity/entity.c` + `core/source/entity/entity_manager.c` + `core/include/entity/entity.h` + `core/include/entity/entity_manager.h`

## Surface Concerns

**L3 SIMULATION module.** Entities are the engine's abstraction for dynamic objects that can exist in the world. Created and destroyed at runtime via game actions, entities carry identity (UUID-32), lifecycle (allocate/release/enable/disable), and a vtable of six function pointers for game-specific behavior. There are no predefined entity types — kinds are registered dynamically via `entity_registrar`. Called from world tick and game action managers.

- **Vtable dispatch** — Each entity holds six function pointers (`m_entity_dispose_handler`, `m_entity_update_handler`, `m_entity_enable_handler`, `m_entity_disable_handler`, `m_entity_serialize_handler`, `m_entity_deserialize_handler`) copied from the kind's function table at allocation via `sanitize_entity_functions()`. Functions may be NULL; callers check before invoking. This is the only polymorphism mechanism in the engine core.
- **Default handlers** — dispose releases the entity's sprite and AABB hitbox by UUID; enable/disable activate/deactivate the hitbox; update is NULL by design as an intentional hook for engine consumers. Which defaults are wired on which paths is documented in `entity_manager.c`.
- **Entity kinds** — The core's default enum defines `Entity_Kind__None` (the only usable kind) and `Entity_Kind__Unknown`, which is a **sentinel**: it sizes the `entity_functions[Entity_Kind__Unknown]` kind table, and `register_entity_into__entity_manager()` rejects `kind >= Entity_Kind__Unknown`. Games extend the enum via the `types/implemented/entity/entity_kind.h` override, then register each kind via `register_entity_into__entity_manager()`, adding its set of function pointers to the manager's kind table.
- **Allocation lifecycle** — Entities are allocated from a fixed-capacity pool of 128 slots. Allocation generates a UUID via the manager's repeatable pseudo-random, invokes the game-installed initializer, and copies the kind's vtable. Release invokes the dispose handler and frees the slot. Pointer-array indices are not stable across releases — prefer UUID lookups (see `entity_manager.c` comments for the allocation/removal strategy).
- **Serialization** — Entities serialize in two parts: `Serialization_Header` (UUID + branding + size) and `Entity_Data` (kind + flags). The default handlers conditionally serialize/deserialize the AABB hitbox and inventory based on flag bits. Deserialization restores the vtable via `sanitize_entity_functions()` and sets the entity as enabled.
- **Hitbox coupling** — The entity's UUID doubles as its AABB hitbox's identity, enabling UUID-based lookup (the default serialize/deserialize handlers resolve the hitbox and inventory by the entity's UUID). Note: entity allocation does **not** register the hitbox in the collision node tree. Collision-node entries are created/moved by the `game_action__hitbox` process (`poll_for_collision_node_update`, only when a hitbox crosses a global-space boundary) and by the client teleport process — a hitbox that never crosses a boundary may never get an entry, and since save iterates node entries (below), such entities are silently not serialized.
- **Process wrapping** — World save/load wraps entity (de)serialization in incremental processes, one entity per step: `m_process__serialize_entities_in__global_space` walks the global space's collision-node entry list, looking each entry's UUID up in the entity manager, then serializing and releasing the entity; `m_process__deserialize_entities_in__global_space` allocates a fresh `Entity_Kind__None` slot per step and deserializes one entity, gated on `quantity_of__file_contents` (it does not walk the collision node).

## Public API Surface

### Key Types

**`Entity`** — fixed-capacity pool of 128. Contains `_serialization_header`, `entity_data` (`Entity_Data`: kind, flags), and `entity_functions` (`Entity_Functions`: 6 function pointers).

**`Entity_Manager`** — embedded in `World`. Holds the contiguous serialization-header array, pointer array for iteration, insertion cursor, repeatable pseudo-random, kind function-pointer table, and game-installed `f_entity_initializer`.

### Key Functions

- `void initialize_entity_manager(Entity_Manager *p_entity_manager);`
- `void register_entity_into__entity_manager(Entity_Manager *p_entity_manager, Entity_Kind kind, Entity_Functions functions);`
- `void sanitize_entity_functions(Entity_Manager *p_entity_manager, Entity *p_entity);` — copies non-NULL handlers from the kind table onto the entity; runs at allocation and again during deserialization.
- `Entity *allocate_entity_with__this_uuid_in__entity_manager(Game *p_game, World *p_world, Entity_Manager *p_entity_manager, Entity_Kind kind, Identifier__u32 uuid);` — returns allocated entity or 0.
- `Entity *allocate_entity_in__entity_manager(Game *p_game, World *p_world, Entity_Manager *p_entity_manager, Entity_Kind kind);` — returns allocated entity or 0, generates UUID.
- `void release_entity_from__entity_manager(Game *p_game, World *p_world, Entity_Manager *p_manager, Entity *p_entity);`
- `void initialize_entity(Entity *p_entity, enum Entity_Kind kind);`
- `PLATFORM_Write_File_Error serialize_entity(Game *p_game, Serialization_Request *p_serialized_request, Entity *p_entity);` / `PLATFORM_Read_File_Error deserialize_entity(Game *p_game, Serialization_Request *p_serialization_request, Entity *p_entity);` — the two-part (de)serialization entry points used by the world save/load processes.
- `Entity *get_p_entity_by__uuid_from__entity_manager(Entity_Manager *p_entity_manager, Identifier__u32 uuid);` — returns entity or 0.
- `Entity *get_p_entity_by__index_from__entity_manager(Entity_Manager *p_entity_manager, Index__u32 index);` — returns entity or 0; indices are not stable across releases.
- `static inline void set_entity_as__enabled(Entity *p_entity);` / `bool is_entity__enabled(Entity *p_entity);` / `bool is_entity__allocated(Entity *p_entity);` / `Entity_Kind get_kind_of__entity(Entity *p_entity);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/entity/entity.c` | Entity init, default vtable handlers, serialization/deserialization |
| `core/source/entity/entity_manager.c` | Manager init, allocation/release, function pointer sanitization |
| `core/source/entity/implemented/entity_registrar.c` | Stub: `register_entities()` |
| `core/include/entity/entity.h` | Entity struct layout, inline helpers (enabled, allocated, kind) |
| `core/include/entity/entity_manager.h` | Manager API, inline UUID/lookup functions |
| `core/include/entity/implemented/entity_registrar.h` | Registrar header |
