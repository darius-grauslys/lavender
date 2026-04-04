# Specification: core/include/scene/scene.h

## Overview

Provides initialization and basic query utilities for the `Scene` struct —
the engine's unit of high-level game state (e.g. title screen, gameplay,
pause menu). Each `Scene` encapsulates load, enter (main loop), and unload
handlers that the `Scene_Manager` drives as a state machine.

## Dependencies

- `defines.h` (for `Scene`, `Scene_Manager`, `Game`, `m_Enter_Scene`)
- `game.h` (for `get_p_scene_manager_from__game`)

## Types

### Scene (struct)

Defined in `defines.h`:

    typedef struct Scene_t {
        Serialization_Header _serialization_header;
        Scene *p_parent_scene;
        m_Load_Scene m_load_scene_handler;
        m_Enter_Scene m_enter_scene_handler;
        m_Unload_Scene m_unload_scene_handler;
        void *p_scene_data;
        bool is_active;
    } Scene;

| Field | Type | Description |
|-------|------|-------------|
| `_serialization_header` | `Serialization_Header` | UUID and struct size for pool management. |
| `p_parent_scene` | `Scene*` | Optional pointer to a parent scene for hierarchical scene graphs. |
| `m_load_scene_handler` | `m_Load_Scene` | Called once when the scene is loaded. Prepares `Game` for scene entry. |
| `m_enter_scene_handler` | `m_Enter_Scene` | Called each frame while the scene is active. Functions as the main loop. |
| `m_unload_scene_handler` | `m_Unload_Scene` | Called once when the scene is unloaded. Cleans up `Game` after scene exit. |
| `p_scene_data` | `void*` | Opaque pointer to scene-specific data (e.g. `Scene_Data__Game`). |
| `is_active` | `bool` | Whether this scene is currently active. |

### Handler Signatures

    typedef void (*m_Load_Scene)(Scene *p_this_scene, Game *p_game);
    typedef void (*m_Enter_Scene)(Scene *p_this_scene, Game *p_game);
    typedef void (*m_Unload_Scene)(Scene *p_this_scene, Game *p_game);

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_scene` | `(Scene*) -> void` | Zeroes all handler pointers, sets `p_parent_scene` and `p_scene_data` to null, and sets `is_active` to false. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_scene__valid` | `(Scene*) -> bool` | `bool` | Returns true if `m_enter_scene_handler` is non-null. A scene without an enter handler is considered invalid/unregistered. |
| `poll_is__scene_active` | `(Game*, Scene*) -> bool` | `bool` | Returns true if the given scene is the currently active scene in the game's `Scene_Manager`. Compares against `p_active_scene`. |

## Agentic Workflow

### Scene Lifecycle

    [Unregistered] --> register_scene_into__scene_manager --> [Registered/Inactive]
                                                                     |
                                                      set_active_scene_for__scene_manager
                                                                     |
                                                              m_load_scene_handler
                                                                     |
                                                                 [Active]
                                                                     |
                                                        m_enter_scene_handler (each frame)
                                                                     |
                                                      set_active_scene_for__scene_manager
                                                        (to a different scene)
                                                                     |
                                                             m_unload_scene_handler
                                                                     |
                                                             [Registered/Inactive]

### Validity Convention

A scene is considered valid if and only if it has a non-null
`m_enter_scene_handler`. The `m_load_scene_handler` and
`m_unload_scene_handler` are optional — a scene may have no setup or
teardown requirements.

### Scene Data Convention

The `p_scene_data` pointer is opaque and its lifetime is managed by the
scene's load and unload handlers. Common patterns:

- **Static data**: Point to a global or static struct (e.g. `Scene_Data__Game`).
- **Dynamic data**: Allocate in `m_load_scene_handler`, free in
  `m_unload_scene_handler`.

### Preconditions

- `is_scene__valid`: requires a non-null `p_scene`.
- `poll_is__scene_active`: requires a non-null `p_game` and `p_scene`.

### Postconditions

- After `initialize_scene`: all handlers are null, `is_active` is false,
  `p_parent_scene` and `p_scene_data` are null.
- After `poll_is__scene_active` returns true: the scene is the current
  active scene in the game's scene manager.
