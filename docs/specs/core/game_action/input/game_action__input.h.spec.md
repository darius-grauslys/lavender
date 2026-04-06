# 1. Specification: core/include/game_action/core/input/game_action__input.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
input-related game action. This action transmits player input state
from a client to the server in multiplayer mode. In offline mode,
input is driven locally and this action is a no-op.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`, `Input`)
- `game.h` (for `dispatch_game_action_to__server`)

## 1.3. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__input__input` | `Input` | Complete copy of the client's input state. |

## 1.4. Functions

### 1.4.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__input_for__server` | `(Game_Action_Logic_Table*) -> void` | Registers input handling for server-side processing. |
| `register_game_action__input_for__client` | `(Game_Action_Logic_Table*) -> void` | Registers input handling for client-side relay. |
| `register_game_action__input_for__offline` | `(Game_Action_Logic_Table*) -> void` | No-op. Input is driven locally in offline mode. (static inline) |

### 1.4.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__input` | `(Game_Action*, Input*) -> void` | Copies the input state into the game action payload. |

### 1.4.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__input` | `(Game*, Input*) -> bool` | `bool` | Creates and dispatches the input action to the server. |

## 1.5. Agentic Workflow

### 1.5.1. Multiplayer Input Flow

1. Client polls input via `PLATFORM_poll_input`.
2. Client calls `dispatch_game_action__input(p_game, p_input)`.
3. The action is sent to the server over TCP.
4. Server receives the action and applies the input to the client's
   `Client.input_of__client` via `copy_input_into__client`.

### 1.5.2. Offline Mode

In offline mode, `register_game_action__input_for__offline` is a no-op.
Input is read directly from `Game.input` or the local client's input
without going through the game action system.

### 1.5.3. Preconditions

- `p_input` must be a valid `Input` struct with current frame data.

### 1.5.4. Postconditions

- In multiplayer: the server receives the client's input state.
- In offline: no effect.
