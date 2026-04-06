# 1. Specification: core/include/serialization/serialization_request.h

## 1.1 Overview

Manages the lifecycle and state flags of `Serialization_Request`, which is the
engine's abstraction for an in-flight I/O or TCP transfer operation. A request
tracks a data pointer, a file handler (for disk I/O) or TCP packet destination
(for network), and a set of flags describing its current state.

## 1.2 Dependencies

- `defines.h` (for `Serialization_Request`, `Serialization_Request_Flags`,
  `PLATFORM_File_System_Context`)
- `defines_weak.h` (forward declarations)

## 1.3 Types

### 1.3.1 Serialization_Request

    typedef struct Serialization_Request_t {
        void *p_data;
        Serialization_Header *p_serialization_header;
        union {
            struct {
                void *p_file_handler;
                Quantity__u32 quantity_of__file_contents;
            };
            struct {
                u8 *p_tcp_packet_destination;
                u8 *pM_packet_bitmap;
                Quantity__u16 quantity_of__bytes_in__destination;
                Quantity__u16 quantity_of__tcp_packets__anticipated;
            };
        };
        Serialization_Request_Flags serialization_request_flags;
    } Serialization_Request;

| Field | Type | Description |
|-------|------|-------------|
| `p_data` | `void*` | Pointer to the data being serialized/deserialized. |
| `p_serialization_header` | `Serialization_Header*` | Header of the struct being serialized. |
| `p_file_handler` | `void*` | Platform-specific file handle (for I/O mode). |
| `quantity_of__file_contents` | `Quantity__u32` | Available for user usage; tracks file content size. |
| `p_tcp_packet_destination` | `u8*` | Destination buffer for TCP packets (for TCP mode). |
| `pM_packet_bitmap` | `u8*` | Bitmap tracking received TCP packets. Heap-allocated. |
| `quantity_of__bytes_in__destination` | `Quantity__u16` | Size of TCP destination buffer. |
| `quantity_of__tcp_packets__anticipated` | `Quantity__u16` | Expected number of TCP packets. |
| `serialization_request_flags` | `Serialization_Request_Flags` | Bitmask of state flags. |

### 1.3.2 Serialization_Request_Flags (u8)

| Flag | Bit | Description |
|------|-----|-------------|
| `SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED` | 0 | Request slot is allocated from the platform pool. |
| `SERIALZIATION_REQUEST_FLAG__IS_ACTIVE` | 1 | Request is currently in-flight. |
| `SERIALZIATION_REQUEST_FLAG__USE_SERIALIZER_OR_BUFFER` | 2 | Selects between serializer and raw buffer mode. |
| `SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE` | 3 | If set: reading. If clear: writing. |
| `SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE` | 4 | If set: request persists after completion. If clear: fire-and-forget. |
| `SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO` | 5 | If set: TCP mode. If clear: file I/O mode. |

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_serialization_request` | `(Serialization_Request*) -> void` | Zeroes out all fields and flags. |

### 1.4.2 Activation / Deactivation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `activate_serialization_request` | `(Serialization_Request*, void* file_handler, Quantity__u16 tcp_payload_size, bool is_tcp_or_io) -> bool` | `bool` | Activates the request. For TCP mode, allocates the packet bitmap (`pM_packet_bitmap`). Returns false if bitmap allocation fails. **WARNING**: Deactivate before calling a second time to avoid memory leaks. |
| `deactivate_serialization_request` | `(PLATFORM_File_System_Context*, Serialization_Request*) -> void` | `void` | Deactivates the request. Frees the packet bitmap if in TCP mode. Closes the file if in I/O mode. |

### 1.4.3 Flag Setters (static inline)

| Function | Description |
|----------|-------------|
| `set_serialization_request_as__allocated` | Sets `IS_ALLOCATED` flag. |
| `set_serialization_request_as__deallocated` | Clears `IS_ALLOCATED` flag. |
| `set_serialization_request_as__active` | Sets `IS_ACTIVE` flag. |
| `set_serialization_request_as__inactive` | Clears `IS_ACTIVE` flag. |
| `set_serialization_request_as__read` | Sets `READ_OR_WRITE` flag (reading). |
| `set_serialization_request_as__write` | Clears `READ_OR_WRITE` flag (writing). |
| `set_serialization_request_as__keep_alive` | Sets `KEEP_ALIVE` flag. |
| `set_serialization_request_as__fire_and_forget` | Clears `KEEP_ALIVE` flag. |
| `set_serialization_request_as__tcp` | Sets `IS_TCP_OR_IO` flag. |
| `set_serialization_request_as__io` | Clears `IS_TCP_OR_IO` flag. |

### 1.4.4 Flag Getters (static inline)

| Function | Returns | Description |
|----------|---------|-------------|
| `is_serialization_request__allocated` | `bool` | True if `IS_ALLOCATED` is set. |
| `is_serialization_request__active` | `bool` | True if `IS_ACTIVE` is set. |
| `is_serialization_request__reading` | `bool` | True if `READ_OR_WRITE` is set. |
| `is_serialization_request__writing` | `bool` | True if `READ_OR_WRITE` is NOT set. |
| `is_serialization_request__keep_alive` | `bool` | True if `KEEP_ALIVE` is set. |
| `is_serialization_request__fire_and_forget` | `bool` | True if `KEEP_ALIVE` is NOT set. |
| `is_serialization_request__tcp_or_io` | `bool` | True if `IS_TCP_OR_IO` is set (TCP mode). |

## 1.5 Agentic Workflow

### 1.5.1 Lifecycle

1. **Allocate** a request from the platform pool via
   `PLATFORM_allocate_serialization_request`.
2. **Initialize** with `initialize_serialization_request`.
3. **Configure** flags (read/write, tcp/io, keep_alive).
4. **Activate** with `activate_serialization_request`.
5. **Use**: The request is driven by the serialization process or
   platform I/O system.
6. **Deactivate** with `deactivate_serialization_request` when complete.
7. **Release** back to the platform pool via
   `PLATFORM_release_serialization_request`.

### 1.5.2 Preconditions

- `activate_serialization_request` must not be called twice without an
  intervening `deactivate_serialization_request` (memory leak).
- For TCP mode, `tcp_payload_size` must be non-zero.
- For I/O mode, `file_handler` must be a valid platform file handle.

### 1.5.3 Postconditions

- After `activate_serialization_request`: `IS_ACTIVE` flag is set. For TCP
  mode, `pM_packet_bitmap` is allocated.
- After `deactivate_serialization_request`: `IS_ACTIVE` flag is cleared.
  `pM_packet_bitmap` is freed (TCP) or file is closed (I/O).

### 1.5.4 Error Handling

- `activate_serialization_request` returns false if TCP bitmap allocation
  fails.

### 1.5.5 Platform Integration

Serialization requests are pooled per-platform:

- NDS: `PLATFORM_File_System_Context.serialization_requests[]`
- SDL: `PLATFORM_File_System_Context.SDL_serialization_requests[]`
- no_gui: `PLATFORM_File_System_Context.NO_GUI_serialization_requests[]`

Platform functions for request management:

- `PLATFORM_allocate_serialization_request`
- `PLATFORM_release_serialization_request`
- `PLATFORM_get_quantity_of__active_serialization_requests`
