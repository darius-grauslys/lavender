# 1. Specification: core/include/rendering/graphics_window.h

## 1.1 Overview

Defines operations on `Graphics_Window` — the engine's abstraction for a
renderable surface that can contain UI elements, sprites, tile maps, and
world rendering. Graphics windows form a parent-child hierarchy and can
own or share `UI_Manager`, `Sprite_Manager`, and hitbox manager instances.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Graphics_Window`, all sub-component types)
- `game.h` (for `Game`, `get_p_gfx_context_from__game`, `get_p_hitbox_context_from__game`)
- `rendering/gfx_context.h` (for `Gfx_Context` accessors)
- `rendering/graphics_window_manager.h` (for manager operations, parent lookup)
- `rendering/sprite_context.h` (for `Sprite_Context` accessors)
- `rendering/sprite_manager.h` (for `Sprite_Manager` operations)
- `serialization/identifiers.h` (for `is_identifier_u32__invalid`, `IDENTIFIER__UNKNOWN__u32`)
- `serialization/serialization_header.h` (for `GET_UUID_P`, `IS_DEALLOCATED_P`)
- `types/implemented/graphics_window_kind.h` (for `Graphics_Window_Kind` enum)
- `types/implemented/hitbox_manager_type.h` (for `Hitbox_Manager_Type` enum)
- `ui/ui_context.h` (for `get_p_ui_manager_by__uuid_from__ui_context`)
- `vectors.h` (for `Vector__3i32`, `VECTOR__3i32__OUT_OF_BOUNDS`)
- `collisions/hitbox_context.h` (for hitbox manager lookup)

## 1.3 Types

### 1.3.1 Graphics_Window (struct)

    typedef struct Graphics_Window_t {
        Serialization_Header _serialization_header;
        UI_Tile_Map__Wrapper ui_tile_map__wrapper;
        Vector__3i32 origin_of__gfx_window;
        Vector__3i32 position_of__gfx_window;
        Vector__3i32 position_of__gfx_window__minimum;
        Vector__3i32 position_of__gfx_window__maximum;
        Quantity__u32 width_of__graphics_window__u32;
        Quantity__u32 height_of__graphics_window__u32;
        f_PLATFORM_render_gfx_window f_PLATFORM_compose_gfx_window;
        f_PLATFORM_render_gfx_window f_PLATFORM_render_gfx_window;
        Camera *p_camera;
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window;
        Identifier__u32 graphics_window__parent__uuid;
        union {
            Identifier__u32 ui_tile_map__texture__uuid;
            Identifier__u32 tile_map__texture__uuid;
        };
        Identifier__u32 uuid_of__sprite_manager;
        Identifier__u32 uuid_of__ui_manager;
        Identifier__u32 uuid_of__hitbox_manager;
        Graphics_Window_Kind the_kind_of__window;
        Index__u8 priority_of__window;
        Graphics_Window_Flags__u8 graphics_window__flags;
    } Graphics_Window;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management. |
| `ui_tile_map__wrapper` | `UI_Tile_Map__Wrapper` | Tile map backing data for UI composition. |
| `origin_of__gfx_window` | `Vector__3i32` | Origin position (for relative positioning). |
| `position_of__gfx_window` | `Vector__3i32` | Current position. |
| `position_of__gfx_window__minimum` | `Vector__3i32` | Minimum scroll position. |
| `position_of__gfx_window__maximum` | `Vector__3i32` | Maximum scroll position. |
| `width_of__graphics_window__u32` | `Quantity__u32` | Window width in pixels. |
| `height_of__graphics_window__u32` | `Quantity__u32` | Window height in pixels. |
| `f_PLATFORM_compose_gfx_window` | `f_PLATFORM_render_gfx_window` | Platform compose callback. |
| `f_PLATFORM_render_gfx_window` | `f_PLATFORM_render_gfx_window` | Platform render callback. |
| `p_camera` | `Camera*` | Attached camera, or null. |
| `p_PLATFORM_gfx_window` | `PLATFORM_Graphics_Window*` | Platform-specific window handle. |
| `graphics_window__parent__uuid` | `Identifier__u32` | Parent window UUID, or `IDENTIFIER__UNKNOWN__u32`. |
| `ui_tile_map__texture__uuid` / `tile_map__texture__uuid` | `Identifier__u32` | Texture UUID for tile map rendering (union). |
| `uuid_of__sprite_manager` | `Identifier__u32` | Sprite manager UUID (owned if == window UUID). |
| `uuid_of__ui_manager` | `Identifier__u32` | UI manager UUID (owned if == window UUID). |
| `uuid_of__hitbox_manager` | `Identifier__u32` | Hitbox manager UUID (owned if == window UUID). |
| `the_kind_of__window` | `Graphics_Window_Kind` | Window kind discriminator. |
| `priority_of__window` | `Index__u8` | Priority for composition/rendering order. |
| `graphics_window__flags` | `Graphics_Window_Flags__u8` | State flags. |

### 1.3.2 Graphics_Window_Flags__u8 (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `GRAPHICS_WINDOW__FLAG__IS_ENABLED` | 0 | Window is active. |
| `GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY` | 1 | Needs recomposition. |
| `GRAPHICS_WINDOW__FLAG__IS_PLATFORM_PROVIDED` | 2 | Provided by platform, cannot be released. |

### 1.3.3 f_PLATFORM_render_gfx_window (function pointer)

    typedef void (*f_PLATFORM_render_gfx_window)(
            Game *p_game,
            Graphics_Window *p_gfx_window);

### 1.3.4 Resource Sharing Model

Graphics windows can **own** or **share** three resource managers. If the
manager UUID equals the window's own UUID, the window owns it. If the UUID
differs but is valid, the resource is shared (borrowed from another window).

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_graphics_window` | `(Graphics_Window*) -> void` | Initializes to deallocated empty state. |
| `initialize_graphics_window_as__allocated` | `(Graphics_Window*, PLATFORM_Graphics_Window*, Graphics_Window_Kind) -> void` | Initializes as allocated with platform handle and kind. |

### 1.4.2 Tile Map

| Function | Signature | Description |
|----------|-----------|-------------|
| `update_graphics_window__ui_tiles` | `(Graphics_Window*, const UI_Tile_Raw*, Quantity__u32) -> void` | Updates tile map data. |
| `set_graphics_window__ui_tile_map` | `(Graphics_Window*, UI_Tile_Map__Wrapper) -> void` | Sets the tile map wrapper. |

### 1.4.3 Resource Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_ui_manager_for__graphics_window` | `(Gfx_Context*, Graphics_Window*, Quantity__u16) -> UI_Manager*` | `UI_Manager*` | Allocates a UI manager and associates it with this window (ownership). |
| `allocate_sprite_manager_for__graphics_window` | `(Gfx_Context*, Graphics_Window*, Quantity__u32) -> void` | `void` | Allocates a sprite manager for this window. |
| `allocate_hitbox_manager_for__graphics_window` | `(Hitbox_Context*, Graphics_Window*, Hitbox_Manager_Type, Quantity__u32) -> void` | `void` | Allocates a hitbox manager for this window. |
| `allocate_p_sprite_from__graphics_window` | `(Game*, Graphics_Window*, Identifier__u32, Texture, Texture_Flags) -> Sprite*` | `Sprite*` | Allocates a sprite from this window's sprite manager. |

### 1.4.4 Resource Release

| Function | Signature | Description |
|----------|-----------|-------------|
| `release_graphics_window_ui_manager` | `(Game*, Graphics_Window*) -> void` | Releases the UI manager if owned. |
| `release_graphics_window_sprite_manager` | `(Game*, Graphics_Window*) -> void` | Releases the sprite manager if owned. |
| `release_graphics_window_hitbox_manager` | `(Game*, Graphics_Window*) -> void` | Releases the hitbox manager if owned. |

### 1.4.5 Resource Sharing

| Function | Signature | Description |
|----------|-----------|-------------|
| `share_sprite_manager_with__graphics_window` | `(Graphics_Window*, Identifier__u32) -> void` | Sets a shared (non-owned) sprite manager UUID. |
| `share_ui_manager_with__graphics_window` | `(Graphics_Window*, Identifier__u32) -> void` | Sets a shared (non-owned) UI manager UUID. |
| `share_hitbox_manager_with__graphics_window` | `(Graphics_Window*, Identifier__u32) -> void` | Sets a shared (non-owned) hitbox manager UUID. |

### 1.4.6 Position

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_position_3i32_of__graphics_window` | `(Game*, Graphics_Window*, Vector__3i32) -> void` | Sets position. |
| `set_position_3i32_of__graphics_window__relative_to` | `(Game*, Graphics_Window*, Vector__3i32 old, Vector__3i32 new) -> void` | Sets position relative to old/new origin. |

### 1.4.7 Reset and Composition

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `reset_graphics_window` | `(Game*, Graphics_Window*, bool) -> void` | `void` | Resets a window. For platform-provided windows when exiting a scene. |
| `is_graphics_window_in_need_of__composition` | `(Game*, Graphics_Window*) -> bool` | `bool` | True if window or its UI manager is dirty. |
| `set_graphics_window_as__no_longer_needing__composition` | `(Game*, Graphics_Window*) -> void` | `void` | Clears dirty flags. |

### 1.4.8 Default Handlers

| Function | Signature | Description |
|----------|-----------|-------------|
| `f_graphics_window__default_compose` | `(Game*, Graphics_Window*) -> void` | Default composition function. |
| `f_graphics_window__default_render` | `(Game*, Graphics_Window*) -> void` | Default rendering function. |

### 1.4.9 Ownership Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `does_graphics_window_own_a__sprite_manager` | `(Graphics_Window*) -> bool` | `bool` | True if window UUID == `uuid_of__sprite_manager` and UUID is valid. |
| `does_graphics_window_own_a__ui_manager` | `(Graphics_Window*) -> bool` | `bool` | Same pattern for UI manager. |
| `does_graphics_window_own_a__hitbox_manager` | `(Graphics_Window*) -> bool` | `bool` | Same pattern for hitbox manager. |
| `does_graphics_window_share_a__sprite_manager` | `(Graphics_Window*) -> bool` | `bool` | True if sprite manager UUID is valid but differs from window UUID. |
| `does_graphics_window_share_a__ui_manager` | `(Graphics_Window*) -> bool` | `bool` | Same pattern. |
| `does_graphics_window_share_a__hitbox_manager` | `(Graphics_Window*) -> bool` | `bool` | Same pattern. |

### 1.4.10 Sub-Component Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_ui_tile_map_from__graphics_window` | `(Graphics_Window*) -> UI_Tile_Map__Wrapper*` | `UI_Tile_Map__Wrapper*` | Returns pointer to tile map wrapper. Debug null-checked. |
| `get_p_ui_manager_from__graphics_window` | `(Game*, Graphics_Window*) -> UI_Manager*` | `UI_Manager*` | Looks up UI manager by UUID. Accessor chain: `p_game` -> `gfx_context` -> `ui_context` -> `get_p_ui_manager_by__uuid_from__ui_context`. Debug null-checked. |
| `is_graphics_window_with__ui_manager` | `(Game*, Graphics_Window*) -> bool` | `bool` | True if UI manager lookup returns non-null. |
| `get_p_sprite_manager_from__graphics_window` | `(Game*, Graphics_Window*) -> Sprite_Manager*` | `Sprite_Manager*` | Looks up sprite manager by UUID. Accessor chain: `p_game` -> `gfx_context` -> `sprite_context` -> `get_p_sprite_manager_by__uuid_from__sprite_context`. Debug null-checked. |
| `get_hitbox_manager_instance_from__graphics_window` | `(Game*, Graphics_Window*) -> Hitbox_Manager_Instance*` | `Hitbox_Manager_Instance*` | Looks up hitbox manager instance by UUID. |
| `get_pV_hitbox_manager_from__graphics_window` | `(Game*, Graphics_Window*) -> void*` | `void*` | Returns opaque hitbox manager pointer. |

### 1.4.11 Position Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_origin_3i32_of__graphics_window` | `(Graphics_Window*) -> Vector__3i32` | `Vector__3i32` | Returns origin. Debug null-checked. |
| `set_origin_3i32_of__graphics_window` | `(Graphics_Window*, Vector__3i32) -> void` | `void` | Sets origin. Debug null-checked. |
| `get_position_3i32_of__graphics_window` | `(Graphics_Window*) -> Vector__3i32` | `Vector__3i32` | Returns position. Debug null-checked. |
| `get_position_maximum_3i32_of__graphics_window` | `(Graphics_Window*) -> Vector__3i32` | `Vector__3i32` | Returns max scroll position. |
| `get_position_minimum_3i32_of__graphics_window` | `(Graphics_Window*) -> Vector__3i32` | `Vector__3i32` | Returns min scroll position. |

### 1.4.12 Parent/Child (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_parent_of__graphics_window` | `(Graphics_Window_Manager*, Graphics_Window*) -> Graphics_Window*` | `Graphics_Window*` | Looks up parent by `graphics_window__parent__uuid`. |
| `is_graphics_window_a__child_of__this_graphics_window` | `(Graphics_Window* child, Graphics_Window* parent) -> bool` | `bool` | True if child's parent UUID matches parent's UUID. |

### 1.4.13 Kind (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_kind_of__p_graphics_window` | `(Graphics_Window*) -> Graphics_Window_Kind` | `Graphics_Window_Kind` | Returns window kind. |
| `is_graphics_window_of__this_kind` | `(Graphics_Window*, Graphics_Window_Kind) -> bool` | `bool` | True if kind matches. |

### 1.4.14 Flags (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_graphics_window__enabled` | `(Graphics_Window*) -> bool` | `bool` | True if `IS_ENABLED` set. |
| `set_graphics_window_as__enabled` | `(Graphics_Window*) -> void` | `void` | Sets `IS_ENABLED`. |
| `set_graphics_window_as__disabled` | `(Graphics_Window*) -> void` | `void` | Clears `IS_ENABLED`. |
| `is_graphics_window__platform_provided` | `(Graphics_Window*) -> bool` | `bool` | True if `IS_PLATFORM_PROVIDED` set. |
| `set_graphics_window_as__platform_provided` | `(Graphics_Window*) -> void` | `void` | Sets `IS_PLATFORM_PROVIDED`. |
| `set_graphics_window_as__no_longer__platform_provided` | `(Graphics_Window*) -> void` | `void` | Clears `IS_PLATFORM_PROVIDED`. |
| `set_graphics_window_as__in_need_of__composition` | `(Graphics_Window*) -> void` | `void` | Sets `COMPOSE__DIRTY`. |

### 1.4.15 Camera (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_camera_from__graphics_window` | `(Graphics_Window*) -> Camera*` | `Camera*` | Returns camera pointer. |
| `set_p_camera_of__graphics_window` | `(Graphics_Window*, Camera*) -> void` | `void` | Sets camera pointer. |

### 1.4.16 Allocation State (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_graphics_window__allocated` | `(Graphics_Window*) -> bool` | `bool` | True if non-null and has non-null `p_PLATFORM_gfx_window`. Null-safe. |

### 1.4.17 Texture UUIDs (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_graphics_window__tile_map__texture` | `(Graphics_Window*, Identifier__u32) -> void` | `void` | Sets tile map texture UUID. |
| `get_uuid_of__tile_map__texture_from__gfx_window` | `(Graphics_Window*) -> Identifier__u32` | `Identifier__u32` | Returns tile map texture UUID. |
| `set_graphics_window__ui_tile_map__texture` | `(Graphics_Window*, Identifier__u32) -> void` | `void` | Sets UI tile map texture UUID. |
| `get_uuid_of__ui_tile_map__texture_from__gfx_window` | `(Graphics_Window*) -> Identifier__u32` | `Identifier__u32` | Returns UI tile map texture UUID. |

## 1.5 Agentic Workflow

### 1.5.1 Resource Sharing Model

Graphics windows can **own** or **share** three resource managers:
- `uuid_of__sprite_manager` — if equals window UUID, window owns it.
- `uuid_of__ui_manager` — if equals window UUID, window owns it.
- `uuid_of__hitbox_manager` — if equals window UUID, window owns it.

If the UUID differs from the window's own UUID but is valid, the resource
is shared (borrowed from another window).

### 1.5.2 Preconditions

- All debug-checked functions require non-null pointers.
- `is_graphics_window__allocated` is null-safe.

### 1.5.3 Error Handling

- Debug builds call `debug_error` on null pointer violations and return
  null/false/`VECTOR__3i32__OUT_OF_BOUNDS`/`IDENTIFIER__UNKNOWN__u32`.

## 1.6 Header Guard

`GRAPHICS_WINDOW_H`
