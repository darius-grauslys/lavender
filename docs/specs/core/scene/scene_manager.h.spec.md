# Specification: core/include/scene/scene_manager.h

## Overview

Provides initialization, registration, lookup, and active-scene management
for the `Scene_Manager` — the engine's scene state machine driver. The
`Scene_Manager` holds a fixed-size array of `Scene` slots indexed by
`Scene_Kind` and maintains a pointer to the currently active scene.

## Dependencies

- `defines.h` (for `Scene_Manager`, `Scene`, `Scene_Kind`,
  `m_Load_Scene`, `m_Enter_Scene`, `m_Unload_Scene`)
- `defines_weak.h` (forward declarations)

## Types

### Scene_Manager (struct)

Defined in `defines.h`:

    typedef struct Scene_Manager_t {
        Scene scenes[Scene_Kind__Unknown];
        Scene *p_active_scene;
    } Scene_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `scenes` | `Scene[Scene_Kind__Unknown]` | Fixed-size array of scene slots. Indexed by `Scene_Kind`. The array size is determined by the `Scene_Kind__Unknown` sentinel value. |
| `p_active_scene` | `Scene*` | Pointer to the currently active scene, or null if no scene is active. |

### Scene_Kind (enum)

Defined via `types/implemented/scene_kind.h`. The default (engine-shipped)
definition is:

    typedef enum Scene_Kind {
        Scene_Kind__None = 0,
        Scene_Kind__Unknown
    } Scene_Kind;

This file is an **implemented type** — it is not part of the engine build
process directly. It is copied by `tools/lav_new_project` into a new game
project directory, where it is then included as part of the project's build.
This keeps the default representation packaged with the engine and deployed
on project creation via the tooling. Game projects extend this enum to
define their own scene kinds (e.g. `Scene_Kind__Title_Screen`,
`Scene_Kind__Gameplay`, etc.), ensuring `Scene_Kind__Unknown` remains the
final sentinel value.

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_scene_manager` | `(Scene_Manager*) -> void` | Initializes all scene slots via `initialize_scene` and sets `p_active_scene` to null. |

### Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_scene_into__scene_manager` | `(Scene_Manager*, Scene_Kind, m_Load_Scene, m_Enter_Scene, m_Unload_Scene) -> void` | Registers a scene's handlers into the slot indexed by the given `Scene_Kind`. Overwrites any previously registered handlers for that slot. |

### Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_scene_from__scene_manager` | `(Scene_Manager*, Scene_Kind) -> Scene*` | `Scene*` | Returns a pointer to the scene slot for the given `Scene_Kind`. |
| `get_p_active_scene_from__scene_manager` | `(Scene_Manager*) -> Scene*` | `Scene*` | Returns `p_active_scene`. (static inline) |

### Active Scene Management

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_active_scene_for__scene_manager` | `(Scene_Manager*, Scene_Kind) -> void` | Transitions to a new active scene. If a scene is currently active, its `m_unload_scene_handler` is called. The new scene's `m_load_scene_handler` is then called, and `p_active_scene` is updated. |
| `quit_scene_state_machine` | `(Scene_Manager*) -> void` | Unloads the current active scene (if any) and sets `p_active_scene` to null, effectively stopping the scene state machine. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_p_scene_the__active_scene_in__scene_manager` | `(Scene_Manager*, Scene*) -> bool` | `bool` | Returns true if the given scene pointer equals `p_active_scene`. |

## Agentic Workflow

### Scene State Machine

The `Scene_Manager` operates as a simple state machine:

    [No Active Scene] --> set_active_scene_for__scene_manager(Kind_A)
                                    |
                          m_load_scene_handler (Kind_A)
                                    |
                              [Kind_A Active]
                                    |
                          m_enter_scene_handler (each frame)
                                    |
                    set_active_scene_for__scene_manager(Kind_B)
                                    |
                          m_unload_scene_handler (Kind_A)
                                    |
                          m_load_scene_handler (Kind_B)
                                    |
                              [Kind_B Active]
                                    |
                          m_enter_scene_handler (each frame)
                                    |
                      quit_scene_state_machine
                                    |
                          m_unload_scene_handler (Kind_B)
                                    |
                            [No Active Scene]

### Registration Pattern

Scenes are typically registered during game initialization, before any
scene is made active. The `register_scenes` function (declared in
`scene_registrar.h`) is the conventional entry point for batch
registration:

    initialize_scene_manager(p_scene_manager);
    register_scenes(p_scene_manager);  // registers all game scenes
    set_active_scene_for__scene_manager(p_scene_manager, Scene_Kind__Title);

### Scene_Kind Extension

The `Scene_Kind` enum determines the number of scene slots available.
When extending `Scene_Kind` in a game project:

- Add new scene kinds before `Scene_Kind__Unknown`.
- `Scene_Kind__Unknown` must always be the last entry — it serves as
  the array size sentinel for `scenes[Scene_Kind__Unknown]`.
- `Scene_Kind__None` (value 0) is reserved as the default/empty scene.

### Preconditions

- `initialize_scene_manager`: requires a non-null `Scene_Manager*`.
- `register_scene_into__scene_manager`: `Scene_Kind` must be less than
  `Scene_Kind__Unknown`.
- `set_active_scene_for__scene_manager`: the scene for the given
  `Scene_Kind` should have been registered (i.e. `is_scene__valid`
  should return true). Behavior when setting an unregistered scene as
  active is undefined.
- `get_p_scene_from__scene_manager`: `Scene_Kind` must be less than
  `Scene_Kind__Unknown`.

### Postconditions

- After `initialize_scene_manager`: all scene slots are initialized
  (handlers null, `is_active` false), `p_active_scene` is null.
- After `set_active_scene_for__scene_manager`: the previous scene (if
  any) has been unloaded, the new scene has been loaded, and
  `p_active_scene` points to the new scene's slot.
- After `quit_scene_state_machine`: the previous scene (if any) has
  been unloaded, and `p_active_scene` is null.

### Error Handling

- Out-of-bounds `Scene_Kind` values (>= `Scene_Kind__Unknown`) will
  result in array out-of-bounds access. Debug builds should guard
  against this.
