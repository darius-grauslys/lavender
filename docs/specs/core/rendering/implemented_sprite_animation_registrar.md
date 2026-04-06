# 1. Sprite Animation Registrar (Implemented/Template) Specification

## 1.1 File
`core/include/rendering/implemented/sprite_animation_registrar.h`

## 1.2 Purpose
Declares the game-specific function that registers all sprite animation
definitions into the `Sprite_Manager`. This file is a **template** — it is
copied to the game project directory by `lav_new_project` and is meant to
be modified by the engine user.

## 1.3 Template Behavior
This file resides in `core/include/rendering/implemented/` and is copied
to the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the
original in core serves as the default/template. The `implemented/`
directory is NOT in the core include path — it is only in the game
project's include path.

## 1.4 Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Sprite_Manager` |

## 1.5 Functions

### 1.5.1 `register_sprite_animations`
