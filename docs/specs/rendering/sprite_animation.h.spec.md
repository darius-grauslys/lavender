# Specification: core/include/rendering/sprite_animation.h

## Overview

Provides `static inline` helper functions for querying and mutating
`Sprite_Animation` flag state — specifically the looping and
direction-offset flags. Contains no non-inline functions.

## Dependencies

- `defines.h` (for `Sprite_Animation`, `Sprite_Animation_Flags__u3`, flag macros)

## Types

### Sprite_Animation (struct)

    typedef struct Sprite_Animation_t {
        Sprite_Animation_Kind the_kind_of_animation__this_sprite_has;
        Timer__u8 animation_timer__u8;
        Quantity__u8 sprite_animation__initial_frame__u8;
        Quantity__u8 sprite_animation__quantity_of__frames__u8;
        Quantity__u8 sprite_animation__ticks_per__frame__u5  :5;
        Sprite_Animation_Flags__u3 sprite_animation__flags__u3;
    } Sprite_Animation;

### Sprite_Animation_Flags__u3 (u8, 3 bits used)

| Flag | Bit | Description |
|------|-----|-------------|
| `SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING` | 0 | Animation plays once then stops. |
| `SPRITE_ANIMATION_FLAG__IS_OFFSET_BY__DIRECTION` | 1 | Frame index is offset by entity direction. |

## Functions

All functions are `static inline`.

### Looping

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite_animation__NOT_looping` | `(Sprite_Animation*) -> bool` | `bool` | True if `IS_NOT_LOOPING` set. |
| `is_sprite_animation__looping` | `(Sprite_Animation*) -> bool` | `bool` | True if `IS_NOT_LOOPING` NOT set. |
| `set_sprite_animation_as__looping` | `(Sprite_Animation*) -> void` | `void` | Clears `IS_NOT_LOOPING`. |
| `set_sprite_animation_as__NOT_looping` | `(Sprite_Animation*) -> void` | `void` | Sets `IS_NOT_LOOPING`. |

### Direction Offset

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sprite_animation__offset_by__direction` | `(Sprite_Animation*) -> bool` | `bool` | True if `IS_OFFSET_BY__DIRECTION` set. |
| `set_sprite_animation_as__offset_by__direction` | `(Sprite_Animation*) -> void` | `void` | Sets `IS_OFFSET_BY__DIRECTION`. |
| `set_sprite_animation_as__NOT_offset_by__direction` | `(Sprite_Animation*) -> void` | `void` | Clears `IS_OFFSET_BY__DIRECTION`. |

## Agentic Workflow

### Relationships

- `Sprite_Animation` is embedded in `Sprite` (at `sprite.animation`).
- Registered into `Sprite_Context` via `register_sprite_animation_into__sprite_context`.
- Driven by `poll_sprite_for__animation` (see `sprite.h`).

### Preconditions

- All functions require non-null `p_sprite_animation`.

## Header Guard

`SPRITE_ANIMATION_H`
