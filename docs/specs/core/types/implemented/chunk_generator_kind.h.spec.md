# 1 Specification: core/include/types/implemented/chunk_generator_kind.h

## 1.1 Overview

Template header that defines the `Chunk_Generator_Kind` enum — the set of
chunk generation algorithms available for world construction. This file is
copied to the game project directory by `tools/lav_new_project` and is
meant to be extended by the engine user.

## 1.2 Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. The game developer extends the copy with
game-specific generator kinds. If `DEFINE_CHUNK_GENERATOR_KIND` is not
defined after the `#include`, `defines_weak.h` falls back to a built-in
default.

## 1.3 Dependencies

None (self-contained).

## 1.4 Types

### 1.4.1 Chunk_Generator_Kind (enum)

    typedef enum Chunk_Generator_Kind {
        Chunk_Generator_Kind__None,
        Chunk_Generator_Kind__Overworld = Chunk_Generator_Kind__None,
        Chunk_Generator_Kind__Overworld__Plains,
        Chunk_Generator_Kind__Overworld__Forest,
        Chunk_Generator_Kind__Overworld__Mountain,
        Chunk_Generator_Kind__Overworld__Desert,
        Chunk_Generator_Kind__Overworld__Beach,
        Chunk_Generator_Kind__Overworld__Ocean,
        Chunk_Generator_Kind__Overworld__River,
        Chunk_Generator_Kind__Unknown
    } Chunk_Generator_Kind;

| Value | Description |
|-------|-------------|
| `Chunk_Generator_Kind__None` | Default generator sentinel. Assign your default generator to this value. |
| `Chunk_Generator_Kind__Unknown` | End-of-enum sentinel. Used for array sizing in `Chunk_Generator_Table`. |

## 1.5 Injection Mechanism

In `defines_weak.h`:

    #include "types/implemented/chunk_generator_kind.h"
    #ifndef DEFINE_CHUNK_GENERATOR_KIND
    typedef enum Chunk_Generator_Kind {
        Chunk_Generator_Kind__None = 0,
        Chunk_Generator_Kind__Unknown
    } Chunk_Generator_Kind;
    #endif

## 1.6 Agentic Workflow

### 1.6.1 Extension Pattern

Assign your default generator to `Chunk_Generator_Kind__None` using `=`:

    Chunk_Generator_Kind__None,
    Chunk_Generator_Kind__Overworld = Chunk_Generator_Kind__None,

Add biome-specific generators between `None` and `Unknown`.

### 1.6.2 Constraints

- `Chunk_Generator_Kind__None` must remain first (value 0).
- `Chunk_Generator_Kind__Unknown` must remain last.
- `Chunk_Generator_Kind__Unknown` is used for array sizing in
  `Chunk_Generator_Table.M_process__chunk_generators[]`.
- Generators are registered via `register_chunk_generators` (see
  `world/implemented/chunk_generator_registrar.h`).
- The `#define DEFINE_CHUNK_GENERATOR_KIND` line must not be removed.

## 1.7 Header Guard

`IMPL_CHUNK_GENERATOR_KIND_H`
