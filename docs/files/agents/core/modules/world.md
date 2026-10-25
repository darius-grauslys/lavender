# World — 3D tile-based spatial simulation

**Sources:** `core/source/world/world.c` + `core/include/world/world.h`

## Surface Concerns

The World is the engine's spatial model — a 3D tile-based world partitioned into global and local spaces, chunks, tiles, and regions. It owns the spatial hierarchy that determines what data is loaded, where entities are, which tiles exist, and what the camera sees. `manage_world()` is the per-tick entry point, called from the game layer's frame loop (e.g. the NDS game scene), not from core's `Game`.

- **Space management** — Global spaces (indexed by chunk vector, UUID-64 hashed, managed by Global_Space_Manager) and local spaces (a per-client 8×8×1 sliding window of slots pointing into global spaces). Reference counting via `hold_global_space()` / `drop_global_space()`. Each tick, every client's window scrolls to that client's hitbox position (an outdated `#warning` in world.c still mentions camera-based scrolling).
- **Chunk pool** — Contiguous array of `Chunk` structs keyed by UUID-64. Each chunk holds 128 tiles (8×8×2) in a linear 3D layout. Allocated/deallocated via serialization header system.
- **Chunk generation** — Function-pointer table keyed by `Chunk_Generator_Kind`. Games register generators via `register_chunk_generator_into__chunk_generator_table()`. Populated during world init.
- **Regions** — Higher-level partition above chunks for serialization tracking. Bitmap tracking of serialized chunks with wrap-around for negative coordinates. Partially stubbed: `is_structure_within__region()` aborts, `set_center_of__region_manager()`'s loop is unimplemented, and container serialization in global space (`m_process__serialize_containers_in__global_space`) is fully commented out.
- **Tiles** — Smallest spatial unit. `Tile_Kind` enum; game-defined kinds live between `None` and `Unknown`. Passability, sight-blocking, height, and ground presence defined via `Tile_Logic_Context`.
- **Tile logic context** — Maps tile layers to dynamically-allocated `Tile_Logic_Record` arrays. Provides inline helpers: `poll__is_tile__unpassable()`, `poll__is_tile__sight_blocking()`, etc. Only heap allocation in world beyond World itself.
- **Camera** — Position (fixed-point), fulcrum, z-near/far planes, handler function pointer. The default handler is a no-op; `set_camera_to__follow()` installs a handler that tracks a hitbox by UUID. `is_camera__active()` validates all parameters.
- **Entity tick hook** — `manage_world` calls each enabled entity's `m_entity_update_handler`; core provides no default, per-tick entity behavior is entirely game-defined.
- **Fixed-capacity pools** — `QUANTITY_OF__GLOBAL_SPACE = 256` (4 clients × 64 local spaces) bounds global spaces, chunks, and collision nodes; `Collision_Node_Pool` also holds 256 hitbox entries.
- **UUID identity** — `Global_Space`, `Chunk`, and `Collision_Node` are UUID-64 hashed, looked up via `dehash_identitier_u64_in__contigious_array()`. Entities use UUID-32.
- **Game-action protocol** — World mutation via game actions: `game_action__global_space__request` (load), `game_action__global_space__store` (save), `game_action__world__load_world` (full load). Serialization runs through process-wrapped filesystem I/O.

## Public API Surface

### Key Types

**`World`** — heap-allocated, referenced from `Game.pM_world`. Key members:
- `_serialization_header`
- `repeatable_pseudo_random` (typo: struct named `Repeatable_Psuedo_Random`)
- `name` (char[32]), `length_of__world_name`
- `region_manager`, `structure_manager` (embedded; stubbed)
- `entity_manager`, `global_space_manager`, `chunk_pool`, `chunk_generator_table` (embedded managers)
- `collision_node_pool`, `tile_logic_context`, `inventory_manager`, `item_manager` (embedded)
- `camera` (embedded `Camera`)
- `p_graphics_window_for__world`
- `spawn_point` (`Vector__3i32F4`)
- `f_hitbox_aabb_tile_touch_handler`, `f_hitbox_aabb_collision_handler` (core defaults installed at world init; game-overridable)
- `f_tile_render_kernel` (game/backend-installed rendering callback)

### Key Functions

- `void initialize_world(Game *p_game, World *p_world);`
- `void manage_world(Game *p_game);` — fixed tick order: collision resolve → hitbox movement → entity update → per-client local-space scrolling (hitbox-driven).
- `bool poll_world_for__scrolling(Game *p_game, World *p_world, Graphics_Window *p_gfx_window);` — returns bool. Stubbed (calls `debug_abort`).
- `Process *load_world(Game *p_game);` — returns process or 0 on failure.
- `void save_world(PLATFORM_File_System_Context *p_PLATOFRM_file_system_context, World *p_world);` — stubbed (calls `debug_abort`). Typo: `PLATOFRM` in the header's parameter name.
- `Entity *get_p_entity_from__world_using__3i32F4(Game *p_game, World *p_world, Vector__3i32F4 position__3i32F4);` — returns entity or 0.
- `void set_name_of__world(World *p_world, World_Name_String name_of__world);`
- `bool poll_for_collision_node_update(Game *p_game, Vector__3i32F4 position_old, Vector__3i32F4 position_new, Identifier__u32 uuid_u32_of__entry);` — returns bool.

## Key Files Table

| File | Role |
|------|------|
| `core/source/world/world.c` | World init, manage_world tick, entity iteration, serialization processes |
| `core/source/world/global_space.c` | Global space lifecycle, serialization/deserialization state machines |
| `core/source/world/global_space_manager.c` | Global space allocation/deallocation by chunk vector, tile lookup |
| `core/source/world/local_space_manager.c` | Local space grid, scrolling logic, neighbor management |
| `core/source/world/local_space.c` | Local space init, 9-way collision polling |
| `core/source/world/chunk.c` | Chunk init, chunk serialization/deserialization processes |
| `core/source/world/chunk_pool.c` | Chunk pool allocation/release |
| `core/source/world/chunk_generator_table.c` | Chunk generation function table |
| `core/source/world/camera.c` | Camera init, follow handler |
| `core/source/world/tile_logic_context.c` | Tile logic table init/release per layer |
| `core/source/world/tile_logic_table.c` | Tile logic record array allocation (the module's heap allocation) |
| `core/source/world/region.c` | Region coordinate math, bitmap tracking |
| `core/source/world/region_manager.c` | Region manager init |
| `core/include/world/world.h` | World public API + inline getters |
| `core/include/world/global_space.h` | Global space lifecycle flags + inline helpers |
| `core/include/world/global_space_manager.h` | UUID generation for global spaces |
| `core/include/world/local_space.h` | Local space inline helpers |
| `core/include/world/local_space_manager.h` | Local space manager public API |
| `core/include/world/chunk.h` | Chunk tile access, state flags |
| `core/include/world/camera.h` | Camera API |
| `core/include/world/tile.h` | Tile flag helpers |
| `core/include/world/tile_logic_context.h` | Tile logic lookup helpers |
| `core/include/world/region.h` | Region helpers |
| `core/include/world/region_manager.h` | Region manager API |
| `core/include/world/chunk_generator_table.h` | Chunk generator table API |
