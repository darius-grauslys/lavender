# Specification: core/include/world/world.h

## Overview

Defines operations on `World` — the top-level container for all world state
including entities, chunks, global spaces, collision nodes, tile logic,
chunk generation, inventory, items, camera, and rendering configuration.
Provides initialization, entity management, scrolling, save/load, and
accessor functions.

## Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `World`, `Game`, `Entity`, all sub-component types)

## Types

### World (struct)

    typedef struct World_t {
        Serialization_Header _serialization_header;
        Region_Manager region_manager;
        Entity_Manager entity_manager;
        Global_Space_Manager global_space_manager;
        Collision_Node_Pool collision_node_pool;
        Chunk_Pool chunk_pool;
        Structure_Manager structure_manager;
        Tile_Logic_Table tile_logic_table;
        Chunk_Generator_Table chunk_generator_table;
        Repeatable_Psuedo_Random repeatable_pseudo_random;
        Inventory_Manager inventory_manager;
        Item_Manager item_manager;
        Camera camera;
        f_Tile_Render_Kernel f_tile_render_kernel;
        World_Name_String name;
        Vector__3i32F4 spawn_point;
        f_Hitbox_AABB_Tile_Touch_Handler f_hitbox_aabb_tile_touch_handler;
        f_Hitbox_AABB_Collision_Handler f_hitbox_aabb_collision_handler;
        Graphics_Window *p_graphics_window_for__world;
        Quantity__u8 length_of__world_name;
    } World;

### World_Name_String

    #define WORLD_NAME_MAX_SIZE_OF 32
    typedef char World_Name_String[WORLD_NAME_MAX_SIZE_OF];

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_world` | `(Game*, World*) -> void` | Initializes all world sub-components. |

### World Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `manage_world` | `(Game*) -> void` | Per-frame world update (scrolling, generation, etc.). |
| `manage_world__entities` | `(Game*) -> void` | Per-frame entity update. |

### Entity Management

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_entity_into__world` | `(Game*, Entity_Kind, Vector__3i32F4) -> Entity*` | `Entity*` | Allocates and initializes an entity at the given position. |
| `get_p_entity_from__world_using__3i32F4` | `(Game*, World*, Vector__3i32F4) -> Entity*` | `Entity*` | Finds an entity near the given position. |

### Scrolling

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_world_for__scrolling` | `(Game*, World*, Graphics_Window*) -> bool` | `bool` | Checks and performs world scrolling based on camera position. |

### Save/Load

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `save_world` | `(PLATFORM_File_System_Context*, World*) -> void` | `void` | Saves the world. Only call when leaving world. |
| `load_world` | `(Game*) -> Process*` | `Process*` | Loads the world. Only call from main menu. Returns the load process. |

### Collision Node Update

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_for_collision_node_update` | `(Game*, Vector__3i32F4 old, Vector__3i32F4 new, Identifier__u32) -> bool` | `bool` | Updates collision node membership when an entity moves between chunks. |

### Name Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_name_of__world` | `(World*, World_Name_String) -> void` | Sets the world name string. |

### Sub-Component Accessors (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `get_p_camera_from__world` | `Camera*` | Returns `&world.camera`. |
| `get_p_inventory_manager_from__world` | `Inventory_Manager*` | Returns `&world.inventory_manager`. |
| `get_p_item_manager_from__world` | `Item_Manager*` | Returns `&world.item_manager`. |
| `get_p_entity_manager_from__world` | `Entity_Manager*` | Returns `&world.entity_manager`. Debug null-checked. |
| `get_p_tile_logic_table_from__world` | `Tile_Logic_Table*` | Returns `&world.tile_logic_table`. |
| `get_p_chunk_generation_table_from__world` | `Chunk_Generator_Table*` | Returns `&world.chunk_generator_table`. |
| `get_p_global_space_manager_from__world` | `Global_Space_Manager*` | Returns `&world.global_space_manager`. |
| `get_p_collision_node_pool_from__world` | `Collision_Node_Pool*` | Returns `&world.collision_node_pool`. |
| `get_p_chunk_pool_from__world` | `Chunk_Pool*` | Returns `&world.chunk_pool`. |
| `get_p_repeatable_psuedo_random_from__world` | `Repeatable_Psuedo_Random*` | Returns `&world.repeatable_pseudo_random`. |
| `get_p_graphics_window_from__world` | `Graphics_Window*` | Returns `world.p_graphics_window_for__world`. |

### Handler Setters (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_f_hitbox_aabb_tile_touch_handler_of__world` | `(World*, f_Hitbox_AABB_Tile_Touch_Handler) -> void` | Sets the tile touch collision handler. |
| `set_f_hitbox_aabb_collision_handler_of__world` | `(World*, f_Hitbox_AABB_Collision_Handler) -> void` | Sets the entity collision handler. |
| `set_spawn_point_of__world` | `(World*, Vector__3i32F4) -> void` | Sets the world spawn point. |
| `set_f_tile_render_kernel_of__world` | `(World*, f_Tile_Render_Kernel) -> void` | Sets the tile render kernel. |

### Spawn Point and Render Kernel (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_spawn_point_of__world` | `(World*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns the spawn point. |
| `get_f_tile_render_kernel_of__world` | `(World*) -> f_Tile_Render_Kernel` | `f_Tile_Render_Kernel` | Returns the tile render kernel. |

## Agentic Workflow

### World Ownership

`World` is heap-allocated and owned by `Game` (at `game.pM_world`). It is
allocated during `load_world` and freed during scene transitions.

### Save/Load Constraints

- `save_world`: Only call when leaving the world and returning to main menu.
- `load_world`: Only call from the main menu. Returns a `Process*` that
  must complete before the world is usable.

### Preconditions

- `get_p_entity_manager_from__world`: debug builds abort if `p_world` is null.
- All other accessors require non-null `p_world`.

## Header Guard

`WORLD_H`
