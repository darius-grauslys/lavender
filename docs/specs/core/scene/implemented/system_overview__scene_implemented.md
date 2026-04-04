# System Overview: Implemented Scene Types and Registration

## Purpose

The `implemented/` directory under the scene system contains
project-extensible types and registration entry points. These files ship
with the engine as default templates but are **not compiled as part of the
engine build process**. When a new game project is created via
`tools/lav_new_project`, the contents of all `implemented/` directories
are copied into the corresponding location in the new project directory.
The project's copies are then compiled as part of the project's build,
allowing game developers to extend enumerations and provide
project-specific scene registration logic.

## Architecture

### Deployment Flow

    Engine Source Tree                      Project Directory
    ========================               ========================
    core/include/types/                    project/include/types/
      implemented/                           implemented/
        scene_kind.h          -- copy -->      scene_kind.h
                                               (extended by project)

    core/include/scene/                    project/include/scene/
      implemented/                           implemented/
        scene_registrar.h     -- copy -->      scene_registrar.h
        scene__main.h         -- copy -->      scene__main.h

    (no engine .c files)                   project/source/scene/
                                             implemented/
                                               scene_registrar.c
                                               scene__main.c
                                               (provided by project)

### Guard Macro System

The engine's `defines_weak.h` includes `scene_kind.h` and checks for a
guard macro. If the project has not provided its own definition, a minimal
fallback is used:

    defines_weak.h
        --> #include <types/implemented/scene_kind.h>
        --> #ifndef DEFINE_SCENE_KIND
        -->     typedef enum Scene_Kind {
        -->         Scene_Kind__None = 0,
        -->         Scene_Kind__Unknown
        -->     } Scene_Kind;
        --> #endif

When the project's copy defines `DEFINE_SCENE_KIND`, the fallback is
suppressed and the project's extended definition takes precedence.

### Key Components

| Component | File | Role |
|-----------|------|------|
| `Scene_Kind` | `types/implemented/scene_kind.h` | Enumeration of all scene kinds. Determines `Scene_Manager.scenes[]` array size. Extended by game projects. |
| `register_scenes` | `scene/implemented/scene_registrar.h` | Batch registration entry point. Called during game initialization to register all project scenes into the `Scene_Manager`. |
| `register_scene__main` | `scene/implemented/scene__main.h` | Registers the main/primary scene. Called from within `register_scenes`. |

## Scene_Kind Enumeration

### Default Definition

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Unknown
    } Scene_Kind;

| Enumerator | Value | Description |
|------------|-------|-------------|
| `Scene_Kind__None` | 0 | Default/empty scene. Reserved. |
| `Scene_Kind__Unknown` | (last) | Sentinel value. Always the final entry. Used as the array size for `Scene_Manager.scenes[]`. |

### Extension Pattern

Game projects add new scene kinds between `Scene_Kind__None` and
`Scene_Kind__Unknown`:

    #define DEFINE_SCENE_KIND

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Title_Screen,
        Scene_Kind__Gameplay,
        Scene_Kind__Pause_Menu,
        Scene_Kind__Unknown
    } Scene_Kind;

### Extension Rules

- `Scene_Kind__None` must remain at value 0.
- `Scene_Kind__Unknown` must remain the final entry.
- `DEFINE_SCENE_KIND` must be defined to suppress the engine fallback.
- Adding entries increases `Scene_Manager.scenes[]` size accordingly.

## Registration System

### Initialization Sequence

    initialize_scene_manager(p_scene_manager);
    register_scenes(p_scene_manager);
    set_active_scene_for__scene_manager(p_scene_manager, Scene_Kind__Title_Screen);

### register_scenes

Declared in `scene_registrar.h`. The game project provides the
implementation. This function is the single entry point for registering
all game scenes:

    void register_scenes(Scene_Manager *p_scene_manager) {
        register_scene__main(p_scene_manager);
        // register additional scenes...
    }

**Preconditions:**
- `p_scene_manager` must be non-null and previously initialized via
  `initialize_scene_manager`.
- All `Scene_Kind` values used in registration must be valid (less than
  `Scene_Kind__Unknown`).

**Postconditions:**
- All game scenes are registered and ready to be activated via
  `set_active_scene_for__scene_manager`.

### register_scene__main

Declared in `scene__main.h`. The game project provides the
implementation. Registers the main/primary scene's load, enter, and
unload handlers into the `Scene_Manager`:

    void register_scene__main(Scene_Manager *p_scene_manager);

**Preconditions:**
- `p_scene_manager` must be non-null and previously initialized.
- The `Scene_Kind` used internally must be valid and defined in the
  project's `scene_kind.h`.

**Postconditions:**
- The main scene is registered and can be activated via
  `set_active_scene_for__scene_manager`.

### Modular Registration Convention

The engine encourages a pattern where each scene has its own
`register_scene__<name>` function declared in a corresponding
`scene__<name>.h` header under `implemented/`. This allows game projects
to:

- Add new scenes by creating new `scene__<name>.h` / `.c` pairs.
- Remove scenes by not calling their registration function.
- Keep scene handler implementations organized per-scene.

### Adding a New Scene

To add a new scene to a game project:

1. **Extend `Scene_Kind`** — Add a new enumerator (e.g.
   `Scene_Kind__Inventory`) before `Scene_Kind__Unknown` in the
   project's `scene_kind.h`.

2. **Create registration header** — Create
   `scene/implemented/scene__inventory.h` declaring
   `register_scene__inventory(Scene_Manager*)`.

3. **Create registration source** — Create
   `scene/implemented/scene__inventory.c` implementing
   `register_scene__inventory`, which calls
   `register_scene_into__scene_manager` with the appropriate handlers.

4. **Register in `register_scenes`** — Add a call to
   `register_scene__inventory(p_scene_manager)` in the project's
   `register_scenes` implementation.

## Relationship to Scene_Manager

The implemented types directly affect `Scene_Manager` behavior:

| Implemented Component | Scene_Manager Impact |
|-----------------------|----------------------|
| `Scene_Kind` enum entries | Determines `scenes[]` array size and valid index range. |
| `register_scenes` | Populates `scenes[]` slots with handler callbacks. |
| `register_scene__main` | Populates one specific `scenes[]` slot. |

The `Scene_Manager` itself is an engine type — it is not an implemented
type and is not copied into game projects. Only the scene kinds and
registration functions are project-extensible.

## Relationship to defines_weak.h

The inclusion chain for `Scene_Kind`:

    defines_weak.h
        --> #include <types/implemented/scene_kind.h>
        --> #ifndef DEFINE_SCENE_KIND
        -->     // fallback: Scene_Kind__None, Scene_Kind__Unknown only
        --> #endif

This pattern ensures that:
- The engine can compile with a minimal `Scene_Kind` even without a
  game project.
- Game projects override the enum by defining `DEFINE_SCENE_KIND` in
  their copy of `scene_kind.h`.
- No source code changes are needed in the engine to support
  project-specific scene kinds.
