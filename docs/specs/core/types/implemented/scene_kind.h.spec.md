# 1 Specification: core/include/types/implemented/scene_kind.h

## 1.1 Overview

Template header that defines the `Scene_Kind` enum — the set of game scenes
(menus, gameplay states, etc.) available in the game. This file is copied to
the game project directory by `tools/lav_new_project` and is meant to be
extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_SCENE_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Scene_Kind (enum)

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Unknown
    } Scene_Kind;

| Value | Description |
|-------|-------------|
| `Scene_Kind__None` | No scene / sentinel. |
| `Scene_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/scene_kind.h>
    #ifndef DEFINE_SCENE_KIND
    typedef enum Scene_Kind { ... } Scene_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Main_Menu,
        Scene_Kind__Game,
        Scene_Kind__Pause,
        Scene_Kind__Unknown
    } Scene_Kind;

### 1.6.2 Constraints

- `Scene_Kind__None` must remain first (value 0).
- `Scene_Kind__Unknown` must remain last.
- `Scene_Kind__Unknown` is used for array sizing in
  `Scene_Manager.scenes[Scene_Kind__Unknown]`.
- The `#define DEFINE_SCENE_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_SCENE_KIND_H`
