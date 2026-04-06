# 1. Specification: core/include/game_action/core/game_action__bad_request.h

## 1.1. Overview

Provides initialization, registration, and dispatch for the
`Game_Action_Kind__Bad_Request` game action. This action is sent as a
response to another game action that was rejected or invalid. It carries
an error code and references the UUID of the original action.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Logic_Table`)
- `game.h` (for `dispatch_game_action`, `get_client_uuid_from__game_action`)
- `game_action/game_action.h` (for flag accessors)
- `serialization/serialization_header.h` (for `GET_UUID_P`)

## 1.3. Game_Action_Kind

`Game_Action_Kind__Bad_Request`

## 1.4. Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `ga_kind__bad_request__request_error_code` | `uint32_t` | Application-defined error code describing the rejection reason. |

The `uuid_of__game_action__responding_to` header field is set to the UUID
of the game action that triggered the bad request.

## 1.5. Functions

### 1.5.1. Registration

| Function | Signature | Description |
|----------|-----------|-------------|
| `register_game_action__bad_request` | `(Game_Action_Logic_Table*) -> void` | Registers the bad request action kind in the logic table. |

### 1.5.2. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_for__bad_request` | `(Game_Action*, Game_Action* responding_to, u32 error_code) -> void` | Initializes a bad request action referencing the original action and setting the error code. |

### 1.5.3. Dispatch (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action__bad_request` | `(Game*, Game_Action* original, u32 error_code) -> bool` | `bool` | Creates and dispatches a bad request back to the client that sent the original action. |

## 1.6. Agentic Workflow

### 1.6.1. When to use

- Use when a received game action cannot be fulfilled (e.g. invalid UUID,
  unauthorized operation, resource exhaustion).
- The bad request is sent back to the originating client.

### 1.6.2. Dispatch Pattern

    if (!can_fulfill_request) {
        dispatch_game_action__bad_request(
                p_game,
                p_game_action,
                MY_ERROR_CODE);
    }

### 1.6.3. Preconditions

- `p_game_action` (the original) must be a valid, allocated game action
  with a valid client UUID.

### 1.6.4. Postconditions

- A bad request action is dispatched to the originating client with the
  `IS_BAD_REQUEST` flag set and the error code populated.
