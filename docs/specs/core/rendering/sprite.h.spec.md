# 1. Specification: core/include/rendering/sprite.h

## 1.1 Overview

Defines operations on `Sprite` — the engine's representation of a renderable
animated image. A sprite wraps a platform-specific `PLATFORM_Sprite`, a
sampling texture, an output texture, animation state, and rendering flags.
Provides non-inline functions for animation polling and inline helpers for
flag management.

## 1.2 Dependencies

- `defines_weak.h` (forward declarations)
- `defines.h` (for `Sprite`, `Sprite_Flags`, `Sprite_Animation`, all flag macros)
- `platform.h` (for `PLATFORM_allocate_sprite`, `PLATFORM_release_sprite`)
- `rendering/texture.h` (for `Texture` operations)
- `serialization/serialization_header.h` (for `IS_DEALLOCATED_P` macro)
- `types/implemented/sprite_animation_group_kind.h` (for `Sprite_Animation_Group_Kind` enum)
- `types/implemented/sprite_animation_kind.h` (for `Sprite_Animation_Kind` enum)

## 1.3 Types

### 1.3.1 Sprite (struct)

    typedef struct Sprite_t {
        Serialization_Header _serialization_header;
        PLATFORM_Sprite *p_PLATFORM_sprite;
        Texture texture_for__sprite_to__sample;
        Texture texture_of__sprite;
        m_Sprite_Animation_Handler m_sprite_animation_handler;
        Sprite_Animation animation;
        Sprite_Animation_Group_Kind the_kind_of__sprite__animation_group;
        Index__u16 index_of__sprite_frame;
        Sprite_Kind the_kind_of__sprite;
        Sprite_Flags sprite_flags__u8;
        Direction__u8 direction__old__u8;
        Direction__u8 direction__delta__u8;
    } Sprite;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID for pool management. |
| `p_PLATFORM_sprite` | `PLATFORM_Sprite*` | Platform-specific sprite handle. |
| `texture_for__sprite_to__sample` | `Texture` | Source texture (sprite sheet). |
| `texture_of__sprite` | `Texture` | Output texture for this sprite instance. |
| `m_sprite_animation_handler` | `m_Sprite_Animation_Handler` | Per-frame animation callback. |
| `animation` | `Sprite_Animation` | Current animation state. |
| `the_kind_of__sprite__animation_group` | `Sprite_Animation_Group_Kind` | Animation group for subgroup lookup. |
| `index_of__sprite_frame` | `Index__u16` | Current frame index. |
| `the_kind_of__sprite` | `Sprite_Kind` | Sprite kind discriminator. |
| `sprite_flags__u8` | `Sprite_Flags` | Enabled, needs update, flipped flags. |
| `direction__old__u8` | `Direction__u8` | Previous direction (for delta calculation). |
| `direction__delta__u8` | `Direction__u8` | Direction change since last frame. |

### 1.3.2 Sprite_Flags (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `SPRITE_FLAG__BIT_IS_ENABLED` | 0 | Sprite is active and renderable. |
| `SPRITE_FLAG__BIT_IS_NEEDING_GRAPHICS_UPDATE` | 1 | Sprite needs platform graphics update. |
| `SPRITE_FLAG__BIT_IS_FLIPPED_X` | 2 | Sprite is horizontally flipped. |
| `SPRITE_FLAG__BIT_IS_FLIPPED_Y` | 3 | Sprite is vertically flipped. |

### 1.3.3 m_Sprite_Animation_Handler (function pointer)

    typedef void (*m_Sprite_Animation_Handler)(
            Sprite *p_this_sprite,
            Game *p_game,
            Sprite_Context *p_sprite_context);

### 1.3.4 Sprite_Animation_Group_Set (struct)

    typedef struct Sprite_Animation_Group_Set_t {
        Quantity__u8 quantity_of__columns_in__sprite_animation_group__u4 :4;
        Quantity__u8 quantity_of__rows_in__sprite_animation_group__u4    :4;
        Index__u8 index_of__sprite_animation_group_in__group_set_u8;
    } Sprite_Animation_Group_Set;

Expresses subgroups within the sprite's sample texture.

## 1.4 Functions

### 1.4.1 Animation

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_sprite_animation_handler__default` | `(Sprite*, Game*, Sprite_Context*) -> void` | Default animation handler. Advances timer and updates frame index. |
| `poll_sprite_for__animation` | `(Game*, Sprite*, Sprite_Context*) -> void` | Polls the sprite's animation handler. Called each frame for animated sprites. |
| `set_sprite_animation` | `(Sprite_Context*, Sprite*, Sprite_Animation_Kind) -> void` | Sets the sprite's current animation to the registered animation of the given kind. |

### 1.4.2 Allocation State (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite__deallocated` | `(Sprite*) -> bool` | `bool` | True if the sprite's serialization header indicates deallocation via `IS_DEALLOCATED_P`. |

### 1.4.3 Enabled State (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite__enabled` | `(Sprite*) -> bool` | `bool` | True if `IS_ENABLED` set. |
| `set_sprite_as__enabled` | `(Sprite*) -> bool` | `bool` | Sets `IS_ENABLED`. **Note:** returns `bool` (flags cast) — likely unintentional. |
| `set_sprite_as__disabled` | `(Sprite*) -> bool` | `bool` | Clears `IS_ENABLED`. **Note:** returns `bool` (flags cast) — likely unintentional. |

### 1.4.4 Graphics Update (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite__needing_graphics_update` | `(Sprite*) -> bool` | `bool` | True if `IS_NEEDING_GRAPHICS_UPDATE` set. |
| `set_sprite_as__needing_graphics_update` | `(Sprite*) -> bool` | `bool` | Sets `IS_NEEDING_GRAPHICS_UPDATE`. |
| `set_sprite_as__NOT_needing_graphics_update` | `(Sprite*) -> bool` | `bool` | Clears `IS_NEEDING_GRAPHICS_UPDATE`. |

### 1.4.5 Frame (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_frame_index_of__sprite` | `(Sprite*, Index__u8) -> void` | Sets the frame index and marks the sprite as needing a graphics update. |

### 1.4.6 Flipping (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite__flipped_x` | `(Sprite*) -> bool` | `bool` | True if `IS_FLIPPED_X` set. |
| `set_sprite_as__flipped_x` | `(Sprite*) -> bool` | `bool` | Sets `IS_FLIPPED_X`. |
| `set_sprite_as__NOT_flipped_x` | `(Sprite*) -> bool` | `bool` | Clears `IS_FLIPPED_X`. |
| `is_sprite__flipped_y` | `(Sprite*) -> bool` | `bool` | True if `IS_FLIPPED_Y` set. |
| `set_sprite_as__flipped_y` | `(Sprite*) -> bool` | `bool` | Sets `IS_FLIPPED_Y`. |
| `set_sprite_as__NOT_flipped_y` | `(Sprite*) -> bool` | `bool` | Clears `IS_FLIPPED_Y`. |

### 1.4.7 Animation Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_sprite_animation_from__sprite` | `(Sprite*) -> Sprite_Animation*` | `Sprite_Animation*` | Returns pointer to embedded animation. |
| `get_the_kind_of__sprite_animation_group_of__this_sprite` | `(Sprite*) -> Sprite_Animation_Group_Kind` | `Sprite_Animation_Group_Kind` | Returns the animation group kind. |

## 1.5 Agentic Workflow

### 1.5.1 Relationships

- Managed by `Sprite_Manager` (see `sprite_manager.h`).
- Platform sprite allocated via `PLATFORM_allocate_sprite`.
- Rendered via `PLATFORM_render_sprite`.
- Animation state driven by `Sprite_Context` (see `sprite_context.h`).
- UI elements can reference sprites via `set_ui_element__sprite`.

### 1.5.2 Preconditions

- All functions require non-null `p_sprite`.

## 1.6 Header Guard

`SPRITE_H`
