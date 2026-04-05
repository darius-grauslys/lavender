# Specification: core/include/inventory/implemented/item_registrar.h

## Overview

Declares the platform/game-specific item registration entry point. This
header is part of the "implemented" pattern used throughout the engine,
where a header declares a function signature and the concrete implementation
is provided by the platform or game layer. The `register_items` function
is called during initialization to populate the `Item_Manager` with all
game-specific item templates.

## Dependencies

- `defines.h` (for `Item_Manager`)

## Functions

### Registration Entry Point

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_items` | `(Item_Manager*) -> void` | Registers all platform/game-specific item templates into the item manager. Called after `register_core_items_into__item_manager`. |

## Agentic Workflow

### Registration Sequence

    initialize_item_manager(p_item_manager)
        |
    register_core_items_into__item_manager(p_item_manager)
        |
    register_items(p_item_manager)   <-- this function
        |
    [Item_Manager fully populated]

### Implementation Pattern

This header follows the engine's "implemented" convention: the header lives
in `core/include/inventory/implemented/` and declares the interface, while
the concrete implementation is provided by each platform or game target.

A typical implementation:

    void register_items(Item_Manager *p_item_manager) {
        Item sword;
        initialize_item(&sword, Item_Kind__Sword);
        register_item_in__item_manager(
            p_item_manager, Item_Kind__Sword, sword);

        Item potion;
        initialize_item(&potion, Item_Kind__Potion);
        register_item_in__item_manager(
            p_item_manager, Item_Kind__Potion, potion);
        // ... etc.
    }

### Preconditions

- `p_item_manager` must be initialized via `initialize_item_manager` before
  calling `register_items`.
- Core items should already be registered via
  `register_core_items_into__item_manager`.

### Postconditions

- After `register_items`: all game-specific item kinds have corresponding
  templates in the `Item_Manager`.

### Error Handling

- Implementation-defined. Typically delegates to
  `register_item_in__item_manager` which performs bounds checking in debug
  builds.
