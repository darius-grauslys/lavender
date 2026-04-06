# 1 System Overview: Implemented Types (Template Injection System)

## 1.1 Purpose

The `types/implemented/` directory contains **template headers** that define
game-customizable types — enums, structs, and constants — which are injected
into the engine's central `defines_weak.h` and `defines.h` headers via
conditional compilation. These templates ship with the engine and are copied
to each new game project by the `tools/lav_new_project` script. The copies
in the game project directory are the files that participate in the build;
the originals in the engine serve only as starting-point templates.

This system allows the engine to reference game-specific types (entity kinds,
tile kinds, item kinds, etc.) without hard-coding them, while giving each
game project full control over the concrete values.

## 1.2 Architecture

### 1.2.1 Injection Mechanism

Every template header follows the same pattern:

    // types/implemented/example_kind.h
    #ifndef IMPL_EXAMPLE_KIND_H
    #define IMPL_EXAMPLE_KIND_H

    #define DEFINE_EXAMPLE_KIND

    typedef enum Example_Kind {
        Example_Kind__None = 0,
        // ... game-specific entries ...
        Example_Kind__Unknown
    } Example_Kind;

    #endif

The consuming header (`defines_weak.h` or `defines.h`) includes the template
and checks whether the guard macro was defined:

    #include <types/implemented/example_kind.h>
    #ifndef DEFINE_EXAMPLE_KIND
    // Fallback: minimal default definition
    typedef enum Example_Kind {
        Example_Kind__None = 0,
        Example_Kind__Unknown
    } Example_Kind;
    #endif

If the game project provides its own copy of the template (which defines
`DEFINE_EXAMPLE_KIND`), the fallback is suppressed. If the file is absent
or empty, the fallback provides a minimal compilable definition.

### 1.2.2 Two Injection Targets

| Target | Receives | Reason |
|--------|----------|--------|
| `defines_weak.h` | Enum types (forward-declarable discriminators) | These are used in forward declarations, function signatures, and weak typedefs throughout the engine. They must be available early in the include chain. |
| `defines.h` | Struct types and constants | These depend on types from `defines_weak.h` (e.g. `Tile` contains `Tile_Kind`, `Entity_Data` contains `Entity_Kind`). They are available after full type definitions. |

### 1.2.3 Data Flow

    tools/lav_new_project
        |
        | copies templates from core/include/types/implemented/
        v
    game_project/include/types/implemented/
        |
        | game developer extends with game-specific entries
        v
    Build system includes game_project headers
        |
        | #include <types/implemented/tile_kind.h>  (game's copy)
        | #define DEFINE_TILE_KIND is set
        v
    defines_weak.h / defines.h
        |
        | fallback suppressed; game's definition used
        v
    Engine code references Tile_Kind, Entity_Kind, etc.

## 1.3 Template Categories

### 1.3.1 World & Tile Templates

These templates define the types used by the world, chunk, and tile systems.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `tile_kind.h` | `DEFINE_TILE_KIND` | `defines_weak.h` | `Tile_Kind` enum | `Tile_Logic_Table_Data.tile_logic_record__tile_kind[Tile_Kind__Unknown]` |
| `tile.h` | `DEFINE_TILE` | `defines.h` | `Tile` struct | Stored in `Chunk.tiles[]` |
| `tile_logic_table_data.h` | `DEFINE_TILE_LOGIC_TABLE_DATA` | `defines.h` | `Tile_Logic_Table_Data` struct | Embedded in `Tile_Logic_Table` |
| `tile_logic_table_list.h` | `DEFINE_TILE_LOGIC_TABLE_LIST` | `defines.h` | `MAX_QUANTITY_OF__TILE_LOGIC_TABLES` constant | Limits number of registered tile logic tables |
| `chunk_generator_kind.h` | `DEFINE_CHUNK_GENERATOR_KIND` | `defines_weak.h` | `Chunk_Generator_Kind` enum | `Chunk_Generator_Table.M_process__chunk_generators[Chunk_Generator_Kind__Unknown]` |

**Dependencies within this group:**

- `Tile` (from `tile.h`) contains a `Tile_Kind` field (from `tile_kind.h`).
- `Tile_Logic_Table_Data` (from `tile_logic_table_data.h`) is sized by
  `Tile_Kind__Unknown` (from `tile_kind.h`).
- `Chunk_Generator_Kind` is independent but generators produce tiles of
  specific `Tile_Kind` values.

**Lifecycle:**

1. Game developer adds tile kinds to `tile_kind.h`.
2. Game developer optionally extends `Tile` struct in `tile.h` with
   additional per-tile data (flags, metadata).
3. Game developer registers tile logic records per `Tile_Kind` via
   `register_tile_logic_tables`.
4. Game developer adds chunk generator kinds and registers generators via
   `register_chunk_generators`.

### 1.3.2 Entity Templates

These templates define the types used by the entity management system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `entity_kind.h` | `DEFINE_ENTITY_KIND` | `defines_weak.h` | `Entity_Kind` enum | `Entity_Manager.entity_functions[Entity_Kind__Unknown]` |
| `entity_data.h` | `DEFINE_ENTITY_DATA` | `defines.h` | `Entity_Data` struct | Embedded in every `Entity` |
| `entity_functions.h` | `DEFINE_ENTITY_FUNCTIONS` | `defines.h` | `Entity_Functions` struct | Stored per-kind in `Entity_Manager` |

**Dependencies within this group:**

- `Entity_Data` (from `entity_data.h`) contains an `Entity_Kind` field
  (from `entity_kind.h`) and `Entity_Flags__u32`.
- `Entity_Functions` (from `entity_functions.h`) uses handler typedefs
  from `defines_weak.h` (`m_Entity_Handler`,
  `m_Entity_Serialization_Handler`, `m_Entity_Deserialization_Handler`).
- The `Entity_Manager` indexes `Entity_Functions` by `Entity_Kind`.

**Lifecycle:**

1. Game developer adds entity kinds to `entity_kind.h`.
2. Game developer extends `Entity_Data` in `entity_data.h` with
   game-specific fields (health, inventory pointer, sprite, etc.).
3. Game developer optionally adds custom handler function pointers to
   `Entity_Functions` in `entity_functions.h` (after the six required
   handlers).
4. Entity functions are registered per-kind during game initialization.

**Constraints:**

- `Entity_Functions` must contain **only function pointers**. The engine
  copies the entire struct by value when registering entity kinds.
- The six required handlers (`dispose`, `update`, `disable`, `enable`,
  `serialize`, `deserialize`) must not be removed or reordered.

### 1.3.3 Item Templates

These templates define the types used by the inventory and item systems.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `item_kind.h` | `DEFINE_ITEM_KIND` | `defines_weak.h` | `Item_Kind` enum | `Item_Manager.item_templates[(u16)Item_Kind__Unknown]` |
| `item_data.h` | `DEFINE_ITEM_DATA` | `defines.h` | `Item_Data` struct | Embedded in every `Item` |

**Dependencies within this group:**

- `Item_Data` is independent of `Item_Kind` at the struct level, but
  `Item_Kind` discriminates which `Item_Data` interpretation applies.
- `Item_Data` is embedded in `Item`, which is embedded in `Item_Stack`,
  which is embedded in `Inventory`. Size of `Item_Data` directly affects
  total `Inventory` memory footprint.

**Lifecycle:**

1. Game developer adds item kinds to `item_kind.h`.
2. Game developer extends `Item_Data` in `item_data.h` with game-specific
   fields (damage, durability, weight, etc.).

### 1.3.4 Sprite & Animation Templates

These templates define the types used by the sprite rendering and animation
systems.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `sprite_kind.h` | `DEFINE_SPRITE_KIND` | `defines_weak.h` | `Sprite_Kind` enum | Stored in `Sprite.the_kind_of__sprite` |
| `sprite_animation_kind.h` | `DEFINE_SPRITE_ANIMATION_KIND` | `defines_weak.h` | `Sprite_Animation_Kind` enum | `Sprite_Context.sprite_animations[Sprite_Animation_Kind__Unknown]` |
| `sprite_animation_group_kind.h` | `DEFINE_SPRITE_ANIMATION_GROUP_KIND` | `defines_weak.h` | `Sprite_Animation_Group_Kind` enum | `Sprite_Context.sprite_animation_groups[Sprite_Animation_Group_Kind__Unknown]` |

**Dependencies within this group:**

- `Sprite_Kind` identifies which sprite asset to use.
- `Sprite_Animation_Kind` identifies a specific animation sequence.
- `Sprite_Animation_Group_Kind` identifies a group of related animations
  (e.g. all animations for a particular entity type).
- Animations and groups are registered via `register_sprite_animations`
  and `register_sprite_animation_group_into__sprite_context`.

**Lifecycle:**

1. Game developer adds sprite kinds to `sprite_kind.h`.
2. Game developer adds animation kinds to `sprite_animation_kind.h`.
3. Game developer adds animation group kinds to
   `sprite_animation_group_kind.h`.
4. Registrations happen during game initialization via the corresponding
   registrar functions.

### 1.3.5 Audio Templates

These templates define the types used by the audio system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `audio_effect_kind.h` | `DEFINE_AUDIO_EFFECT_KIND` | `defines_weak.h` | `Audio_Effect_Kind` enum | Platform-specific audio effect arrays |
| `audio_stream_kind.h` | `DEFINE_AUDIO_STREAM_KIND` | `defines_weak.h` | `Audio_Stream_Kind` enum | Platform-specific audio stream management |

**Dependencies within this group:**

- `Audio_Effect_Kind` and `Audio_Stream_Kind` are independent of each other.
- Both are consumed by `PLATFORM_Audio_Context` for platform-specific
  audio resource management.

**Lifecycle:**

1. Game developer adds audio effect kinds to `audio_effect_kind.h`.
2. Game developer adds audio stream kinds to `audio_stream_kind.h`.
3. Platform backends map these kinds to concrete audio resources.

### 1.3.6 UI Templates

These templates define the types used by the UI system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `ui_element_kind.h` | `DEFINE_UI_ELEMENT_KIND` | `defines_weak.h` | `UI_Element_Kind` enum | Discriminator in `UI_Element` |
| `ui_tile_kind.h` | `DEFINE_UI_TILE_KIND` | `defines_weak.h` | `UI_Tile_Kind` enum | 10-bit bitfield in `UI_Tile` (max 1024 kinds) |
| `ui_sprite_kind.h` | `DEFINE_UI_SPRITE_KIND` | `defines_weak.h` | `UI_Sprite_Kind` enum | Platform-specific sprite allocation |
| `ui_element_data.h` | `DEFINE_UI_ELEMENT_DATA` | `defines.h` | `UI_Element_Data` struct | Embedded in every `UI_Element` |
| `graphics_window_kind.h` | `DEFINE_GRAPHICS_WINDOW_KIND` | `defines_weak.h` | `Graphics_Window_Kind` enum | `UI_Context.ui_window_record[Graphics_Window_Kind__Unknown]` |

**Dependencies within this group:**

- `UI_Element_Kind` is a discriminator stored in `UI_Element`. Unlike most
  template enums, the core engine defines all standard UI element kinds
  (`Button`, `Draggable`, `Slider`, `Drop_Zone`, `Text`, `Text_Box`,
  `Logical`, `Window`). This enum is typically not extended.
- `UI_Element_Data` is embedded in every `UI_Element`, affecting
  `UI_Manager` pool memory footprint.
- `Graphics_Window_Kind` identifies registered UI windows. Each kind must
  be registered via `register_ui_window_into__ui_context`.
- `UI_Tile_Kind` is stored as a 10-bit bitfield, limiting the maximum
  number of kinds to 1024.
- `UI_Sprite_Kind` controls platform-specific sprite allocation. The
  default template aliases all sizes together; games should break the
  aliases if they need distinct sprite sizes.

**Lifecycle:**

1. Game developer adds graphics window kinds to `graphics_window_kind.h`
   and registers them via `register_ui_window_into__ui_context`.
2. Game developer adds UI tile kinds to `ui_tile_kind.h` for tile-based
   UI composition.
3. Game developer extends `UI_Element_Data` in `ui_element_data.h` with
   game-specific per-element data.
4. Game developer optionally adjusts `UI_Sprite_Kind` aliases in
   `ui_sprite_kind.h`.

### 1.3.7 Collision & Hitbox Templates

These templates define the types used by the collision detection system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `hitbox_kind.h` | `DEFINE_HITBOX_KIND` | `defines.h` | `Hitbox_Kind` enum | Hitbox type discrimination in game actions |
| `hitbox_manager_type.h` | `DEFINE_HITBOX_MANAGER_TYPE` | `defines.h` | `Hitbox_Manager_Type` enum | `Hitbox_Context.hitbox_manager_instance__invocation_table[Hitbox_Manager_Type__Unknown]` and `Hitbox_Context.hitbox_manager_registration_records[Hitbox_Manager_Type__Unknown]` |

**Dependencies within this group:**

- `Hitbox_Kind` enumerates the geometric types of hitboxes (`Opaque`,
  `AABB`, and optionally `AAABBB`, `Ball`, `Sphere`).
- `Hitbox_Manager_Type` enumerates the hitbox manager implementations.
  `Hitbox_Manager_Type__AABB` is required by core for UI hitbox management.
- `Game_Action_Kind__Hitbox` (from `game_action_kind.h`) uses `Hitbox_Kind`
  for hitbox type discrimination in game actions, creating a cross-group
  dependency.

**Lifecycle:**

1. Game developer optionally adds hitbox kinds to `hitbox_kind.h` (e.g.
   `AAABBB`, `Ball`, `Sphere`).
2. Game developer optionally adds hitbox manager types to
   `hitbox_manager_type.h` and reassigns `Hitbox_Manager_Type__Default`.
3. Core registers built-in hitbox managers; game can register additional
   ones.

### 1.3.8 Game Action Templates

These templates define the types used by the game action / multiplayer
communication system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `game_action_kind.h` | `DEFINE_GAME_ACTION_KIND` | `defines_weak.h` | `Game_Action_Kind` enum | `Game_Action_Logic_Table.game_action_logic_entries[Game_Action_Kind__Unknown]` |

**Dependencies:**

- `Game_Action_Kind` has a cross-group dependency on `Hitbox_Kind` via the
  `Game_Action_Kind__Hitbox` / `Game_Action_Kind__Hitbox__End` delimiter
  range.
- All engine-defined kinds (from `None` through `Custom`) must remain
  present and in order. Game developers add custom actions between
  `Game_Action_Kind__Custom` and `Game_Action_Kind__Unknown`.

**Lifecycle:**

1. Game developer adds custom game action kinds after
   `Game_Action_Kind__Custom`.
2. Game action logic is registered per-kind in the
   `Game_Action_Logic_Table`.

### 1.3.9 Scene Templates

These templates define the types used by the scene management system.

| Template | Guard Macro | Injection Target | Type | Array Sizing Usage |
|----------|-------------|------------------|------|--------------------|
| `scene_kind.h` | `DEFINE_SCENE_KIND` | `defines_weak.h` | `Scene_Kind` enum | `Scene_Manager.scenes[Scene_Kind__Unknown]` |

**Dependencies:**

- `Scene_Kind` is independent of other template types.

**Lifecycle:**

1. Game developer adds scene kinds to `scene_kind.h` (e.g. `Main_Menu`,
   `Game`, `Pause`).
2. Scenes are registered per-kind in the `Scene_Manager`.

## 1.4 Sentinel Conventions

All template enums follow a consistent sentinel pattern:

| Sentinel | Position | Purpose |
|----------|----------|---------|
| `*__None` | First (value 0) | Default / empty / uninitialized state. |
| `*__Unknown` | Last | End-of-enum sentinel. Used for array sizing (`array[Kind__Unknown]` allocates exactly enough entries for all valid kinds). |

The `__Unknown` sentinel is critical: engine data structures use it to
determine array dimensions at compile time. Adding entries before `__Unknown`
automatically grows the corresponding arrays.

## 1.5 Cross-Template Dependencies

    tile_kind.h ──────────> tile.h                  (Tile contains Tile_Kind)
    tile_kind.h ──────────> tile_logic_table_data.h (sized by Tile_Kind__Unknown)
    entity_kind.h ────────> entity_data.h           (Entity_Data contains Entity_Kind)
    hitbox_kind.h ────────> game_action_kind.h      (Hitbox__End delimiter)

All other templates are independent of each other at the type level, though
they may interact at runtime through the systems that consume them.

## 1.6 Memory Impact

Several template types are embedded in pooled structures. Extending them
increases per-instance memory usage:

| Template | Embedded In | Pool Owner | Impact |
|----------|-------------|------------|--------|
| `Tile` | `Chunk.tiles[]` | `Chunk_Manager` | `sizeof(Tile) * CHUNK__QUANTITY_OF__TILES` per chunk |
| `Entity_Data` | `Entity.entity_data` | `Entity_Manager` | `sizeof(Entity_Data) * MAX_QUANTITY_OF__ENTITIES` |
| `Item_Data` | `Item.item_data` → `Item_Stack` → `Inventory` | `Inventory_Manager` | Cascading size increase through `Item` → `Item_Stack` → `Inventory` |
| `UI_Element_Data` | `UI_Element.ui_element_data` | `UI_Manager` | `sizeof(UI_Element_Data) * max_quantity_of__ui_elements` |

## 1.7 Guard Macro Summary

Every template header defines a guard macro that suppresses the fallback
definition. These macros must never be removed from the template files:

| File | Guard Macro |
|------|-------------|
| `tile_kind.h` | `DEFINE_TILE_KIND` |
| `tile.h` | `DEFINE_TILE` |
| `tile_logic_table_data.h` | `DEFINE_TILE_LOGIC_TABLE_DATA` |
| `tile_logic_table_list.h` | `DEFINE_TILE_LOGIC_TABLE_LIST` |
| `chunk_generator_kind.h` | `DEFINE_CHUNK_GENERATOR_KIND` |
| `entity_kind.h` | `DEFINE_ENTITY_KIND` |
| `entity_data.h` | `DEFINE_ENTITY_DATA` |
| `entity_functions.h` | `DEFINE_ENTITY_FUNCTIONS` |
| `item_kind.h` | `DEFINE_ITEM_KIND` |
| `item_data.h` | `DEFINE_ITEM_DATA` |
| `sprite_kind.h` | `DEFINE_SPRITE_KIND` |
| `sprite_animation_kind.h` | `DEFINE_SPRITE_ANIMATION_KIND` |
| `sprite_animation_group_kind.h` | `DEFINE_SPRITE_ANIMATION_GROUP_KIND` |
| `audio_effect_kind.h` | `DEFINE_AUDIO_EFFECT_KIND` |
| `audio_stream_kind.h` | `DEFINE_AUDIO_STREAM_KIND` |
| `ui_element_kind.h` | `DEFINE_UI_ELEMENT_KIND` |
| `ui_tile_kind.h` | `DEFINE_UI_TILE_KIND` |
| `ui_sprite_kind.h` | `DEFINE_UI_SPRITE_KIND` |
| `ui_element_data.h` | `DEFINE_UI_ELEMENT_DATA` |
| `graphics_window_kind.h` | `DEFINE_GRAPHICS_WINDOW_KIND` |
| `game_action_kind.h` | `DEFINE_GAME_ACTION_KIND` |
| `scene_kind.h` | `DEFINE_SCENE_KIND` |
| `hitbox_kind.h` | `DEFINE_HITBOX_KIND` |
| `hitbox_manager_type.h` | `DEFINE_HITBOX_MANAGER_TYPE` |

## 1.8 Agentic Workflow Summary

When extending any template:

1. **Never remove** the `#define DEFINE_*` guard macro.
2. **Never remove** the `*__None` first entry or `*__Unknown` last entry
   from enums.
3. **Never remove or reorder** engine-required fields in structs
   (`Entity_Functions` required handlers, `Entity_Data.the_kind_of__entity`,
   `Tile.the_kind_of__tile`).
4. **Add new enum entries** between the last engine-defined entry and
   `*__Unknown`.
5. **Add new struct fields** after the engine-required fields.
6. **Be mindful of memory impact** when extending embedded structs (`Tile`,
   `Entity_Data`, `Item_Data`, `UI_Element_Data`).
