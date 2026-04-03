# Specification: core/include/process/game_action_process.h

## Overview

Provides initialization and configuration utilities for processes that
execute game actions. A game action process wraps a `Game_Action` as its
`p_process_data`, enabling the game action to be processed cooperatively
over multiple poll cycles.

Also provides the ability to convert a game action process into a TCP
payload receiver, which tracks incoming `TCP_Delivery` fragments via a
`Serialization_Request`.

## Dependencies

- `defines.h` (for `Process`, `Game_Action`, `Serialization_Request`)
- `defines_weak.h` (forward declarations)
- `game.h` (for game accessors)
- `platform.h` (for `PLATFORM_allocate_serialization_request`)
- `process/process.h` (for process status functions)
- `game_action/game_action.h` (for game action accessors)

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_process_as__game_action_process` | `(Process*, Game_Action*) -> void` | Sets `p_process_data` to the game action and marks the process kind as `Process_Kind__Game_Action`. |

### TCP Payload Receiver

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_game_action_process_as__tcp_payload_receiver` | `(Game*, Process*, u8* destination, Quantity__u16 destination_size) -> bool` | `bool` | Converts the process into a TCP payload receiver. Allocates a `Serialization_Request`, sets it as the process's data (the original `Game_Action*` is moved to `Serialization_Request.p_data`). Returns false on allocation failure. |

### Dispose Handler

| Function | Signature | Description |
|----------|-----------|-------------|
| `m_process__dispose_handler__game_action__default` | `(Process*, Game*) -> void` | Default dispose handler for game action processes. Releases the game action from the client's game action manager and releases the serialization request if one was allocated. |

## Agentic Workflow

### Game Action Process Lifecycle

1. A `Game_Action` is allocated in a `Game_Action_Manager`.
2. `initialize_process_as__game_action_process(p_process, p_game_action)`.
3. The process's `m_process_run__handler` is set to the appropriate
   handler from the `Game_Action_Logic_Table`.
4. The process runs cooperatively, accessing the game action via
   `(Game_Action*)p_this_process->p_process_data`.
5. On completion/failure, the dispose handler releases the game action.

### TCP Payload Receiver Pattern

For game actions that need to receive multi-packet data (e.g. chunk data):

1. The process handler calls `set_game_action_process_as__tcp_payload_receiver`.
2. The `Serialization_Request` becomes `p_process_data`.
3. The original `Game_Action*` is stored in `Serialization_Request.p_data`.
4. Each poll cycle, the handler calls `poll_game_action_process__tcp_receive`
   (from `tcp_game_action_process.h`) to check for incoming fragments.
5. When all fragments arrive, the handler processes the reassembled data.
6. The dispose handler releases both the serialization request and the
   game action.

### Data Pointer Chain (TCP mode)

    Process.p_process_data
        --> Serialization_Request
            .p_data --> Game_Action (original)
            .p_tcp_packet_destination --> destination buffer
            .pM_packet_bitmap --> fragment tracking bitmap

### Preconditions

- `initialize_process_as__game_action_process`: `p_game_action` must be
  a valid, allocated game action.
- `set_game_action_process_as__tcp_payload_receiver`: the process must
  already be initialized as a game action process. The destination buffer
  must be pre-allocated.

### Postconditions

- After `initialize_process_as__game_action_process`:
  `p_process->p_process_data` points to the game action.
- After `set_game_action_process_as__tcp_payload_receiver`:
  `p_process->p_process_data` points to a `Serialization_Request`.

### Error Handling

- `set_game_action_process_as__tcp_payload_receiver` returns false if
  `PLATFORM_allocate_serialization_request` fails.
