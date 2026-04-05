# Specification: core/include/inventory/implemented/item_registrar.h

## Overview

Declares the game-specific item registration entry point. This header is
a **template file** shipped with the engine under the `implemented/`
convention. Prior to compilation, every `implemented/` directory is copied
into the game project directory where the game developer modifies the
copied files to suit their project. The version in `core/include/` is
therefore the **default template** — it compiles to a no-op or minimal
stub, and the game project's copy provides the real implementation.

Because the engine is compiled together with the game (not as a DLL or
shared library), the game project's copy of this file replaces the
template at compile time. This pattern is used throughout the engine for
all extensible enums, data structs, and registration entry points (e.g.,
`item_kind.h`, `item_data.h`, `entity_kind.h`, `entity_data.h`,
`tile_kind.h`, `scene_kind.h`, etc.).

## Dependencies

- `defines.h` (for `Item_Manager`)

## Template Convention

### How `implemented/` Works

1. The engine ships `core/include/inventory/implemented/item_registrar.h`
   as a **template**.
2. Before building a game project, the build system copies all
   `implemented/` directories into the game project's include path.
3. The game developer modifies the copied `item_registrar.h` (and other
   `implemented/` files) to register game-specific items, entities, tiles,
   etc.
4. At compile time, the game project's copy is found first on the include
   path, overriding the engine template.

### Two Override Mechanisms

The `implemented/` convention uses two distinct override mechanisms
depending on whether the file is a **type definition header** or a
**behavioral header**:

#### Type Definition Headers (Preprocessor Guard Pattern)

Files like `item_kind.h`, `item_data.h`, `entity_kind.h`, and
`entity_data.h` use a **`#define` guard** to override the engine's
fallback definitions. The engine template defines a guard macro (e.g.,
`#define DEFINE_ITEM_KIND`) and provides the game-specific typedef. The
engine's `defines_weak.h` checks for this guard:

    // In defines_weak.h:
    #include <types/implemented/item_kind.h>
    #ifndef DEFINE_ITEM_KIND
    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Unknown
    } Item_Kind;
    #endif

When the game project's copy of `item_kind.h` defines `DEFINE_ITEM_KIND`
and provides its own enum, the fallback in `defines_weak.h` is suppressed.
This is a **preprocessor-level** override — both the template and the
fallback exist in the source tree, but only one compiles.

#### Behavioral Headers (Include Path Replacement)

Files like `item_registrar.h` declare function signatures whose
implementations are provided in `.c` files. The game project's copy of
the `.c` file physically replaces the template on the include/source path.
There is no preprocessor guard involved — the linker sees exactly one
implementation of `register_items`.

### Relationship to Other `implemented/` Templates

| Template File | Mechanism | Purpose |
|---------------|-----------|---------|
| `types/implemented/item_kind.h` | Preprocessor guard (`DEFINE_ITEM_KIND`) | Defines the `Item_Kind` enum. Game projects extend with concrete item kinds between `None` and `Unknown`. |
| `types/implemented/item_data.h` | Preprocessor guard (`DEFINE_ITEM_DATA`) | Defines the `Item_Data` struct. Game projects add per-item payload fields. |
| `inventory/implemented/item_registrar.h` | Include path replacement | Declares `register_items`. Game projects implement to populate `Item_Manager`. |
| `types/implemented/entity_kind.h` | Preprocessor guard (`DEFINE_ENTITY_KIND`) | Defines the `Entity_Kind` enum. |
| `types/implemented/entity_data.h` | Preprocessor guard (`DEFINE_ENTITY_DATA`) | Defines the `Entity_Data` struct. Includes `Entity_Flags__u32 entity_flags` and `Entity_Kind the_kind_of__entity` in the default template. |
| `types/implemented/tile_kind.h` | Preprocessor guard (`DEFINE_TILE_KIND`) | Defines the `Tile_Kind` enum. |
| `types/implemented/scene_kind.h` | Preprocessor guard (`DEFINE_SCENE_KIND`) | Defines the `Scene_Kind` enum. |

The `item_registrar.h` template is the **behavioral counterpart** to the
`item_kind.h` and `item_data.h` **data templates**: the data templates
define what item kinds and data exist, while the registrar template defines
how those items are registered into the `Item_Manager` at initialization.

### Preprocessor Guard Pattern Detail

Each type definition template follows the same structure:

    // types/implemented/item_kind.h (engine template):
    #ifndef IMPL_ITEM_KIND_H
    #define IMPL_ITEM_KIND_H

    #define DEFINE_ITEM_KIND

    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Unknown
    } Item_Kind;

    #endif

The `#define DEFINE_ITEM_KIND` line is the key: it signals to
`defines_weak.h` that a game-provided definition exists, suppressing the
fallback. The game project's copy adds concrete kinds:

    // Game project's copy of types/implemented/item_kind.h:
    #ifndef IMPL_ITEM_KIND_H
    #define IMPL_ITEM_KIND_H

    #define DEFINE_ITEM_KIND

    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Sword,
        Item_Kind__Potion,
        Item_Kind__Arrow,
        Item_Kind__Stick,
        // ... game-specific kinds ...
        Item_Kind__Unknown
    } Item_Kind;

    #endif

The `Item_Kind__Unknown` sentinel must always be the last value, as it is
used for array sizing (`Item item_templates[(u16)Item_Kind__Unknown]` in
`Item_Manager`) and bounds checking.

## Functions

### Registration Entry Point

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_items` | `(Item_Manager*) -> void` | Registers all game-specific item templates into the item manager. Called after `register_core_items_into__item_manager` during engine initialization. |

### Template Implementation

The engine template declares only the function signature:

    void register_items(Item_Manager *p_item_manager);

The game project's copy provides the implementation. A typical game
implementation:

    void register_items(Item_Manager *p_item_manager) {
        Item sword;
        initialize_item(&sword, Item_Kind__Sword);
        register_item_in__item_manager(
            p_item_manager, Item_Kind__Sword, sword);

        Item potion;
        initialize_item(&potion, Item_Kind__Potion);
        register_item_in__item_manager(
            p_item_manager, Item_Kind__Potion, potion);

        // Register all game-specific item kinds...
    }

If the game project does not modify the template, a default stub
implementation is compiled (typically empty or registering no items).

## Agentic Workflow

### Registration Sequence

    initialize_item_manager(p_item_manager)
        |
    register_core_items_into__item_manager(p_item_manager)
        |   (engine-level items, defined in core)
        |
    register_items(p_item_manager)   <-- this function (game-provided)
        |   (game-specific items)
        |
    [Item_Manager fully populated]

### Two-Phase Registration

The engine enforces a two-phase registration pattern:

1. **Core phase** (`register_core_items_into__item_manager`): Defined in
   `core/source/inventory/`. Registers engine-level items that are common
   across all games built on the engine. This function is NOT a template
   — it ships with the engine and is not copied to the game project.

2. **Game phase** (`register_items`): Defined via the `implemented/`
   template. The game project's copy registers all game-specific items.
   This is where the bulk of item registration occurs for any non-trivial
   game.

This separation ensures that:
- Core items are always available regardless of game implementation.
- Game items cannot accidentally omit or break core item registration.
- The game developer has full control over game-specific items without
  modifying engine source.

### Coordination with `item_kind.h` and `item_data.h`

For `register_items` to register a game-specific item, the corresponding
`Item_Kind` enum value must exist. This means the game project must also
modify the `types/implemented/item_kind.h` template to add the enum
values:

    // In game's copy of types/implemented/item_kind.h:
    #define DEFINE_ITEM_KIND
    typedef enum Item_Kind {
        Item_Kind__None = 0,
        Item_Kind__Sword,
        Item_Kind__Potion,
        Item_Kind__Arrow,
        // ... game-specific kinds ...
        Item_Kind__Unknown
    } Item_Kind;

Similarly, if items carry game-specific data, the game project modifies
`types/implemented/item_data.h`:

    // In game's copy of types/implemented/item_data.h:
    #define DEFINE_ITEM_DATA
    typedef struct Item_Data_t {
        u8 damage;
        u8 durability;
    } Item_Data;

All three templates (`item_kind.h`, `item_data.h`, `item_registrar.h`)
must be coordinated for the item system to function correctly:

1. `item_kind.h` defines the enum values (what items exist).
2. `item_data.h` defines the per-item payload (what data items carry).
3. `item_registrar.h` registers templates (how items are initialized).

### Build System Integration

The `implemented/` copy mechanism is a build-system concern. The engine
uses two complementary strategies:

- **Type headers** (`item_kind.h`, `item_data.h`): Use `#define` guards
  checked by `defines_weak.h` and `defines.h`. The game project's copy
  defines the guard macro, suppressing the engine's fallback typedef.
  Both files exist in the source tree but only one definition compiles.

- **Behavioral headers** (`item_registrar.h`): The header declares a
  function signature. The game project provides the `.c` implementation.
  The linker sees exactly one definition. No preprocessor dispatch is
  involved for the implementation.

In both cases:
- No runtime dispatch or function pointer indirection is involved.
- The override is resolved entirely at compile/link time.

### Preconditions

- `p_item_manager` must be initialized via `initialize_item_manager`
  before calling `register_items`.
- Core items should already be registered via
  `register_core_items_into__item_manager`.
- The game project's `item_kind.h` must define all `Item_Kind` values
  that `register_items` will reference.

### Postconditions

- After `register_items`: all game-specific item kinds have corresponding
  templates in the `Item_Manager`.
- `get_item_from__item_manager(p_item_manager, Item_Kind__X)` returns a
  valid `Item` for every kind registered by the game.

### Error Handling

- Implementation-defined. Typically delegates to
  `register_item_in__item_manager` which calls `debug_error` and returns
  early on out-of-bounds `Item_Kind` in debug builds.
- If the game project does not modify the template, no game-specific items
  are registered. This is not an error — it simply means only core items
  are available.
