# 1. System Overview: Scene State Machine

## 1.1. Purpose

The scene system provides a high-level state machine for managing discrete
game states (e.g. title screen, gameplay, pause menu). Each state is
represented by a `Scene` struct containing load, enter, and unload handler
callbacks. The `Scene_Manager` drives transitions between scenes, ensuring
orderly teardown of the outgoing scene and setup of the incoming scene.

## 1.2. Architecture

### 1.2.1. Data Hierarchy

    Game
    +-- Scene_Manager
    |   +-- scenes[Scene_Kind__Unknown]          (fixed-size array of Scene slots)
    |   |   +-- Scene[0]  (Scene_Kind__None)
    |   |   |   +-- Serialization_Header
    |   |   |   +-- m_Load_Scene   m_load_scene_handler
    |   |   |   +-- m_Enter_Scene  m_enter_scene_handler
    |   |   |   +-- m_Unload_Scene m_unload_scene_handler
    |   |   |   +-- void *p_scene_data  --> Scene_Data__Game (or other)
    |   |   |   +-- Scene *p_parent_scene
    |   |   |   +-- bool is_active
    |   |   +-- Scene[1]  (first project-defined kind)
    |   |   +-- ...
    |   |   +-- Scene[N-1]  (last kind before Scene_Kind__Unknown)
    |   |
    |   +-- Scene *p_active_scene  --> points to one of scenes[0..N-1]

### 1.2.2. Key Types

| Type | Role |
|------|------|
| `Scene_Manager` | Top-level owner. Lives in `Game`. Holds the fixed-size scene array and a pointer to the currently active scene. Drives the state machine. |
| `Scene` | A single game state. Contains load/enter/unload handler callbacks, an opaque data pointer, and a parent scene pointer for hierarchical scene graphs. |
| `Scene_Kind` | Enumeration indexing into `Scene_Manager.scenes[]`. Extended by game projects. `Scene_Kind__Unknown` is the sentinel/array-size value. |
| `Scene_Data__Game` | A concrete scene data struct used by the gameplay scene. Contains HUD and typer animation timers. Accessed via inline accessors that cast `Scene.p_scene_data`. |
| `Serialization_Header` | UUID and struct size metadata embedded in each `Scene` for pool management and identification. |

### 1.2.3. Handler Function Pointer Types

| Type | Signature | Role |
|------|-----------|------|
| `m_Load_Scene` | `void (*)(Scene*, Game*)` | Called once when a scene is loaded (transition in). Prepares game state for the scene. |
| `m_Enter_Scene` | `void (*)(Scene*, Game*)` | Called each frame while the scene is active. Functions as the scene's main loop. |
| `m_Unload_Scene` | `void (*)(Scene*, Game*)` | Called once when a scene is unloaded (transition out). Cleans up game state. |

### 1.2.4. Limits

| Constraint | Determined By | Description |
|------------|---------------|-------------|
| Number of scene slots | `Scene_Kind__Unknown` | The sentinel value of the `Scene_Kind` enum. Adding entries before it increases the slot count. |
| Active scenes | 1 | Only one scene may be active at a time. |

## 1.3. State Machine

### 1.3.1. Transition Diagram

    [No Active Scene]
            |
            | set_active_scene_for__scene_manager(Kind_A)
            |
            v
    m_load_scene_handler(Kind_A)
            |
            v
    [Kind_A Active] <-- m_enter_scene_handler called each frame
            |
            | set_active_scene_for__scene_manager(Kind_B)
            |
            v
    m_unload_scene_handler(Kind_A)
            |
            v
    m_load_scene_handler(Kind_B)
            |
            v
    [Kind_B Active] <-- m_enter_scene_handler called each frame
            |
            | quit_scene_state_machine()
            |
            v
    m_unload_scene_handler(Kind_B)
            |
            v
    [No Active Scene]  (p_active_scene = NULL)

### 1.3.2. Transition Rules

- Transitioning to a new scene always unloads the current scene first
  (if one is active), then loads the new scene.
- `quit_scene_state_machine` unloads the current scene and sets
  `p_active_scene` to null, halting the state machine.
- A scene is considered valid if and only if its `m_enter_scene_handler`
  is non-null. The load and unload handlers are optional.

## 1.4. Lifecycle

### 1.4.1. Initialization

    initialize_scene_manager(&game.scene_manager);
        -> All Scene slots: handlers set to null, is_active = false,
           p_scene_data = NULL, p_parent_scene = NULL.
        -> p_active_scene = NULL.

### 1.4.2. Registration

Scenes are registered during game initialization, before any scene is
made active. The project provides a `register_scenes` function that
batch-registers all scenes:

    register_scenes(&game.scene_manager);

Internally, `register_scenes` calls per-scene registration functions
(e.g. `register_scene__main`) and/or calls
`register_scene_into__scene_manager` directly:

    register_scene_into__scene_manager(
        p_scene_manager,
        Scene_Kind__Gameplay,
        m_load__gameplay,
        m_enter__gameplay,
        m_unload__gameplay);

Registration overwrites any previously registered handlers for the given
`Scene_Kind` slot.

### 1.4.3. Activation

    set_active_scene_for__scene_manager(
        &game.scene_manager,
        Scene_Kind__Gameplay);

        -> If a scene is currently active, calls its m_unload_scene_handler.
        -> Calls the new scene's m_load_scene_handler.
        -> Sets p_active_scene to the new scene's slot.

### 1.4.4. Per-Frame Execution

Each frame, the game loop invokes the active scene's enter handler:

    Scene *p_active = get_p_active_scene_from__scene_manager(
        &game.scene_manager);
    if (p_active && is_scene__valid(p_active)) {
        p_active->m_enter_scene_handler(p_active, &game);
    }

### 1.4.5. Scene Data Access

Scene-specific data is stored via the opaque `p_scene_data` pointer.
Accessor functions cast this pointer to the appropriate type:

    Timer__u8 *p_hud_timer =
        get_hud_timer_from__scene__game(p_active_scene);

    Timer__u8 *p_typer_timer =
        get_typer_timer_from__scene__game(p_active_scene);

The lifetime of `p_scene_data` is managed by the scene's load and unload
handlers. Common patterns include pointing to static/global data or
dynamically allocating in the load handler and freeing in the unload
handler.

### 1.4.6. Shutdown

    quit_scene_state_machine(&game.scene_manager);
        -> Calls the active scene's m_unload_scene_handler (if any).
        -> Sets p_active_scene = NULL.

## 1.5. Scene Validity

A `Scene` is considered valid when `m_enter_scene_handler` is non-null.
This is the minimum requirement — a scene must have a main loop. The load
and unload handlers are optional and may be null if the scene requires no
setup or teardown.

    is_scene__valid(p_scene)  ->  p_scene->m_enter_scene_handler != NULL

The `poll_is__scene_active` function checks whether a given scene is the
currently active scene in the game's `Scene_Manager`:

    poll_is__scene_active(p_game, p_scene)
        -> p_scene == get_p_active_scene_from__scene_manager(...)

## 1.6. Scene_Kind Extension

The `Scene_Kind` enum is an **implemented type** — it ships with the engine
as a minimal default but is copied into game projects for extension. The
enum directly determines:

- The number of scene slots in `Scene_Manager.scenes[Scene_Kind__Unknown]`.
- The valid range of `Scene_Kind` values accepted by all `Scene_Manager`
  functions.

Extension rules:

- `Scene_Kind__None` must remain at value 0.
- `Scene_Kind__Unknown` must remain the final entry (sentinel).
- New scene kinds are added between `Scene_Kind__None` and
  `Scene_Kind__Unknown`.
- The `DEFINE_SCENE_KIND` guard macro must be defined to suppress the
  engine's fallback definition in `defines_weak.h`.

## 1.7. Hierarchical Scenes

Each `Scene` has a `p_parent_scene` pointer, enabling hierarchical scene
relationships. This allows scenes to reference a parent scene for
delegation or context. The engine does not enforce any particular
hierarchical behavior — the semantics of `p_parent_scene` are determined
by the game project's scene handler implementations.

## 1.8. Relationship to Game

The `Scene_Manager` lives within the `Game` struct and is accessed via
`get_p_scene_manager_from__game`. All scene handler callbacks receive
both the `Scene*` (self) and `Game*` (engine context), giving handlers
full access to the engine's subsystems (graphics, audio, world, entities,
etc.) through the `Game` struct.

## 1.9. Capacity Constraints

- Only **one scene** may be active at any time. The `Scene_Manager` does
  not support concurrent or stacked active scenes.
- The total number of registerable scenes is fixed at compile time by the
  `Scene_Kind__Unknown` sentinel value.
- Scene slots are statically allocated within the `Scene_Manager` — there
  is no dynamic allocation of `Scene` structs.
