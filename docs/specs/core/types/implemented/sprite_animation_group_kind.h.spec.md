# 1 Specification: core/include/types/implemented/sprite_animation_group_kind.h

## 1.1 Overview

Template header that defines the `Sprite_Animation_Group_Kind` enum — the
set of sprite animation group types available in the game. Animation groups
define subregions within a sprite sheet for organizing related animations.
This file is copied to the game project directory by `tools/lav_new_project`
and is meant to be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_SPRITE_ANIMATION_GROUP_KIND` is not
defined after the `#include`, `defines_weak.h` falls back to a built-in
default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Sprite_Animation_Group_Kind (enum)

    typedef enum Sprite_Animation_Group_Kind {
        Sprite_Animation_Group_Kind__None,
        Sprite_Animation_Group_Kind__Unknown
    } Sprite_Animation_Group_Kind;

| Value | Description |
|-------|-------------|
| `Sprite_Animation_Group_Kind__None` | No group / sentinel. |
| `Sprite_Animation_Group_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/sprite_animation_group_kind.h>
    #ifndef DEFINE_SPRITE_ANIMATION_GROUP_KIND
    typedef enum Sprite_Animation_Group_Kind { ... } Sprite_Animation_Group_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Sprite_Animation_Group_Kind {
        Sprite_Animation_Group_Kind__None,
        Sprite_Animation_Group_Kind__Player,
        Sprite_Animation_Group_Kind__Skeleton,
        Sprite_Animation_Group_Kind__Unknown
    } Sprite_Animation_Group_Kind;

### 1.6.2 Constraints

- `Sprite_Animation_Group_Kind__None` must remain first.
- `Sprite_Animation_Group_Kind__Unknown` must remain last.
- `Sprite_Animation_Group_Kind__Unknown` is used for array sizing in
  `Sprite_Context.sprite_animation_groups[Sprite_Animation_Group_Kind__Unknown]`.
- Groups are registered via `register_sprite_animation_group_into__sprite_context`.
- The `#define DEFINE_SPRITE_ANIMATION_GROUP_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_SPRITE_ANIMATION_GROUP_KIND_H`
