# Specification: core/include/types/implemented/scene_kind.h

## Overview

Template header that defines the `Scene_Kind` enum — the set of game scenes
(menus, gameplay states, etc.) available in the game. This file is copied to
the game project directory by `tools/lav_new_project` and is meant to be
extended by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_SCENE_KIND` is not defined after the
`#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Scene_Kind (enum)

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Unknown
    } Scene_Kind;

| Value | Description |
|-------|-------------|
| `Scene_Kind__None` | No scene / sentinel. |
| `Scene_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/scene_kind.h>
    #ifndef DEFINE_SCENE_KIND
    typedef enum Scene_Kind { ... } Scene_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Main_Menu,
        Scene_Kind__Game,
        Scene_Kind__Pause,
        Scene_Kind__Unknown
    } Scene_Kind;

### Constraints

- `Scene_Kind__None` must remain first (value 0).
- `Scene_Kind__Unknown` must remain last.
- `Scene_Kind__Unknown` is used for array sizing in
  `Scene_Manager.scenes[Scene_Kind__Unknown]`.
- The `#define DEFINE_SCENE_KIND` line must not be removed.

## Header Guard

`IMPL_SCENE_KIND_H`
