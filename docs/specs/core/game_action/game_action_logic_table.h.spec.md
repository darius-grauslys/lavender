# 1. Specification: core/include/game_action/game_action_logic_table.h

## 1.1. Overview

The `Game_Action_Logic_Table` is an array of `Game_Action_Logic_Entry`
indexed by `Game_Action_Kind`. It serves as the central dispatch table
for all game actions, determining how each kind of action is processed
(outbound vs inbound), at what priority, and with what flags.

## 1.2. Dependencies

- `defines.h` (for `Game_Action_Logic_Table`, `Game_Action_Logic_Entry`,
  `Game_Action_Kind`, `Process_Manager`, `Process`)
- `game_action/game_action.h` (for `get_kind_of__game_action`)
- `game_action/game_action_logic_entry.h` (for entry accessors)

## 1.3. Types

### 1.3.1. Game_Action_Logic_Table (struct)

    typedef struct Game_Action_Logic_Table_t {
        Game_Action_Logic_Entry game_action_logic_entries[
            Game_Action_Kind__Unknown];
    } Game_Action_Logic_Table;

Indexed by `Game_Action_Kind`. The entry at index `Game_Action_Kind__Unknown`
is not used (it serves as the array bound).

## 1.4. Functions

### 1.4.1. Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_game_action_logic_table` | `(Game_Action_Logic_Table*) -> void` | Zeroes out all entries. Must be called before any registration. |

### 1.4.2. Lookup (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_game_action_logic_entry_by__game_action_kind` | `(Game_Action_Logic_Table*, Game_Action_Kind) -> Game_Action_Logic_Entry*` | `Game_Action_Logic_Entry*` or `NULL` | Returns the entry for the given kind. Returns NULL if kind >= `Game_Action_Kind__Unknown`. |

### 1.4.3. Process Dispatch

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `dispatch_game_action_process` | `(Process_Manager*, Game_Action*, m_Process, Process_Priority__u8, Process_Flags__u8) -> Process*` | `Process*` | Low-level: allocates a `Process` with the given handler and attaches the game action as `p_process_data`. |
| `dispatch_game_action_process__outbound` | `(Game_Action_Logic_Table*, Process_Manager*, Game_Action*) -> Process*` | `Process*` | Looks up the entry by kind, dispatches the outbound process handler. |
| `dispatch_game_action_process__inbound` | `(Game_Action_Logic_Table*, Process_Manager*, Game_Action*) -> Process*` | `Process*` | Looks up the entry by kind, dispatches the inbound process handler. |

### 1.4.4. Handler Lookup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_m_process__outbound_for__this_game_action_kind` | `(Game_Action_Logic_Table*, Game_Action_Kind) -> m_Process` | `m_Process` | Returns the outbound handler for the given kind. |
| `get_m_process__inbound_for__this_game_action_kind` | `(Game_Action_Logic_Table*, Game_Action_Kind) -> m_Process` | `m_Process` | Returns the inbound handler for the given kind. |

## 1.5. Agentic Workflow

### 1.5.1. Initialization Sequence

1. Call `initialize_game_action_logic_table(...)`.
2. Call `register_game_actions__offline(...)`, `register_game_actions__client(...)`,
   or `register_game_actions__server(...)` from `game_action_registrar.h`.
3. Each registrar calls kind-specific `register_game_action__*` functions
   which populate the table entries.

### 1.5.2. Dispatch Flow

1. A game action is created and initialized with a specific kind.
2. The dispatch handler (`m_game_action_handler__dispatch` on `Game`) is called.
3. The handler looks up the logic entry via
   `get_p_game_action_logic_entry_by__game_action_kind`.
4. If the entry has `IS_WITH_PROCESS`, a `Process` is allocated via
   `dispatch_game_action_process__outbound` or `__inbound`.
5. The process runs the registered `m_Process` handler with the game action
   as `p_process_data`.

### 1.5.3. Process Data Convention

When a game action is processed via a `Process`, the game action is stored
in `Process.p_process_data`. The process handler casts it back:

    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

The client UUID can be extracted via `GA_UUID_SOURCE(p_game_action)`.

### 1.5.4. Preconditions

- Table must be initialized before any lookups or dispatches.
- All required `Game_Action_Kind` values must be registered before use.

### 1.5.5. Postconditions

- After `dispatch_game_action_process__outbound`: a `Process` is allocated
  and enqueued in the `Process_Manager` with the game action attached.
- The process will run on the next process manager poll cycle.

### 1.5.6. Error Handling

- `get_p_game_action_logic_entry_by__game_action_kind` returns NULL for
  out-of-range kinds.
- `dispatch_game_action_process__outbound/inbound` may return NULL if the
  process manager is full or the handler is NULL.
