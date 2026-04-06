# 1. Specification: core/include/rendering/implemented/sprite_animation_registrar.h

## 1.1 Overview

Declares the game-specific function that registers all sprite animation
definitions. This file is a **template** — it is copied to the game project
directory by `lav_new_project` and is meant to be modified by the engine
user.

## 1.2 Template Behavior

This file resides in `core/include/rendering/implemented/` and is copied to
the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the original
in core serves as the default/template. The `implemented/` directory is NOT
in the core include path — it is only in the game project's include path.

## 1.3 Dependencies

- `defines.h` (for `Sprite_Manager`)

## 1.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_sprite_animations` | `(Sprite_Manager*) -> void` | Registers all game-specific sprite animations by calling `register_sprite_animation_into__sprite_context` for each animation the game defines. |

## 1.5 Agentic Workflow

### 1.5.1 Implementation Notes

- Must be implemented by the game project.
- Called during game initialization.
- Despite the parameter name `p_sprite_manager`, the actual registration
  target is the `Sprite_Context` — this signature may be updated in a
  future refactor.

## 1.6 Header Guard

`SPRITE_ANIMATION_REGISTRAR_H`
