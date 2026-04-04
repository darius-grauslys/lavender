# Aliased Texture Registrar (Implemented/Template) Specification

## File
`core/include/rendering/implemented/aliased_texture_registrar.h`

## Purpose
Declares the game-specific function that registers all named textures into
the `Aliased_Texture_Manager`. This file is a **template** — it is copied
to the game project directory by `lav_new_project` and is meant to be
modified by the engine user.

## Template Behavior
This file resides in `core/include/rendering/implemented/` and is copied
to the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the
original in core serves as the default/template. The `implemented/`
directory is NOT in the core include path — it is only in the game
project's include path.

## Dependencies
| Header | Purpose |
|--------|---------|
| `defines.h` | `Aliased_Texture_Manager`, `Game` |

## Functions

### `register_aliased_textures`
