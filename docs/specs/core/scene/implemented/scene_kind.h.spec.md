# 1. Specification: core/include/types/implemented/scene_kind.h

## 1.1. Overview

Defines the `Scene_Kind` enumeration, which discriminates between the
different scenes available in the game. This file is an **implemented type**
— it ships with the engine as a default template but is not compiled as part
of the engine build process.

## 1.2. Deployment

This file resides at `core/include/types/implemented/scene_kind.h` within
the engine source tree. When a new game project is created via
`tools/lav_new_project`, the contents of all `implemented/` directories
under `core/` are copied into the corresponding location in the new project
directory. The project's copy is then included as part of the project's
build process, allowing game developers to extend the enum with
project-specific scene kinds.

The engine's `defines_weak.h` includes this file and checks for the
`DEFINE_SCENE_KIND` guard macro. If the macro is not defined (i.e. the
project has not provided its own definition), a minimal fallback is used.
To override the default, the project's copy must define `DEFINE_SCENE_KIND`
before the enum definition.

## 1.3. Guard Macro

    #define DEFINE_SCENE_KIND

When this macro is defined, the fallback definition in `defines_weak.h` is
suppressed. The project's `scene_kind.h` must define this macro to ensure
its definition takes precedence.

## 1.4. Default Definition

    #define DEFINE_SCENE_KIND

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Unknown
    } Scene_Kind;

| Enumerator | Value | Description |
|------------|-------|-------------|
| `Scene_Kind__None` | 0 | Default/empty scene. Reserved. |
| `Scene_Kind__Unknown` | 1 | Sentinel value. Must always be the last entry. Used as the array size for `Scene_Manager.scenes[]`. |

## 1.5. Extension Convention

Game projects extend this enum by adding new scene kinds between
`Scene_Kind__None` and `Scene_Kind__Unknown`:

    #ifndef IMPL_SCENE_KIND_H
    #define IMPL_SCENE_KIND_H

    #define DEFINE_SCENE_KIND

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Title_Screen,
        Scene_Kind__Gameplay,
        Scene_Kind__Pause_Menu,
        Scene_Kind__Unknown
    } Scene_Kind;

    #endif

### 1.5.1. Rules

- `Scene_Kind__None` must remain at value 0.
- `Scene_Kind__Unknown` must remain the final entry.
- The `DEFINE_SCENE_KIND` macro must be defined to suppress the engine's
  fallback definition in `defines_weak.h`.
- Adding entries increases the size of `Scene_Manager.scenes[]`
  accordingly.

## 1.6. Agentic Workflow

### 1.6.1. When to Modify

This file should be modified when a game project needs to add, remove, or
reorder scene kinds. It is modified in the **project directory**, not in
the engine source tree.

### 1.6.2. Relationship to Scene_Manager

The `Scene_Kind` enum directly determines:

- The number of scene slots in `Scene_Manager.scenes[Scene_Kind__Unknown]`.
- The valid range of `Scene_Kind` values accepted by
  `register_scene_into__scene_manager`, `get_p_scene_from__scene_manager`,
  and `set_active_scene_for__scene_manager`.

### 1.6.3. Relationship to defines_weak.h

The inclusion chain is:

    defines_weak.h
        --> #include <types/implemented/scene_kind.h>
        --> #ifndef DEFINE_SCENE_KIND
        -->     // fallback definition used
        --> #endif

If the project provides its own `scene_kind.h` with `DEFINE_SCENE_KIND`
defined, the fallback is skipped and the project's definition is used.

### 1.6.4. Preconditions

- `Scene_Kind__Unknown` must be the last enumerator.
- `Scene_Kind__None` must be 0.

### 1.6.5. Postconditions

- After modification and rebuild, `Scene_Manager` will have the correct
  number of scene slots for all defined scene kinds.
