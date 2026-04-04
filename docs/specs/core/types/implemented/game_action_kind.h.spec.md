# Specification: core/include/types/implemented/game_action_kind.h

## Overview

Template header that defines the `Game_Action_Kind` enum — the set of
game action types used for multiplayer communication, entity management,
world loading, and custom game logic. This file is copied to the game
project directory by `tools/lav_new_project` and is meant to be extended
by the engine user.

## Template Behavior

This file resides in `core/include/types/implemented/` and is copied to
the game project's corresponding `types/implemented/` directory by the
`lav_new_project` script. If `DEFINE_GAME_ACTION_KIND` is not defined after
the `#include`, `defines_weak.h` falls back to a built-in default.

## Dependencies

None (self-contained).

## Types

### Game_Action_Kind (enum)

    typedef enum Game_Action_Kind {
        Game_Action_Kind__None = 0,
        Game_Action_Kind__Bad_Request,
        Game_Action_Kind__TCP_Connect__Begin,
        Game_Action_Kind__TCP_Connect,
        Game_Action_Kind__TCP_Connect__Reject,
        Game_Action_Kind__TCP_Connect__Accept,
        Game_Action_Kind__TCP_Disconnect,
        Game_Action_Kind__TCP_Delivery,
        Game_Action_Kind__World__Load_World,
        Game_Action_Kind__World__Load_Client,
        Game_Action_Kind__World__Request_Client_Data,
        Game_Action_Kind__Global_Space__Request,
        Game_Action_Kind__Global_Space__Resolve,
        Game_Action_Kind__Global_Space__Store,
        Game_Action_Kind__Inventory__Request,
        Game_Action_Kind__Inventory__Resolve,
        Game_Action_Kind__Entity__Spawn,
        Game_Action_Kind__Entity__Get,
        Game_Action_Kind__Sprite,
        Game_Action_Kind__Hitbox,
        Game_Action_Kind__Hitbox__End,
        Game_Action_Kind__Input = Game_Action_Kind__Hitbox__End,
        Game_Action_Kind__Custom,
        Game_Action_Kind__Unknown
    } Game_Action_Kind;

### Key Values

| Value | Description |
|-------|-------------|
| `Game_Action_Kind__None` | No action / sentinel. |
| `Game_Action_Kind__Hitbox__End` | Delimiter, not a hitbox kind. `Input` reuses its value. |
| `Game_Action_Kind__Custom` | First value available for game-specific actions. |
| `Game_Action_Kind__Unknown` | End-of-enum sentinel. Used for array sizing. |

## Injection Mechanism

In `defines_weak.h`:

    #include <types/implemented/game_action_kind.h>
    #ifndef DEFINE_GAME_ACTION_KIND
    typedef enum Game_Action_Kind { ... } Game_Action_Kind;
    #endif

## Agentic Workflow

### Extension Pattern

Add custom game actions between `Game_Action_Kind__Custom` and
`Game_Action_Kind__Unknown`:

    Game_Action_Kind__Custom,
    Game_Action_Kind__My_Custom_Action,
    Game_Action_Kind__Another_Custom_Action,
    Game_Action_Kind__Unknown

### Constraints

- All engine-defined kinds (from `None` through `Custom`) must remain
  present and in order. Only add and remove entries you have added.
- `Game_Action_Kind__Unknown` must remain last.
- `Game_Action_Kind__Unknown` is used for array sizing in
  `Game_Action_Logic_Table.game_action_logic_entries[]`.
- The `#define DEFINE_GAME_ACTION_KIND` line must not be removed.

## Header Guard

`IMPL_GAME_ACTION_KIND_H`
