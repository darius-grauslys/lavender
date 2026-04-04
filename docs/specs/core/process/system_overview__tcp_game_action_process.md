# System Overview: TCP Game Action Process

## Purpose

The TCP game action process extends the game action process pattern for
multi-packet TCP communication. It enables a process to act as a TCP
payload receiver (reassembling fragmented deliveries) or a TCP payload
sender (splitting data into delivery fragments).

These functions bridge the `Process` scheduling system and the
`TCP_Delivery` game action fragmentation protocol, allowing large payloads
(e.g. chunk data, entity state) to be transmitted cooperatively without
blocking the main loop.

## Architecture

### Receiver Data Layout

When a game action process is converted to a TCP payload receiver:

    Process
    +-- void *p_process_data -> Serialization_Request*
    |                           +-- void *p_data -> Game_Action* (original)
    |                           +-- u8 *p_tcp_packet_destination -> destination buffer
    |                           +-- u8 *pM_packet_bitmap -> fragment bitmap (heap allocated)
    |                           +-- Quantity__u16 quantity_of__bytes_in__destination
    |                           +-- Quantity__u16 quantity_of__tcp_packets__anticipated
    +-- Process_Kind = Process_Kind__Game_Action
    +-- process_sub_state__u8 (handler state machine)

### Sender Data Layout

The sender does not modify the process's data layout. It operates on
caller-provided buffers:

    Process
    +-- void *p_process_data -> Game_Action* (unchanged)
    +-- Process_Kind = Process_Kind__Game_Action

    Caller provides:
    +-- u8 *source          (data to send)
    +-- Quantity__u32 source_size
    +-- u8 *bitmap          (fragment tracking bitmap, caller-managed)
    +-- Quantity__u16 bitmap_bits

### Key Types

| Type | Role |
|------|------|
| `Process` | The cooperative task unit carrying the game action. |
| `Game_Action` | The game action being processed. In receiver mode, moved to `Serialization_Request.p_data`. |
| `Serialization_Request` | Allocated for receiver mode. Tracks fragment reassembly state. |
| `PLATFORM_Read_File_Error` | Return type for receiver polling. Indicates busy, complete, or error. |
| `PLATFORM_Write_File_Error` | Return type for sender polling. Indicates busy, complete, or error. |

## TCP Fragment Protocol

### Fragment Model

Large payloads are split into fixed-size fragments that fit within a single
`TCP_Delivery` game action. Each fragment is identified by an index within
the payload. A bitmap tracks which fragments have been sent or received.

**Receiver side:** The `Serialization_Request` tracks:
- `p_tcp_packet_destination`: buffer where reassembled data is written.
- `quantity_of__bytes_in__destination`: total expected payload size.
- `quantity_of__tcp_packets__anticipated`: number of fragments expected.
- `pM_packet_bitmap`: heap-allocated bitmap (one bit per fragment).

**Sender side:** The caller provides:
- Source data buffer and size.
- A bitmap and bit count for tracking which fragments have been sent.

## Receiver Lifecycle

### 1. Setup

The process handler converts itself to a TCP payload receiver (typically
in sub-state 0):

    initialize_process_as__tcp_game_action_payload_receiver(
            p_game, p_process,
            destination_buffer,
            destination_size);

This function:
1. Allocates a `Serialization_Request` via
   `PLATFORM_allocate_serialization_request`.
2. Moves the original `Game_Action*` from `p_process->p_process_data` to
   `Serialization_Request.p_data`.
3. Sets `p_process->p_process_data` to the `Serialization_Request`.
4. Activates the serialization request in TCP mode, which:
   - Sets `p_tcp_packet_destination` to the destination buffer.
   - Sets `quantity_of__bytes_in__destination` to the destination size.
   - Calculates `quantity_of__tcp_packets__anticipated` from the size.
   - Heap-allocates `pM_packet_bitmap` for fragment tracking.

Returns false if allocation fails.

### 2. Fragment Reception (Per Poll Cycle)

Each poll cycle, the handler calls:

    PLATFORM_Read_File_Error err =
        poll_game_action_process__tcp_receive(p_game, p_process);

This function checks for incoming `TCP_Delivery` game actions addressed
to this process and copies their payload fragments into the destination
buffer at the correct offset. It updates the fragment bitmap accordingly.

| Return Value | Meaning |
|--------------|---------|
| `PLATFORM_Read_File_Error__System_Busy` | Still waiting for fragments. Continue polling next cycle. |
| `PLATFORM_Read_File_Error__End_Of_File` | All expected fragments have arrived. Payload is complete. |
| Any other value | Error. The handler should call `fail_process`. |

### 3. Data Processing

Once all fragments arrive, the handler processes the reassembled data in
the destination buffer:

    // destination_buffer now contains the full payload.
    // Access the original game action:
    Serialization_Request *p_sr =
        (Serialization_Request*)p_process->p_process_data;
    Game_Action *p_ga = (Game_Action*)p_sr->p_data;

### 4. Completion

    complete_process(p_process);
    // The default dispose handler releases both the
    // Serialization_Request and the Game_Action.

### Receiver Flow Diagram

    [Game Action Process] --> initialize_process_as__tcp_game_action_payload_receiver
                                  |
                                  v
                          [Serialization_Request allocated]
                          [Game_Action moved to SR.p_data]
                          [Fragment bitmap allocated]
                                  |
                                  v
                          +-----> poll_game_action_process__tcp_receive
                          |           |
                          |           v
                          |   [System_Busy?] --Yes--> (next poll cycle) --+
                          |           |                                    |
                          |          No                                    |
                          |           |                                    |
                          |   [End_Of_File?] --Yes--> [Process data]      |
                          |           |                    |               |
                          |          No (error)      complete_process      |
                          |           |                    |               |
                          |     fail_process          [Dispose]            |
                          |                                |               |
                          +--------------------------------+               |
                                                                           |
                          <-----------------------------------------------|

## Sender Lifecycle

### 1. Per Poll Cycle

The sender does not require special setup. Each poll cycle, the handler
calls:

    PLATFORM_Write_File_Error err =
        poll_game_action_process__tcp_delivery(
                p_game,
                client_uuid,
                response_uuid,
                source_data,
                source_size,
                bitmap,
                bitmap_bits);

This function sends one fragment per call by:
1. Finding the next unsent fragment in the bitmap.
2. Allocating a `TCP_Delivery` game action for the target client.
3. Copying the fragment data into the delivery game action.
4. Marking the fragment as sent in the bitmap.

| Return Value | Meaning |
|--------------|---------|
| `PLATFORM_Write_File_Error__System_Busy` | Fragment sent, but more remain. Continue next cycle. |
| `PLATFORM_Write_File_Error__Max_Size_Reached` | All fragments have been sent. The handler should call `complete_process`. |
| Any other value | Error. The handler should call `fail_process`. |

### 2. Completion

    complete_process(p_process);
    // Normal game action dispose handler runs.

### Sender Flow Diagram

    [Game Action Process running]
        |
        v
    +-> poll_game_action_process__tcp_delivery(...)
    |       |
    |       v
    |   [System_Busy?] --Yes--> (fragment sent, next poll cycle) --+
    |       |                                                       |
    |      No                                                       |
    |       |                                                       |
    |   [Max_Size_Reached?] --Yes--> complete_process               |
    |       |                                                       |
    |      No (error)                                               |
    |       |                                                       |
    |   fail_process                                                |
    |                                                               |
    +---------------------------------------------------------------+

## Complete Handler Examples

### Receiver Handler

    void my_receiver(Process *p_proc, Game *p_game) {
        switch (p_proc->process_sub_state__u8) {
            case 0: // Setup
                if (!initialize_process_as__tcp_game_action_payload_receiver(
                        p_game, p_proc,
                        my_buffer, sizeof(my_buffer))) {
                    fail_process(p_proc);
                    return;
                }
                set_process__sub_state(p_proc, 1);
                break;
            case 1: // Receive loop
                switch (poll_game_action_process__tcp_receive(p_game, p_proc)) {
                    case PLATFORM_Read_File_Error__System_Busy:
                        break; // Still waiting
                    case PLATFORM_Read_File_Error__End_Of_File:
                        set_process__sub_state(p_proc, 2);
                        break;
                    default:
                        fail_process(p_proc);
                        break;
                }
                break;
            case 2: // Process reassembled data
                // my_buffer contains the full payload
                complete_process(p_proc);
                break;
        }
    }

### Sender Handler

    void my_sender(Process *p_proc, Game *p_game) {
        Game_Action *p_ga = (Game_Action*)p_proc->p_process_data;
        switch (poll_game_action_process__tcp_delivery(
                p_game,
                get_client_uuid_from__game_action(p_ga),
                GET_UUID_P(p_ga),
                source_data,
                sizeof(source_data),
                my_bitmap,
                bitmap_bit_count)) {
            case PLATFORM_Write_File_Error__System_Busy:
                break; // More fragments to send
            case PLATFORM_Write_File_Error__Max_Size_Reached:
                complete_process(p_proc);
                break;
            default:
                fail_process(p_proc);
                break;
        }
    }

## Important Constraints

### Sender Independence

The sender function (`poll_game_action_process__tcp_delivery`) does NOT
require the process to be set up as a TCP payload receiver. It operates
on caller-provided buffers and can be used by any game action process.

### Dispose Handler Assumption

The default dispose handler assumes `Serialization_Request.p_data` is a
`Game_Action*`. If you repurpose `p_data` for non-game-action data, you
MUST release it manually and set it to NULL before completing or failing
the process.

### Fragment Bitmap Ownership

- **Receiver:** The `pM_packet_bitmap` is heap-allocated by
  `activate_serialization_request` and freed by
  `deactivate_serialization_request` during disposal. The process does
  not need to manage this memory manually.
- **Sender:** The bitmap is caller-managed. The caller must allocate it
  before the first `poll_game_action_process__tcp_delivery` call and
  free it after the process completes.

### Preconditions

- `initialize_process_as__tcp_game_action_payload_receiver`: the process
  must already be a game action process. The destination buffer must be
  pre-allocated and large enough for the expected payload.
- `poll_game_action_process__tcp_receive`: the process must have been
  set up as a TCP payload receiver.
- `poll_game_action_process__tcp_delivery`: the game action must be the
  process's assigned game action. The bitmap must be pre-allocated.

### Postconditions

- After `initialize_process_as__tcp_game_action_payload_receiver`:
  `p_process->p_process_data` points to a `Serialization_Request`.
- After `poll_game_action_process__tcp_receive` returns `End_Of_File`:
  the destination buffer contains the fully reassembled payload.
- After `poll_game_action_process__tcp_delivery` returns `Max_Size_Reached`:
  all fragments have been dispatched.

## Relationship to Other Process Types

| Concern | Managed By |
|---------|------------|
| Game action wrapping and default disposal | `game_action_process.h` |
| TCP fragment send/receive polling | `tcp_game_action_process.h` (this module) |
| Serialization request allocation | Platform layer (`PLATFORM_allocate_serialization_request`) |
| Fragment bitmap allocation/deallocation | Platform layer (`activate_serialization_request` / `deactivate_serialization_request`) |
| Process scheduling | `Process_Manager` / `Process_Table` |
