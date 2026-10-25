# Lavender Examples

The projects in this folder are standalone example games. Each one teaches
one concept (scene setup, world allocation, UI, tile layers, entities, ...)
by **shadowing** the engine's stock `implemented/` files.

This document explains the one non-obvious build mechanism every example
relies on: **Include Shadowing** (and its source-file sibling).

## What `implemented/` means

The engine is written in C with a strong convention. Most of it is
"final" core code. A small set of extension points — the things a game
must specialize (its tile kinds, its scene kinds, its entity kinds, its
game actions, its registrars, ...) — live in directories named
`implemented/`. Every `core/**/implemented/` directory holds the **stock**
(version) of those files.

A game provides its **own** copy of those files. The build replaces the
engine's `implemented/` definitions with the game's. That replacement is
"shadowing", and it happens for both headers and C source files.

## Include Shadowing (headers)

The build assembles the compiler include path in this order
(`Makefile.include`):

```
INCLUDE := -I$(INCLUDE_GAME) -I$(INCLUDE_CORE) -I$(INCLUDE_PLATFORM) ...
           ^ game include/ comes FIRST, then core/include
```

`INCLUDE_GAME` is the project's `include/` directory; `INCLUDE_CORE` is
`core/include`. Because the project's directory is listed first, when a
source file writes

```c
#include <types/implemented/tile_kind.h>
```

the compiler finds the **project's** `include/types/implemented/tile_kind.h`
before the core's, and uses it. The project's header **shadows** the core's.

Headers that are NOT under an `implemented/` path (e.g. `world/world.h`,
`client.h`) have no project copy, so they resolve straight to core. You only
ever shadow `implemented/` headers — the rest of the API stays the engine's.

## Source Shadowing (C files)

Header shadowing alone is not enough: the definitions (function bodies,
global definitions) must also come from the game. That is handled in
`core/Makefile.include`:

```make
ifneq ($(GAME_DIR), $(BASE_DIR))
    # building a GAME: exclude the engine's stock implemented/ sources...
    CFILES_CORE != find $(SOURCE_CORE) -name *.c -not -path */implemented/*
else
    # building the engine itself: use its own implemented/ sources
    CFILES_CORE != find $(SOURCE_CORE) -name *.c
endif
```

When a game is built, **every `core/**/implemented/*.c` is excluded** from
the core object list. The game's own `source/**/implemented/*.c` files are
compiled instead (`CFILES_GAME` in the project's `Makefile.include`). So the
game's implementations replace the stock ones, one-for-one.

## Putting it together

To specialize an extension point, a project:

1. Mirrors the engine's `implemented/` directory into its own tree,
   preserving the `include/` vs `source/` split:
   `core/include/types/implemented/...` -> `./include/types/implemented/...`
   and `core/source/world/implemented/...` -> `./source/world/implemented/...`.
   (The `lav_new_project` scaffold script does this for you.)
2. Edits its own copies. The include path makes its headers win, and the
   source exclusion makes its C files win. Core is never modified.

A concrete pair: `types/00__tile_layers` shadows
`include/types/implemented/world/tile_kind.h` + `.../tile_layer.h` (to
declare its tile kinds/layers) **and** `source/world/implemented/
tile_logic_table_registrar.c` (to register the tile logic). Because the
project's versions shadow the stock ones, the engine compiles and links the
project's tile definitions with the rest of the stock engine.

## Conventions

- **C only, no C++**, in core and in examples.
- Naming: `get_`/`set_`/`is_`/`has_` for accessors, `m_` for member
  functions/handlers, `f_` for free functions, `p_` prefix for pointers,
  `__` as the word separator, `__u8`/`__u32F4` etc. as type suffixes.
- `GEN-*-BEGIN`/`GEN-*-END` markers delimit code-generation-managed
  sections; keep them and add code only inside them.

## Layout

`examples/<topic>/<NN__name>/` where `NN` is zero-padded so examples sort in
tutorial order (e.g. `scene/00__empty_scene`, `scene/01__allocate_world`,
`scene/02__allocate_ui`, `types/00__tile_layers`, `entity/00__spawn_entity`).
Planned topics are tracked in `EXAMPLES_TO_MAKE.md`. Every example carries
its own `README.md` with a numbered walkthrough; `AGENTS.md` is the guide
for AI agents working in this tree.
