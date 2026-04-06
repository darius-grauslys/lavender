# 1. System Overview: Rendering

## 1.1 Purpose

The rendering system provides the engine's complete graphics pipeline:
texture management, sprite rendering and animation, windowed composition,
font/text layout, and the bridge to platform-specific graphics backends.
All rendering state is aggregated under a single `Gfx_Context` owned by
`Game`.

## 1.2 Architecture

### 1.2.1 Data Hierarchy

    Game
    +-- Gfx_Context
    |   +-- Graphics_Window_Manager
    |   |   +-- Graphics_Window[0..MAX_QUANTITY_OF__GRAPHICS_WINDOWS-1]
    |   |       +-- Serialization_Header (UUID)
    |   |       +-- PLATFORM_Graphics_Window* (platform handle)
    |   |       +-- UI_Tile_Map__Wrapper (tile map backing data)
    |   |       +-- Identifier__u32 uuid_of__sprite_manager   --> Sprite_Manager
    |   |       +-- Identifier__u32 uuid_of__ui_manager        --> UI_Manager
    |   |       +-- Identifier__u32 uuid_of__hitbox_manager    --> Hitbox_Manager_Instance
    |   |       +-- Identifier__u32 graphics_window__parent__uuid --> parent Graphics_Window
    |   |       +-- f_PLATFORM_compose_gfx_window (compose callback)
    |   |       +-- f_PLATFORM_render_gfx_window (render callback)
    |   |       +-- Camera* (optional)
    |   |       +-- Graphics_Window_Kind (discriminator)
    |   |       +-- Index__u8 priority_of__window
    |   |       +-- Graphics_Window_Flags__u8
    |   |
    |   +-- Aliased_Texture_Manager
    |   |   +-- Aliased_Texture[0..MAX_QUANTITY_OF__ALIASED_TEXTURES-1]
    |   |       +-- Serialization_Header (UUID)
    |   |       +-- Texture_Name__c_str (alias string, up to MAX_LENGTH_OF__TEXTURE_NAME)
    |   |       +-- Texture
    |   |           +-- PLATFORM_Texture* (platform handle)
    |   |           +-- Texture_Flags (size, format, render method, visibility, readonly)
    |   |
    |   +-- Sprite_Context
    |   |   +-- Sprite_Animation[0..Sprite_Animation_Kind__Unknown-1]  (global registry)
    |   |   +-- Sprite_Animation_Group_Set[0..Sprite_Animation_Group_Kind__Unknown-1]  (global registry)
    |   |   +-- Sprite_Manager[0..max_quantity_of__sprite_managers-1]  (heap-allocated pool)
    |   |       +-- Serialization_Header (UUID)
    |   |       +-- Sprite[0..max_quantity_of__sprites-1]  (heap-allocated pool)
    |   |       |   +-- Serialization_Header (UUID)
    |   |       |   +-- PLATFORM_Sprite* (platform handle)
    |   |       |   +-- Texture texture_for__sprite_to__sample (source sheet)
    |   |       |   +-- Texture texture_of__sprite (output)
    |   |       |   +-- Sprite_Animation (current animation state)
    |   |       |   +-- m_Sprite_Animation_Handler (per-frame callback)
    |   |       |   +-- Sprite_Flags (enabled, update needed, flip x/y)
    |   |       |
    |   |       +-- Sprite_Render_Record[0..max_quantity_of__sprites-1]  (heap-allocated)
    |   |           +-- Vector__3i32F4 position
    |   |           +-- Sprite* (reference into sprite pool)
    |   |
    |   +-- Font_Manager
    |   |   +-- Font[0..MAX_QUANTITY_OF__FONT-1]
    |   |       +-- Font_Letter font_lookup_table[256]  (indexed by ASCII code)
    |   |       +-- Texture texture_of__font (atlas)
    |   |       +-- Font_Flags (IS_ALLOCATED)
    |   |
    |   +-- UI_Context  (see UI specs)
    |   +-- UI_Tile_Map_Manager  (see UI specs)
    |   +-- PLATFORM_Gfx_Context*  (platform-specific state)

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Gfx_Context` | Top-level rendering state container. Owned by `Game`. Aggregates all rendering subsystems. |
| `Graphics_Window_Manager` | Fixed-size pool of `Graphics_Window` instances. Handles allocation, priority sorting, parent-child relationships, composition, and rendering. |
| `Graphics_Window` | A renderable surface. Can own or share a `UI_Manager`, `Sprite_Manager`, and hitbox manager. Forms parent-child hierarchies. Wraps a `PLATFORM_Graphics_Window`. |
| `Aliased_Texture_Manager` | Pool of `Aliased_Texture` entries. Maps human-readable string names to `Texture` instances. |
| `Aliased_Texture` | A `Texture` paired with a string alias for name-based lookup. |
| `Texture` | Wraps a `PLATFORM_Texture*` with `Texture_Flags` encoding size, format, render method, and visibility. The fundamental image resource type. |
| `Texture_Flags` | 32-bit bitfield encoding texture dimensions (3+3 bits), format (3 bits), render method (3 bits), and core flags (hidden, readonly). |
| `Sprite_Context` | Manages the heap-allocated pool of `Sprite_Manager` instances and global registries of `Sprite_Animation` and `Sprite_Animation_Group_Set` entries. |
| `Sprite_Manager` | Pool of `Sprite` instances associated with a `Graphics_Window`. Handles allocation, release, UUID lookup, and batch rendering. |
| `Sprite` | A renderable animated image. Wraps `PLATFORM_Sprite*`, two `Texture` references (sample source and output), animation state, and rendering flags. |
| `Sprite_Animation` | Animation state: kind, timer, frame range, ticks-per-frame, and flags (looping, direction offset). Registered globally in `Sprite_Context`, copied into individual `Sprite` instances. |
| `Sprite_Animation_Group_Set` | Describes subgroup layout (rows, columns, index) within a sprite's sample texture. |
| `Sprite_Render_Record` | Pairs a `Sprite*` with a `Vector__3i32F4` position for batch rendering. |
| `Font_Manager` | Fixed-size pool of `Font` instances. |
| `Font` | ASCII lookup table of 256 `Font_Letter` glyph descriptors plus a texture atlas. |
| `Font_Letter` | Compact glyph descriptor: width, height, x/y offsets (4 bits each), and 16-bit atlas index. |
| `Typer` | Text layout engine. Renders strings into a `Texture` or `PLATFORM_Graphics_Window` using a `Font`, with cursor wrapping and line spacing. |

### 1.2.3 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` | 8 | Maximum concurrent graphics windows. |
| `MAX_QUANTITY_OF__ALIASED_TEXTURES` | 128 | Maximum named textures. |
| `MAX_QUANTITY_OF__FONT` | 8 | Maximum fonts in pool. |
| `FONT_LETTER_MAX_QUANTITY_OF` | 256 | One glyph entry per ASCII code. |
| `MAX_LENGTH_OF__TEXTURE_NAME` | 32 | Maximum alias name length (bytes). |

## 1.3 Graphics Window Resource Sharing Model

A `Graphics_Window` can **own** or **share** three resource managers,
identified by UUID fields. If the manager UUID equals the window's own UUID,
the window owns it. If the UUID differs but is valid, the resource is shared
(borrowed from another window).

| UUID Field | Owned When | Shared When |
|------------|------------|-------------|
| `uuid_of__sprite_manager` | UUID == window UUID | UUID valid but != window UUID |
| `uuid_of__ui_manager` | UUID == window UUID | UUID valid but != window UUID |
| `uuid_of__hitbox_manager` | UUID == window UUID | UUID valid but != window UUID |

When a window **owns** a resource, releasing the window also releases the
resource. When a window **shares** a resource, the resource outlives the
window.

    Graphics_Window (UUID: 0x100)
      uuid_of__sprite_manager = 0x100  --> OWNS this Sprite_Manager
      uuid_of__ui_manager     = 0x200  --> SHARES UI_Manager from window 0x200

## 1.4 Graphics Window Parent-Child Hierarchy

Windows form a tree via `graphics_window__parent__uuid`. The manager provides
functions to establish parent-child relationships, query ancestry, find root
parents, and reset/release children when a parent is released or a scene
transitions.

    Graphics_Window (root, parent UUID = IDENTIFIER__UNKNOWN__u32)
      +-- Graphics_Window (child, parent UUID = root UUID)
      |   +-- Graphics_Window (grandchild, parent UUID = child UUID)
      +-- Graphics_Window (child, parent UUID = root UUID)

Platform-provided windows are a special case: they are allocated by the
platform layer during initialization and cannot be released by the engine.
They are identified by the `GRAPHICS_WINDOW__FLAG__IS_PLATFORM_PROVIDED`
flag and are reset (rather than released) during scene transitions.

## 1.5 Texture Pipeline

Textures flow through the system in two paths:

### 1.5.1 Named Texture Path (Asset Loading)

    Game initialization:
      register_aliased_textures(aliased_texture_manager, game)
        -> For each game texture:
           allocate_texture_with__alias(
               p_PLATFORM_gfx_context, p_PLATFORM_gfx_window,
               aliased_texture_manager, "name", texture_flags, &texture)
             -> PLATFORM_allocate_texture(...)
             -> Aliased_Texture stored in pool

           OR load_texture_from__path_with__alias(
               p_PLATFORM_gfx_context, p_PLATFORM_gfx_window,
               aliased_texture_manager, "name", texture_flags, path, &texture)
             -> PLATFORM_allocate_texture_with__path(...)
             -> Aliased_Texture stored in pool

    Runtime lookup:
      get_texture_by__alias(aliased_texture_manager, "name", &texture)
        -> Returns Texture by value via out-parameter

      get_texture_by__uuid(aliased_texture_manager, uuid, &texture)
        -> Returns Texture by value via out-parameter

    Note: bool return values use inverted convention: true = failure, false = success.

### 1.5.2 Sprite Texture Path (Per-Instance)

    allocate_sprite_from__sprite_manager(
        gfx_context, sprite_manager, gfx_window, uuid, sample_texture, texture_flags)
      -> PLATFORM_allocate_sprite(...)
      -> sprite.texture_for__sprite_to__sample = sample_texture (source sheet)
      -> sprite.texture_of__sprite = allocated output texture

## 1.6 Sprite Animation Pipeline

Animations are registered globally in `Sprite_Context` and applied to
individual `Sprite` instances:

### 1.6.1 Registration (Game Initialization)

    register_sprite_animations(p_sprite_manager)  [game-specific, from implemented/]
      -> register_sprite_animation_into__sprite_context(
             sprite_context, Sprite_Animation_Kind__X, animation_definition)
         -> sprite_context.sprite_animations[kind] = definition

      -> register_sprite_animation_group_into__sprite_context(
             sprite_context, Sprite_Animation_Group_Kind__X, group_set)
         -> sprite_context.sprite_animation_groups[group_kind] = group_set

### 1.6.2 Application (Runtime)

    set_sprite_animation(sprite_context, sprite, Sprite_Animation_Kind__X)
      -> Copies registered Sprite_Animation into sprite.animation

### 1.6.3 Per-Frame Update

    poll_sprite_for__animation(game, sprite, sprite_context)
      -> Invokes sprite.m_sprite_animation_handler(sprite, game, sprite_context)
         -> Default handler: advances timer, updates frame index
         -> Sets SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE when frame changes

### 1.6.4 Batch Rendering

    render_sprites_in__sprite_manager(game, sprite_context, sprite_manager, gfx_window)
      -> For each enabled sprite in pool:
         -> PLATFORM_render_sprite(...)

## 1.7 Text Rendering Pipeline

Text rendering uses `Typer` with a `Font` to lay out and render characters:

    1. Font setup:
       Font *p_font = allocate_font_from__font_manager(&font_manager)
       initialize_font(p_font)
       Populate font_lookup_table with Font_Letter entries
       Assign texture atlas to p_font->texture_of__font

    2. Typer setup:
       initialize_typer_with__font(&typer, x, y, w, h, spacing, cx, cy, p_font)
       set_PLATFORM_texture_target_for__typer(&typer, texture)
         OR set_PLATFORM_graphics_window_target_for__typer(&typer, p_gfx_window)

    3. Text output:
       put_c_string_in__typer(gfx_context, &typer, "text", length)
         -> For each character:
            -> get_p_font_letter_from__typer(&typer, char) -> Font_Letter*
            -> poll_typer_for__cursor_wrapping(&typer, p_font_letter)
               -> Wraps to next line if cursor + glyph width exceeds bounding box
            -> PLATFORM_put_char_in__typer(gfx_context, typer, char)
            -> offset_typer_by__font_letter(&typer, p_font_letter)
               -> Advances cursor by glyph width

## 1.8 Lifecycle

### 1.8.1 Initialization

    initialize_gfx_context(&game.gfx_context)
      -> initialize_graphics_window_manager(&graphics_window_manager)
      -> initialize_aliased_texture_manager(&aliased_texture_manager)
      -> initialize_sprite_context(&sprite_context)
      -> initialize_font_manager(&font_manager)
      -> (UI subsystem initialization)

    PLATFORM_initialize_gfx_context(...)
      -> Platform-specific setup
      -> setup_platform_provided_graphics_windows(&gfx_context)

### 1.8.2 Asset Registration (Game-Specific)

    register_aliased_textures(&aliased_texture_manager, p_game)
      -> allocate_texture_with__alias / load_texture_from__path_with__alias
         for each game texture

    register_sprite_animations(p_sprite_manager)
      -> register_sprite_animation_into__sprite_context
         for each animation kind
      -> register_sprite_animation_group_into__sprite_context
         for each animation group kind

### 1.8.3 Window Allocation

    Graphics_Window *p_window =
        allocate_graphics_window_from__graphics_window_manager(
            gfx_context, &graphics_window_manager, texture_flags)
      -> PLATFORM_allocate_gfx_window(...)
      -> Returns Graphics_Window* or null on failure

    Optionally attach resources:
      allocate_ui_manager_for__graphics_window(gfx_context, p_window, capacity)
      allocate_sprite_manager_for__graphics_window(gfx_context, p_window, capacity)
      allocate_hitbox_manager_for__graphics_window(hitbox_context, p_window, type, capacity)

    Or use convenience helpers (from gfx_context_helpers.h):
      GFX_CONTEXT_allocate_graphics_window_with__ui_manager(game, uuid, flags)

### 1.8.4 Per-Frame Update

    For each active sprite:
      poll_sprite_for__animation(game, sprite, sprite_context)

    compose_graphic_windows_in__graphics_window_manager(game)
      -> For each window in priority order:
         -> window.f_PLATFORM_compose_gfx_window(game, window)

    render_graphic_windows_in__graphics_window_manager(game)
      -> For each window in priority order:
         -> window.f_PLATFORM_render_gfx_window(game, window)
         -> render_sprites_in__sprite_manager(game, sprite_context, sprite_manager, window)

### 1.8.5 Window Release

    release_graphics_window_from__graphics_window_manager(game, p_window)
      -> If window owns sprite manager: release_graphics_window_sprite_manager
      -> If window owns UI manager: release_graphics_window_ui_manager
      -> If window owns hitbox manager: release_graphics_window_hitbox_manager
      -> PLATFORM_release_gfx_window(...)

### 1.8.6 Shutdown

    release_all_aliased_textures(p_PLATFORM_gfx_context, &aliased_texture_manager)
      -> PLATFORM_release_texture for each allocated texture
      -> All slots reset

    release_sprite_managers_from__sprite_context(&sprite_context)
      -> Frees heap-allocated sprite manager pool

## 1.9 Platform Integration

The rendering system delegates all hardware-specific operations to platform
functions. The platform layer provides:

| Platform Function | Purpose |
|-------------------|---------|
| `PLATFORM_initialize_gfx_context` | Platform-specific graphics initialization. |
| `PLATFORM_allocate_gfx_window` | Creates a platform-specific graphics window. |
| `PLATFORM_release_gfx_window` | Destroys a platform-specific graphics window. |
| `PLATFORM_allocate_texture` | Allocates a platform texture with given flags. |
| `PLATFORM_allocate_texture_with__path` | Allocates and loads a texture from a file path. |
| `PLATFORM_release_texture` | Frees a platform texture. |
| `PLATFORM_allocate_sprite` | Creates a platform-specific sprite instance. |
| `PLATFORM_release_sprite` | Destroys a platform-specific sprite instance. |
| `PLATFORM_render_sprite` | Renders a sprite to a graphics window. |
| `PLATFORM_put_char_in__typer` | Renders a single character glyph to the typer's render target. |
| `PLATFORM_get_p_graphics_window_with__graphics_window_kind` | Retrieves a platform-provided graphics window by kind. |

Platform-specific state is held in opaque types:

| Opaque Type | Referenced By |
|-------------|---------------|
| `PLATFORM_Gfx_Context` | `Gfx_Context.p_PLATFORM_gfx_context` |
| `PLATFORM_Graphics_Window` | `Graphics_Window.p_PLATFORM_gfx_window` |
| `PLATFORM_Texture` | `Texture.p_PLATFORM_texture` |
| `PLATFORM_Sprite` | `Sprite.p_PLATFORM_sprite` |

## 1.10 Error Conventions

### 1.10.1 Aliased Texture Manager

Functions returning `bool` in the `Aliased_Texture_Manager` use an
**inverted convention**: `true` = failure, `false` = success. This is
consistent across the aliased texture API but differs from most other
engine APIs (e.g. `allocate_sprite_manager__members` returns `true` on
success).

### 1.10.2 Debug Checks

Most `static inline` accessor functions perform null-pointer checks in
debug builds via `debug_error` and return safe defaults (null, false,
`VECTOR__3i32__OUT_OF_BOUNDS`, `IDENTIFIER__UNKNOWN__u32`) on failure.

## 1.11 Convenience Helpers

`gfx_context_helpers.h` provides `static inline` functions that combine
multiple allocation steps:

| Helper | Steps Combined |
|--------|----------------|
| `GFX_CONTEXT_allocate_graphics_window_with__ui_manager` | Allocate window + allocate UI manager. Cleans up on partial failure. |
| `GFX_CONTEXT_allocate_graphics_window_with__ui_manager_and__sprite_pool` | Allocate window + UI manager + sprite pool. **WARNING:** references removed API. |
| `GFX_CONTEXT_allocate_graphics_window_with__sprite_pool` | Allocate window + sprite pool. **WARNING:** references removed API. |

Only `GFX_CONTEXT_allocate_graphics_window_with__ui_manager` is currently
functional. The sprite pool variants reference a removed
`allocate_sprite_pool_from__sprite_manager` API and should be considered
deprecated. Prefer using `allocate_sprite_manager_for__graphics_window`
directly after window allocation.

## 1.12 Deprecated Components

### 1.12.1 animate_sprite.h

This header previously contained sprite animation helpers but all function
bodies are currently commented out. The animation system has been refactored
to use `Sprite_Animation` structs and `m_Sprite_Animation_Handler` callbacks.
New code should use:
- `poll_sprite_for__animation` (from `sprite.h`)
- `set_sprite_animation` (from `sprite.h`)
- `Sprite_Animation` flag helpers (from `sprite_animation.h`)

## 1.13 Relationship to Other Systems

| Concern | Managed By |
|---------|------------|
| Texture allocation and named lookup | `Aliased_Texture_Manager` -> `Aliased_Texture` |
| Sprite pooling, animation, and rendering | `Sprite_Context` -> `Sprite_Manager` -> `Sprite` |
| Window composition and rendering order | `Graphics_Window_Manager` -> `Graphics_Window` |
| Text layout and rendering | `Typer` -> `Font` -> `Font_Letter` |
| Font pooling | `Font_Manager` |
| UI element management | `UI_Context` -> `UI_Manager` (see UI specs) |
| Platform-specific rendering | `PLATFORM_Gfx_Context`, `PLATFORM_Graphics_Window`, etc. |
| Collision/hitbox management per window | `Hitbox_Context` -> `Hitbox_Manager_Instance` (see collision specs) |
| Game-specific asset registration | `implemented/` template headers (see implemented/ overview) |

The `Graphics_Window.uuid_of__sprite_manager`, `uuid_of__ui_manager`, and
`uuid_of__hitbox_manager` fields are the bridges between the rendering
system and the sprite, UI, and collision subsystems respectively. These
UUIDs are resolved through their respective managers at runtime.
