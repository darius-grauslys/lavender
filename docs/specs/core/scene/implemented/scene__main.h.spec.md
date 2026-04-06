# 1. Specification: core/include/scene/implemented/scene__main.h

## 1.1. Overview

Declares the `register_scene__main` function, which registers the
main/primary scene into the `Scene_Manager`. This file is an **implemented
type** header — it ships with the engine as a default template but is not
compiled as part of the engine build process.

## 1.2. Deployment

This file resides at `core/include/scene/implemented/scene__main.h` within
the engine source tree. When a new game project is created via
`tools/lav_new_project`, the contents of all `implemented/` directories
under `core/` are copied into the corresponding location in the new project
directory. The project's copy is then included as part of the project's
build process.

The game project is expected to provide the implementation of
`register_scene__main` in a corresponding `.c` file. This function is
typically called from within `register_scenes` (see `scene_registrar.h`).

## 1.3. Dependencies

- `defines.h` (for `Scene_Manager`)

## 1.4. Functions

### 1.4.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_scene__main` | `(Scene_Manager*) -> void` | Registers the main scene's load, enter, and unload handlers into the `Scene_Manager`. The specific `Scene_Kind` used is determined by the game project. |

## 1.5. Agentic Workflow

### 1.5.1. Usage Pattern

`register_scene__main` is intended to be called from within
`register_scenes` as part of the batch registration of all game scenes:

    void register_scenes(Scene_Manager *p_scene_manager) {
        register_scene__main(p_scene_manager);
        // register other scenes...
    }

This pattern allows each scene to encapsulate its own registration logic
in a dedicated function, keeping `register_scenes` clean and modular.

### 1.5.2. Modular Scene Registration Convention

The engine encourages a pattern where each scene has its own
`register_scene__<name>` function declared in a corresponding
`scene__<name>.h` header under `implemented/`. This allows game projects
to:

- Add new scenes by creating new `scene__<name>.h` / `.c` pairs.
- Remove scenes by simply not calling their registration function.
- Keep scene handler implementations organized per-scene.

### 1.5.3. Preconditions

- `p_scene_manager` must be non-null and previously initialized via
  `initialize_scene_manager`.
- The `Scene_Kind` used internally by this function must be valid and
  defined in the project's `scene_kind.h`.

### 1.5.4. Postconditions

- After `register_scene__main` returns, the main scene is registered in
  the `Scene_Manager` and can be activated via
  `set_active_scene_for__scene_manager`.
