# 1. Specification: core/include/game_action/implemented/game_action_registrar.h

## 1.1. Overview

The game action registrar is the "implemented" hook that populates the
`Game_Action_Logic_Table` with entries for all built-in game action kinds.
Three variants exist for different runtime modes: offline (single-player),
client (multiplayer client), and server (multiplayer server).

This file resides in the `implemented/` directory, meaning it is intended
to be overridden or extended by game-specific implementations.

## 1.2. Dependencies

- `defines.h` (for `Game_Action_Logic_Table`)

## 1.3. Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_actions__offline` | `(Game_Action_Logic_Table*) -> void` | Registers all game action kinds for single-player / offline mode. |
| `register_game_actions__client` | `(Game_Action_Logic_Table*) -> void` | Registers all game action kinds for a multiplayer client. |
| `register_game_actions__server` | `(Game_Action_Logic_Table*) -> void` | Registers all game action kinds for a multiplayer server. |

## 1.4. Agentic Workflow

### 1.4.1. When to use this module

- Called once during game initialization, after
  `initialize_game_action_logic_table`.
- The choice of registrar depends on the runtime mode:
  - Offline: `register_game_actions__offline`
  - Client: `register_game_actions__client`
  - Server: `register_game_actions__server`

### 1.4.2. Expected Implementation

Each registrar calls the kind-specific `register_game_action__*` functions.
For example, `register_game_actions__offline` would call:

    register_game_action__hitbox_for__offline(p_table);
    register_game_action__global_space__request_for__offline(p_table);
    register_game_action__input_for__offline(p_table);
    // ... etc.

### 1.4.3. Server vs Client vs Offline

Different modes register different handlers for the same `Game_Action_Kind`:

- **Server**: Validates and processes actions authoritatively.
- **Client**: Relays actions to the server and handles responses.
- **Offline**: Processes actions locally without network overhead.

Some actions (e.g. `Game_Action_Kind__Input`) are no-ops in offline mode
since input is driven locally.

### 1.4.4. Extending

To add a new game action kind:

1. Add the new `Game_Action_Kind` enum value.
2. Create a `register_game_action__*` function.
3. Add calls to it in all three registrar functions.

### 1.4.5. Preconditions

- `p_game_action_logic_table` must be initialized via
  `initialize_game_action_logic_table`.

### 1.4.6. Postconditions

- All built-in `Game_Action_Kind` values have valid entries in the table.
