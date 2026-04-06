# 1. Specification: core/include/game_action/game_action_logic_entry.h

## 1.1. Overview

Defines the `Game_Action_Logic_Entry` initialization and sanitization
interface. Each entry in the `Game_Action_Logic_Table` describes how a
specific `Game_Action_Kind` should be processed: what flags to apply,
what process handlers to invoke, and at what priority.

## 1.2. Dependencies

- `defines.h` (for `Game_Action_Logic_Entry`, `Game_Action_Flags`,
  `Process_Flags__u8`, `Process_Priority__u8`, `m_Process`)

## 1.3. Types

### 1.3.1. Game_Action_Logic_Entry (struct)

    typedef struct Game_Action_Logic_Entry_t {
        m_Process m_process_of__game_action__inbound;
        m_Process m_process_of__game_action__outbound;
        Game_Action_Flags game_action_flags__inbound;
        Game_Action_Flags game_action_flags__inbound_mask;
        Game_Action_Flags game_action_flags__outbound;
        Game_Action_Flags game_action_flags__outbound_mask;
        Process_Flags__u8 process_flags_of__game_action__outbound;
        Process_Flags__u8 process_flags_of__game_action__inbound;
        Process_Priority__u8 process_priority__u8;
    } Game_Action_Logic_Entry;

| Field | Type | Description |
|-------|------|-------------|
| `m_process_of__game_action__inbound` | `m_Process` | Handler invoked for inbound (received) actions. NULL if no inbound processing. |
| `m_process_of__game_action__outbound` | `m_Process` | Handler invoked for outbound (dispatched) actions. NULL if no outbound processing. |
| `game_action_flags__inbound` | `Game_Action_Flags` | Flags forced onto inbound actions during sanitization. |
| `game_action_flags__inbound_mask` | `Game_Action_Flags` | Bits preserved from the original action during inbound sanitization. |
| `game_action_flags__outbound` | `Game_Action_Flags` | Flags forced onto outbound actions during sanitization. |
| `game_action_flags__outbound_mask` | `Game_Action_Flags` | Bits preserved from the original action during outbound sanitization. |
| `process_flags_of__game_action__outbound` | `Process_Flags__u8` | Process flags applied to the outbound process (e.g. `PROCESS_FLAG__IS_CRITICAL`). |
| `process_flags_of__game_action__inbound` | `Process_Flags__u8` | Process flags applied to the inbound process. |
| `process_priority__u8` | `Process_Priority__u8` | Priority level for the spawned process. |

## 1.4. Functions

### 1.4.1. Core Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_logic_entry` | `(Game_Action_Logic_Entry*, Game_Action_Flags out_flags, Game_Action_Flags out_mask, Game_Action_Flags in_flags, Game_Action_Flags in_mask, Process_Priority__u8, m_Process out_handler, Process_Flags__u8 out_process_flags, m_Process in_handler, Process_Flags__u8 in_process_flags) -> void` | Full initialization with all parameters. |

### 1.4.2. Convenience Initializers (static inline)

| Function | Description |
|----------|-------------|
| `initialize_game_action_logic_entry_as__process__out_and_in` | Both outbound and inbound are processed via `Process`. Both are processed on invocation. |
| `initialize_game_action_logic_entry_as__process__out` | Only outbound is processed via `Process`. Processed on invocation. |
| `initialize_game_action_logic_entry_as__process__in` | Only inbound is processed via `Process`. Processed on invocation. |
| `initialize_game_action_logic_entry_as__react__out` | Outbound is processed but NOT marked as `IS_WITH_PROCESS` in flags (reactive). |
| `initialize_game_action_logic_entry_as__react__in` | Inbound is processed but NOT marked as `IS_WITH_PROCESS` in flags (reactive). |
| `initialize_game_action_logic_entry_as__message` | No processing on either direction. Pure message passthrough. |
| `initialize_game_action_logic_entry_as__broadcast__server` | Outbound is processed and marked as broadcast. Server-side only. |
| `initialize_game_action_logic_entry_as__message_response` | Inbound is processed and marked as a response. |

### 1.4.3. Sanitization

| Function | Signature | Description |
|----------|-----------|-------------|
| `santize_game_action__inbound` | `(Game_Action_Logic_Entry*, Game_Action*) -> void` | Applies inbound flag sanitization: preserves bits in mask, forces bits in flags. |
| `santize_game_action__outbound` | `(Game_Action_Logic_Entry*, Game_Action*) -> void` | Applies outbound flag sanitization. |

### 1.4.4. Getters (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `get_m_process__outbound_of__game_action_logic_entry` | `m_Process` | Outbound process handler. |
| `get_m_process__inbound_of__game_action_logic_entry` | `m_Process` | Inbound process handler. |
| `get_process_priority__game_action_logic_entry` | `Process_Priority__u8` | Process priority. |
| `get_process_flags__outbound_of__game_action_logic_entry` | `Process_Flags__u8` | Outbound process flags. |
| `get_process_flags__inbound_of__game_action_logic_entry` | `Process_Flags__u8` | Inbound process flags. |

## 1.5. Agentic Workflow

### 1.5.1. Registration Pattern

Each `Game_Action_Kind` has a `register_game_action__*` function that
calls one of the convenience initializers:

    void register_game_action__hitbox_for__server(
            Game_Action_Logic_Table *p_table) {
        initialize_game_action_logic_entry_as__process__out(
                &p_table->game_action_logic_entries[
                    Game_Action_Kind__Hitbox__Set_Position],
                PROCESS_PRIORITY__0_MAXIMUM,
                m_process__game_action__hitbox__aabb,
                PROCESS_FLAGS__NONE);
    }

### 1.5.2. Sanitization Flow

When a game action is dispatched or received, the logic table sanitizes
its flags before processing:

1. Look up the `Game_Action_Logic_Entry` by `Game_Action_Kind`.
2. Call `santize_game_action__outbound` (for dispatch) or
   `santize_game_action__inbound` (for receive).
3. The sanitization preserves only the bits in the mask, then ORs in
   the forced flags.

This prevents clients from spoofing flags (e.g. claiming an action is
a broadcast when the server doesn't allow it).

### 1.5.3. Preconditions

- The `Game_Action_Logic_Table` must be initialized before registration.
- Each `Game_Action_Kind` should be registered exactly once.

### 1.5.4. Postconditions

- After sanitization, the game action's flags conform to the entry's
  policy regardless of what the original flags were.
