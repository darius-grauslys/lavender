# 1. Specification: core/include/game_action/game_action.h

## 1.1. Overview

Provides initialization and flag manipulation utilities for `Game_Action`,
the engine's primary command/event object. Game actions are dispatched through
the `Game` struct's handler function pointers and may be processed as
`Process` instances via the `Game_Action_Logic_Table`.

A `Game_Action` is a tagged union: the `Game_Action_Kind` discriminator
selects which union member holds the payload data.

## 1.2. Dependencies

- `defines.h` (for `Game_Action`, `Game_Action_Kind`, `Game_Action_Flags`)
- `defines_weak.h` (forward declarations)
- `game.h` (for `dispatch_game_action`, `dispatch_game_action_to__server`,
  `receive_game_action`, `resolve_game_action`)

## 1.3. Types

### 1.3.1. Game_Action (struct)

A large tagged union. The header portion is shared across all kinds:

    typedef struct Game_Action_t {
        // Header (shared by all kinds):
        Serialization_Header _serialiation_header;
        union {
            struct {
                Identifier__u32 uuid_of__client__u32;
                Identifier__u32 uuid_of__game_action__responding_to;
            };
            Vector__3i32F4 vector_3i32F4__broadcast_point;
        };
        Game_Action_Kind the_kind_of_game_action__this_action_is;
        Game_Action_Flags game_action_flags;

        // Payload (union of all kinds):
        union { ... };
    } Game_Action;

The header is also accessible as `_Game_Action_Header`.

### 1.3.2. Game_Action_Flags (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `GAME_ACTION_FLAGS__BIT_IS_ALLOCATED` | 0 | Slot is allocated in a `Game_Action_Manager`. |
| `GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND` | 1 | If set: inbound (received). If clear: outbound (dispatched). |
| `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS` | 2 | If set: this action is processed via a `Process`. |
| `GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE` | 3 | If set: processed on invocation. If clear: processed on response. |
| `GAME_ACTION_FLAGS__BIT_IS_RESPONSE` | 4 | If set: this action is a response to another action. |
| `GAME_ACTION_FLAGS__BIT_IS_LOCAL` | 5 | If set: will not be sent over TCP. |
| `GAME_ACTION_FLAGS__BIT_IS_BROADCASTED` | 6 | If set: action is broadcast to multiple clients. |
| `GAME_ACTION_FLAGS__BIT_IS_BAD_REQUEST` | 7 | If set: action represents an error/rejection. |

### 1.3.3. Sanitization Masks

| Macro | Value | Description |
|-------|-------|-------------|
| `GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE` | `IS_ALLOCATED \| IS_IN_OR__OUT_BOUND` | Bits preserved during inbound sanitization. |
| `GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE` | `IS_ALLOCATED` | Bits preserved during outbound sanitization. |
| `GAME_ACTION_FLAGS__INBOUND_SANITIZE` | `IS_IN_OR__OUT_BOUND` | Flags forced on for inbound. |
| `GAME_ACTION_FLAGS__OUTBOUND_SANITIZE` | `NONE` | Flags forced on for outbound. |

### 1.3.4. GA_UUID_SOURCE Macro

    #define GA_UUID_SOURCE(game_action) \
        ((Game_Action*)game_action)->uuid_of__client__u32

Extracts the client UUID from a game action. Used when the game action is
accessed through a `Process.p_process_data` pointer.

## 1.4. Functions

### 1.4.1. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action` | `(Game_Action*) -> void` | Zeroes out the game action. |

### 1.4.2. Kind Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_the_kind_of__game_action` | `(Game_Action*, Game_Action_Kind) -> void` | `void` | Sets the action kind discriminator. |
| `get_kind_of__game_action` | `(Game_Action*) -> Game_Action_Kind` | `Game_Action_Kind` | Returns the action kind. |

### 1.4.3. UUID Accessors (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_client_uuid_from__game_action` | `(Game_Action*) -> Identifier__u32` | `Identifier__u32` | Returns `uuid_of__client__u32`. |
| `get_response_uuid_from__game_action` | `(Game_Action*) -> Identifier__u32` | `Identifier__u32` | Returns `uuid_of__game_action__responding_to`. |
| `get_broadcast_point_of__game_action` | `(Game_Action*) -> Vector__3i32F4` | `Vector__3i32F4` | Returns the broadcast point (overlaps client UUID fields). |

### 1.4.4. Flag Accessors (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `is_game_action__allocated` | `bool` | True if allocated. Null-safe. |
| `set_game_action_as__allocated` | `void` | Sets allocated flag. |
| `set_game_action_as__deallocated` | `void` | Clears allocated flag. |
| `is_game_action__inbound` | `bool` | True if inbound. |
| `set_game_action_as__inbound` | `void` | Sets inbound flag. |
| `set_game_action_as__outbound` | `void` | Clears inbound flag. |
| `is_game_action__with_process` | `bool` | True if processed via Process. |
| `is_game_action__processed_on__invocation_or__respose` | `bool` | True if processed on invocation. |
| `is_game_action__responding_to_another__game_action` | `bool` | True if this is a response. |
| `is_game_action__local` | `bool` | True if local-only (no TCP). |
| `set_game_action_as__local` | `void` | Sets local flag. |
| `set_game_action_as__NOT_local` | `void` | Clears local flag. |
| `is_game_action__broadcasted` | `bool` | True if broadcast. |
| `set_game_action_as__broadcasted` | `void` | Sets broadcast flag. |
| `set_game_action_as__NOT_broadcasted` | `void` | Clears broadcast flag. |
| `is_game_action__bad_request` | `bool` | True if bad request. |
| `set_game_action_as__bad_request` | `void` | Sets bad request flag. |
| `set_game_action_as__NOT_bad_request` | `void` | Clears bad request flag. |

## 1.5. Agentic Workflow

### 1.5.1. Dispatching a Game Action

1. Create a `Game_Action` on the stack.
2. Call `initialize_game_action(...)`.
3. Call the kind-specific initializer (e.g. `initialize_game_action_for__hitbox`).
4. Call `dispatch_game_action(p_game, uuid_of__client, &ga)` or
   `dispatch_game_action_to__server(p_game, &ga)`.

The dispatch function is a function pointer on `Game`:
- `m_game_action_handler__dispatch` for outbound.
- `m_game_action_handler__receive` for inbound.
- `m_game_action_handler__resolve` for resolution.

### 1.5.2. Preconditions

- `initialize_game_action` must be called before setting any fields.
- The `Game_Action_Kind` must be set before dispatch.
- For TCP actions, the client UUID must be valid.

### 1.5.3. Postconditions

- After dispatch, the game action may be copied into a `Game_Action_Manager`
  pool and processed asynchronously via a `Process`.

### 1.5.4. Important Notes

- `Game_Action` is sized to fit within a `TCP_Packet` for network transmission.
- The `_serialiation_header` field has a typo (missing 'z') that is consistent
  throughout the codebase. Do not "fix" it.
- `vector_3i32F4__broadcast_point` overlaps `uuid_of__client__u32` and
  `uuid_of__game_action__responding_to`. Only one interpretation is valid
  at a time, determined by whether the action is broadcast.
