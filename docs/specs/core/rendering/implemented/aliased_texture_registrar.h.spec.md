# 1. Specification: core/include/rendering/implemented/aliased_texture_registrar.h

## 1.1 Overview

Declares the game-specific function that registers all named textures into
the `Aliased_Texture_Manager`. This file is a **template** — it is copied
to the game project directory by `lav_new_project` and is meant to be
modified by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/rendering/implemented/` and is copied to
the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the original
in core serves as the default/template. The `implemented/` directory is NOT
in the core include path — it is only in the game project's include path.

## 1.3 Dependencies

- `defines.h` (for `Aliased_Texture_Manager`, `Game`)

## 1.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_aliased_textures` | `(Aliased_Texture_Manager*, Game*) -> void` | Registers all game-specific named textures by calling `allocate_texture_with__alias` or `load_texture_from__path_with__alias` for each texture the game needs. |

## 1.5 Agentic Workflow

### 1.5.1 Implementation Notes

- Must be implemented by the game project.
- Called during game initialization.
- The `Aliased_Texture_Manager` is obtained from `Gfx_Context`.

## 1.6 Header Guard

`ALIAS_TEXTURE_REGISTRAR_H`
