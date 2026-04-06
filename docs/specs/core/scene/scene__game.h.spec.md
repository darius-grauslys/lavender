# 1. Specification: core/include/scene/scene__game.h

## 1.1. Overview

Provides inline accessor utilities for `Scene_Data__Game`, the scene-specific
data structure used by the main gameplay scene. These accessors extract timer
references from the opaque `p_scene_data` pointer on a `Scene`.

## 1.2. Dependencies

- `defines.h` (for `Scene`, `Scene_Data__Game`, `Timer__u8`)

## 1.3. Types

### 1.3.1. Scene_Data__Game (struct)

Defined in `defines.h`:

    typedef struct Scene_Data__Game_t {
        Timer__u8 timer_for__hud_notification__u8;
        Timer__u8 timer_for__typer_sliding__u8;
    } Scene_Data__Game;

| Field | Type | Description |
|-------|------|-------------|
| `timer_for__hud_notification__u8` | `Timer__u8` | Timer controlling the lifespan/visibility of HUD notification popups. |
| `timer_for__typer_sliding__u8` | `Timer__u8` | Timer controlling the sliding animation of the typer/text UI element. |

## 1.4. Functions

### 1.4.1. Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_hud_timer_from__scene__game` | `(Scene*) -> Timer__u8*` | `Timer__u8*` | Casts `p_scene_data` to `Scene_Data__Game*` and returns a pointer to `timer_for__hud_notification__u8`. |
| `get_typer_timer_from__scene__game` | `(Scene*) -> Timer__u8*` | `Timer__u8*` | Casts `p_scene_data` to `Scene_Data__Game*` and returns a pointer to `timer_for__typer_sliding__u8`. |

## 1.5. Agentic Workflow

### 1.5.1. Usage Pattern

These accessors are intended to be called from within the gameplay scene's
`m_enter_scene_handler` (main loop) or from UI/HUD rendering code that
needs to query or manipulate the gameplay scene's timers.

    Scene *p_scene = get_p_active_scene_from__scene_manager(...);
    Timer__u8 *p_hud_timer = get_hud_timer_from__scene__game(p_scene);
    // poll or reset the timer as needed

### 1.5.2. Preconditions

- The `Scene*` argument must be non-null.
- The scene's `p_scene_data` must point to a valid `Scene_Data__Game`
  instance. Calling these accessors on a scene whose `p_scene_data` is
  null or points to a different type will result in undefined behavior.

### 1.5.3. Postconditions

- The returned `Timer__u8*` is a direct pointer into the scene data.
  Modifications through this pointer immediately affect the scene's state.
