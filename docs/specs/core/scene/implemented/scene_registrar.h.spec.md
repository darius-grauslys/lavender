# Specification: core/include/scene/implemented/scene_registrar.h

## Overview

Declares the `register_scenes` function — the conventional entry point for
batch-registering all game scenes into a `Scene_Manager`. This file is an
**implemented type** header — it ships with the engine as a default template
but is not compiled as part of the engine build process.

## Deployment

This file resides at `core/include/scene/implemented/scene_registrar.h`
within the engine source tree. When a new game project is created via
`tools/lav_new_project`, the contents of all `implemented/` directories
under `core/` are copied into the corresponding location in the new project
directory. The project's copy is then included as part of the project's
build process.

The game project is expected to provide the implementation of
`register_scenes` in a corresponding `.c` file. This implementation
registers all project-specific scenes into the scene manager.

## Dependencies

- `defines_weak.h` (for `Scene_Manager` forward declaration)

## Functions

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_scenes` | `(Scene_Manager*) -> void` | Registers all game scenes into the provided `Scene_Manager`. Called during game initialization, after `initialize_scene_manager` and before any scene is made active. |

## Agentic Workflow

### Implementation Pattern

The game project implements `register_scenes` to register each scene kind
with its load, enter, and unload handlers:

    void register_scenes(Scene_Manager *p_scene_manager) {
        register_scene__main(p_scene_manager);

        register_scene_into__scene_manager(
                p_scene_manager,
                Scene_Kind__Title_Screen,
                m_load__title_screen,
                m_enter__title_screen,
                m_unload__title_screen);

        // register additional scenes...
    }

### Initialization Sequence

    initialize_scene_manager(p_scene_manager);
    register_scenes(p_scene_manager);
    set_active_scene_for__scene_manager(p_scene_manager, Scene_Kind__Title_Screen);

### Preconditions

- `p_scene_manager` must be non-null and previously initialized via
  `initialize_scene_manager`.
- All `Scene_Kind` values used in registration must be valid (less than
  `Scene_Kind__Unknown`) and defined in the project's `scene_kind.h`.

### Postconditions

- After `register_scenes` returns, all game scenes are registered and
  ready to be activated via `set_active_scene_for__scene_manager`.
