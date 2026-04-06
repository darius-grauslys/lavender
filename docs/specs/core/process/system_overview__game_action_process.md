# 1. System Overview: Game Action Process

## 1.1 Purpose

The game action process pattern wraps a `Game_Action` as a process's
`p_process_data`, enabling the game action to be processed cooperatively
over multiple poll cycles. This bridges the game action dispatch system
with the cooperative scheduling system, allowing complex game actions
(e.g. multi-step server responses, world modifications) to execute
without blocking the main loop.

## 1.2 Architecture

### 1.2.1 Data Layout (Standard Mode)

    Process
    +-- m_process_run__handler    -> game action handler (from Game_Action_Logic_Table)
    +-- m_process_dispose__handler -> m_process__dispose_handler__game_action__default
    +-- void *p_process_data      -> Game_Action*
    |                                +-- Serialization_Header
    |                                +-- Identifier__u32 uuid_of__client__u32
    |                                +-- Game_Action_Kind the_kind_of__game_action
    |                                +-- (game action payload fields)
    +-- Process_Kind = Process_Kind__Game_Action
    +-- process_sub_state__u8     (handler state machine)
    +-- scratch values            (handler working data)

### 1.2.2 Data Layout (TCP Receiver Mode)

When converted to a TCP payload receiver, the data pointer chain changes:

    Process
    +-- void *p_process_data      -> Serialization_Request*
    |                                +-- void *p_data -> Game_Action* (original)
    |                                +-- u8 *p_tcp_packet_destination -> destination buffer
    |                                +-- u8 *pM_packet_bitmap -> fragment bitmap (heap)
    |                                +-- Quantity__u16 quantity_of__bytes_in__destination
    |                                +-- Quantity__u16 quantity_of__tcp_packets__anticipated
    +-- Process_Kind = Process_Kind__Game_Action

### 1.2.3 Key Types

| Type | Role |
|------|------|
| `Process` | The cooperative task unit carrying the game action. |
| `Game_Action` | The game action being processed. Accessed via `p_process_data` (standard mode) or `Serialization_Request.p_data` (TCP mode). |
| `Serialization_Request` | Allocated when the process is converted to TCP receiver mode. Wraps the original game action and tracks fragment reassembly. |
| `Game_Action_Kind` | Enum discriminating the type of game action. Used by the `Game_Action_Logic_Table` to select the appropriate handler. |

## 1.3 Initialization

### 1.3.1 Standard Game Action Process

    initialize_process_as__game_action_process(p_process, p_game_action);
        -> p_process->p_process_data = p_game_action
        -> p_process->the_kind_of__process_this__process_is = Process_Kind__Game_Action

This function only sets the data pointer and kind. The caller is responsible
for:
- Setting `m_process_run__handler` (typically from the `Game_Action_Logic_Table`).
- Setting `m_process_dispose__handler` (typically
  `m_process__dispose_handler__game_action__default`).

### 1.3.2 TCP Payload Receiver Conversion

    bool success = set_game_action_process_as__tcp_payload_receiver(
            p_game,
            p_process,
            destination_buffer,
            destination_size);

1. Allocates a `Serialization_Request` via
   `PLATFORM_allocate_serialization_request`.
2. Moves the original `Game_Action*` from `p_process->p_process_data` to
   `Serialization_Request.p_data`.
3. Sets `p_process->p_process_data` to the `Serialization_Request`.
4. Configures the serialization request for TCP fragment tracking:
   - `p_tcp_packet_destination` = destination buffer
   - `quantity_of__bytes_in__destination` = destination size
   - `pM_packet_bitmap` = heap-allocated fragment bitmap
   - `quantity_of__tcp_packets__anticipated` = calculated from destination size

Returns false if `PLATFORM_allocate_serialization_request` fails.

## 1.4 Lifecycle

### 1.4.1 Game Action Allocation

A `Game_Action` is allocated from a `Game_Action_Manager` (typically the
client's game action manager):

    Game_Action *p_ga = allocate_game_action(p_game_action_manager);
    // Configure the game action fields...

### 1.4.2 Process Creation

    Process *p_proc = run_process(
            &game.process_manager,
            ga_handler_from_logic_table,
            PROCESS_PRIORITY__0_MAXIMUM,
            PROCESS_FLAGS__NONE);
    initialize_process_as__game_action_process(p_proc, p_ga);
    set_process__dispose_handler(
            p_proc,
            m_process__dispose_handler__game_action__default);

### 1.4.3 Cooperative Execution

Each poll cycle, the scheduler invokes the handler:

    void ga_handler(Process *p_this_process, Game *p_game) {
        Game_Action *p_ga =
            (Game_Action*)p_this_process->p_process_data;

        // Access game action fields...
        // Perform one step of work...

        if (done) {
            complete_process(p_this_process);
        }
    }

### 1.4.4 Disposal

When the process completes or fails, the default dispose handler runs:

    m_process__dispose_handler__game_action__default(p_process, p_game);

This handler:
1. Retrieves the client's `Game_Action_Manager` using
   `uuid_of__client__u32` from the game action.
2. Releases the `Game_Action` from the client's manager.
3. If a `Serialization_Request` was allocated (TCP mode), releases it
   via `deactivate_serialization_request`.

### 1.4.5 Lifecycle Diagram

    [Game_Action allocated] --> initialize_process_as__game_action_process
                                    |
                                    v
                            [Process running]
                                    |
                        (optional) set_game_action_process_as__tcp_payload_receiver
                                    |
                                    v
                            [Handler polls each cycle]
                                    |
                            complete_process / fail_process
                                    |
                                    v
                            m_process__dispose_handler__game_action__default
                                    |
                                    v
                            [Game_Action released]
                            [Serialization_Request released (if TCP)]
                                    |
                                    v
                            [Process slot freed]

## 1.5 TCP Receiver Pattern

For game actions that receive multi-packet payloads (e.g. chunk data from
a server):

    void my_tcp_receiver(Process *p_proc, Game *p_game) {
        switch (p_proc->process_sub_state__u8) {
            case 0: // Setup
                if (!set_game_action_process_as__tcp_payload_receiver(
                        p_game, p_proc,
                        my_buffer, sizeof(my_buffer))) {
                    fail_process(p_proc);
                    return;
                }
                set_process__sub_state(p_proc, 1);
                break;
            case 1: // Receive fragments
                // Delegates to tcp_game_action_process functions
                // See system_overview__tcp_game_action_process.md
                break;
        }
    }

After conversion, the game action is accessed through the serialization
request:

    Serialization_Request *p_sr =
        (Serialization_Request*)p_proc->p_process_data;
    Game_Action *p_ga = (Game_Action*)p_sr->p_data;

## 1.6 Important Constraints

### 1.6.1 Dispose Handler Assumption

The default dispose handler (`m_process__dispose_handler__game_action__default`)
assumes:
- In standard mode: `p_process_data` is a `Game_Action*`.
- In TCP mode: `p_process_data` is a `Serialization_Request*` whose
  `p_data` field is a `Game_Action*`.

If `Serialization_Request.p_data` is NOT a `Game_Action*` (e.g. it was
repurposed), you MUST:
1. Release `p_data` manually before calling `complete_process` or
   `fail_process`.
2. Set `p_data` to NULL.

Otherwise the dispose handler will attempt to release a non-game-action
pointer from the `Game_Action_Manager`, causing undefined behavior.

### 1.6.2 Preconditions

- `initialize_process_as__game_action_process`: `p_game_action` must be
  a valid, allocated game action.
- `set_game_action_process_as__tcp_payload_receiver`: the process must
  already be initialized as a game action process. The destination buffer
  must be pre-allocated and large enough for the expected payload.

### 1.6.3 Postconditions

- After `initialize_process_as__game_action_process`:
  `p_process->p_process_data` points to the game action.
  `p_process->the_kind_of__process_this__process_is` is
  `Process_Kind__Game_Action`.
- After `set_game_action_process_as__tcp_payload_receiver`:
  `p_process->p_process_data` points to a `Serialization_Request`.
  The original game action is at `Serialization_Request.p_data`.

## 1.7 Relationship to Other Process Types

| Concern | Managed By |
|---------|------------|
| Game action wrapping and disposal | `game_action_process.h` (this module) |
| TCP fragment send/receive polling | `tcp_game_action_process.h` |
| File I/O wrapping | `filesystem_process.h` |
| Process allocation and scheduling | `Process_Manager` / `Process_Table` |

The game action process is the most common specialized process type. TCP
game action processes and filesystem processes build on top of or alongside
this pattern.
