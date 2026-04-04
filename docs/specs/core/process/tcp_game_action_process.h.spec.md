# Specification: core/include/process/tcp_game_action_process.h

## Overview

Provides TCP-specific extensions for game action processes. Enables a
process to act as a TCP payload receiver (reassembling multi-packet
deliveries) or a TCP payload sender (splitting data into delivery
fragments).

These functions are the bridge between the `Process` scheduling system
and the `TCP_Delivery` game action fragmentation protocol.

## Dependencies

- `defines.h` (for `Process`, `Game_Action`, `Serialization_Request`,
  `PLATFORM_Read_File_Error`, `PLATFORM_Write_File_Error`,
  `Identifier__u32`, `Quantity__u16`, `Quantity__u32`)

## Functions

### Receiver Setup

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `initialize_process_as__tcp_game_action_payload_receiver` | `(Game*, Process*, u8* destination, Quantity__u16 destination_size) -> bool` | `bool` | Converts a game action process into a TCP payload receiver. Allocates a `Serialization_Request` and activates it in TCP mode. The original `p_process_data` (game action) is moved to `Serialization_Request.p_data`. Returns false on failure. |

### Receiver Polling

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_game_action_process__tcp_receive` | `(Game*, Process*) -> PLATFORM_Read_File_Error` | `PLATFORM_Read_File_Error` | Call this every poll cycle for a TCP receiver process. Returns `PLATFORM_Read_File_Error__System_Busy` while waiting for fragments. Returns `PLATFORM_Read_File_Error__End_Of_File` when all expected fragments have arrived. Returns any other value as an error. |

### Sender Polling

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `poll_game_action_process__tcp_delivery` | `(Game*, Identifier__u32 client_uuid, Identifier__u32 response_uuid, u8* source, Quantity__u32 source_size, u8* bitmap, Quantity__u16 bitmap_bits) -> PLATFORM_Write_File_Error` | `PLATFORM_Write_File_Error` | Sends one fragment per call. Returns `PLATFORM_Write_File_Error__System_Busy` while fragments remain. Returns `PLATFORM_Write_File_Error__Max_Size_Reached` when all fragments have been sent. Returns any other value as an error. The process does NOT need to be set as a TCP process to use this function. |

## Agentic Workflow

### TCP Receive Pattern

Used when a game action process needs to receive a large payload
(e.g. chunk data, entity data) split across multiple `TCP_Delivery`
game actions:

    // In the process handler:
    void my_handler(Process *p_proc, Game *p_game) {
        switch (p_proc->process_sub_state__u8) {
            case 0: // Setup
                initialize_process_as__tcp_game_action_payload_receiver(
                        p_game, p_proc,
                        my_destination_buffer,
                        sizeof(my_destination_buffer));
                set_process__sub_state(p_proc, 1);
                break;
            case 1: // Receive loop
                switch (poll_game_action_process__tcp_receive(p_game, p_proc)) {
                    case PLATFORM_Read_File_Error__System_Busy:
                        break; // Still waiting for fragments
                    case PLATFORM_Read_File_Error__End_Of_File:
                        // All fragments received, process the data
                        set_process__sub_state(p_proc, 2);
                        break;
                    default:
                        fail_process(p_proc);
                        break;
                }
                break;
            case 2: // Process reassembled data
                // ... use my_destination_buffer ...
                complete_process(p_proc);
                break;
        }
    }

### TCP Send Pattern

Used when a game action process needs to send a large payload to a client:

    // In the process handler:
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
                complete_process(p_proc); // All sent
                break;
            default:
                fail_process(p_proc);
                break;
        }
    }

### Relationship to Serialization_Request

When a process is set as a TCP payload receiver, the data pointer chain is:

    Process.p_process_data
        --> Serialization_Request
            .p_data --> Game_Action (original)
            .p_tcp_packet_destination --> destination buffer
            .pM_packet_bitmap --> fragment tracking bitmap (heap allocated)
            .quantity_of__bytes_in__destination --> destination size
            .quantity_of__tcp_packets__anticipated --> expected fragment count

The `pM_packet_bitmap` is heap-allocated by `activate_serialization_request`
and freed by `deactivate_serialization_request` during process disposal.

### Important Constraint

If `Serialization_Request.p_data` is NOT a `Game_Action`, you MUST:

1. Release `p_data` manually before calling `complete_process` or
   `fail_process`.
2. Set `p_data` to NULL after releasing.

This is because the default dispose handler
(`m_process__dispose_handler__game_action__default`) assumes `p_data`
is a `Game_Action*` and will attempt to release it from the client's
`Game_Action_Manager`.

### Preconditions

- `initialize_process_as__tcp_game_action_payload_receiver`: the process
  must already be a game action process. The destination buffer must be
  pre-allocated and large enough for the expected payload.
- `poll_game_action_process__tcp_receive`: the process must have been
  set up as a TCP payload receiver.
- `poll_game_action_process__tcp_delivery`: `p_game_action` must be the
  process's assigned game action. The bitmap must be pre-allocated.

### Postconditions

- After `initialize_process_as__tcp_game_action_payload_receiver`:
  `p_process->p_process_data` points to a `Serialization_Request`.
- After `poll_game_action_process__tcp_receive` returns `End_Of_File`:
  the destination buffer contains the fully reassembled payload.
- After `poll_game_action_process__tcp_delivery` returns `Max_Size_Reached`:
  all fragments have been dispatched.

### Error Handling

- `initialize_process_as__tcp_game_action_payload_receiver` returns false
  if serialization request allocation fails.
- `poll_game_action_process__tcp_receive` returns error codes from
  `PLATFORM_Read_File_Error`.
- `poll_game_action_process__tcp_delivery` returns error codes from
  `PLATFORM_Write_File_Error`.
