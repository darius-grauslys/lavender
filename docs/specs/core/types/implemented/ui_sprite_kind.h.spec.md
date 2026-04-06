# 1 Specification: core/include/types/implemented/ui_sprite_kind.h

## 1.1 Overview

Template header that defines the `UI_Sprite_Kind` enum — the set of UI
sprite types available for sprite-based UI rendering. This file is copied
to the game project directory by `tools/lav_new_project` and is meant to
be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_UI_SPRITE_KIND` is not defined after
the `#include`, `defines_weak.h` falls back to a built-in default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 UI_Sprite_Kind (enum)

    typedef enum UI_Sprite_Kind {
        UI_Sprite_Kind__None = 0,
        UI_Sprite_Kind__8x8,
        UI_Sprite_Kind__16x16
            = UI_Sprite_Kind__8x8,
        UI_Sprite_Kind__32x32
            = UI_Sprite_Kind__16x16,
        UI_Sprite_Kind__Unknown = UI_Sprite_Kind__32x32
    } UI_Sprite_Kind;

| Value | Description |
|-------|-------------|
| `UI_Sprite_Kind__None` | No sprite / sentinel. |
| `UI_Sprite_Kind__8x8` | 8x8 pixel UI sprite. |
| `UI_Sprite_Kind__16x16` | 16x16 pixel UI sprite. Aliased to `8x8` by default. |
| `UI_Sprite_Kind__32x32` | 32x32 pixel UI sprite. Aliased to `16x16` by default. |
| `UI_Sprite_Kind__Unknown` | End-of-enum sentinel. Aliased to `32x32` by default. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/ui_sprite_kind.h>
    #ifndef DEFINE_UI_SPRITE_KIND
    typedef enum UI_Sprite_Kind { ... } UI_Sprite_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

Remove the aliases and add distinct sizes:

    typedef enum UI_Sprite_Kind {
        UI_Sprite_Kind__None = 0,
        UI_Sprite_Kind__8x8,
        UI_Sprite_Kind__16x16,
        UI_Sprite_Kind__32x32,
        UI_Sprite_Kind__64x64,
        UI_Sprite_Kind__Unknown
    } UI_Sprite_Kind;

### 1.6.2 Constraints

- The default template aliases all sizes together, meaning only one sprite
  allocation path exists. Games should break the aliases if they need
  distinct sprite sizes.
- Used by platform-specific sprite allocation (e.g. `NDS_allocate_sprite_for__ui`).
- The `#define DEFINE_UI_SPRITE_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_UI_SPRITE_KIND_H`
