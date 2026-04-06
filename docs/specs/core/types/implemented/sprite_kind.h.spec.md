# 1 Specification: core/include/types/implemented/sprite_kind.h

## 1.1 Overview

Template header that defines the `Sprite_Kind` enum — the set of sprite
types available in the game. This file is copied to the game project
directory by `tools/lav_new_project` and is meant to be extended by the
engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_SPRITE_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Sprite_Kind (enum)

    typedef enum Sprite_Kind {
        Sprite_Kind__None,
        Sprite_Kind__Unknown
    } Sprite_Kind;

| Value | Description |
|-------|-------------|
| `Sprite_Kind__None` | No sprite / sentinel. |
| `Sprite_Kind__Unknown` | End-of-enum sentinel. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/sprite_kind.h>
    #ifndef DEFINE_SPRITE_KIND
    typedef enum Sprite_Kind { ... } Sprite_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Sprite_Kind {
        Sprite_Kind__None,
        Sprite_Kind__Player,
        Sprite_Kind__Enemy,
        Sprite_Kind__Projectile,
        Sprite_Kind__Unknown
    } Sprite_Kind;

### 1.6.2 Constraints

- `Sprite_Kind__None` must remain first (value 0).
- `Sprite_Kind__Unknown` must remain last.
- Stored in `Sprite.the_kind_of__sprite`.
- The `#define DEFINE_SPRITE_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_SPRITE_KIND_H`
