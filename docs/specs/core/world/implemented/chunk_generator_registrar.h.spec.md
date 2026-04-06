# 1 Specification: core/include/world/implemented/chunk_generator_registrar.h

## 1.1 Overview

Declares the game-specific function that registers all chunk generator
process handlers into the `Chunk_Generator_Table`. This file is a
**template** — it is copied to the game project directory by
`lav_new_project` and is meant to be modified by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/world/implemented/` and is copied to
the game project's corresponding `implemented/` directory by the
`lav_new_project` script. The game developer modifies the copy; the
original in core serves as the default/template. The `implemented/`
directory is NOT in the core include path — it is only in the game
project's include path.

## 1.3 Dependencies

- `defines.h` (for `Chunk_Generator_Table`)

## 1.4 Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_chunk_generators` | `(Chunk_Generator_Table*) -> void` | Registers all game-specific chunk generators by calling `register_chunk_generator_into__chunk_generator_table` for each `Chunk_Generator_Kind` the game defines. |

## 1.5 Agentic Workflow

### 1.5.1 Implementation Notes

- Must be implemented by the game project.
- Called during game/world initialization.
- Each call to `register_chunk_generator_into__chunk_generator_table`
  associates a `Chunk_Generator_Kind` with an `m_Process` handler.
- The `Chunk_Generator_Kind` enum must be extended in the game's
  `types/implemented/chunk_generator_kind.h`.

## 1.6 Header Guard

`CHUNK_GENERATOR_REGISTRAR`
