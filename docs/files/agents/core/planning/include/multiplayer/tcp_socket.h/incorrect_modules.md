# Planning: tcp_socket.h — Incorrect Modules

**Review file:** `agents/core/review/include/multiplayer/tcp_socket.h/incorrect_modules.md`
**Source:** `core/source/multiplayer/tcp_socket.c`
**Header:** `core/include/multiplayer/tcp_socket.h`
**Struct definition:** `core/include/defines.h` (Section `SECTION_multiplayer`)

Four functions in `core/source/multiplayer/tcp_socket.c` were flagged as
**Incorrect** in the review file. Each is analyzed below using terminology
from `agents/terminologies/index.md`.

---

## 1. Problem Identification

### 1.1 `receive_bytes_over__tcp_socket` — Incorrect

| Defect | Category |
|--------|----------|
| Returns `MAX_SIZE_OF__TCP_PACKET * quantity_of__received_packets` instead of the actual accumulated byte count from each `PLATFORM_tcp_recieve` call. | **Semantic Alignment** — violates the documented **Postcondition** ("Returns the quantity of bytes received"). |
| Swallows `TCP_ERROR__DESTINATION_OVERFLOW` (-1) by returning `0`. Since `0` is a valid "no bytes received" **Sentinel**, the caller cannot distinguish "no data" from "overflow error." | **Lossless** propagation violation — error codes are not propagated faithfully. |
| No **Precondition** null checks on `p_tcp_socket` or `p_PLATFORM_tcp_socket`. | **Conservative** invariant gap — inconsistent with `poll_tcp_socket_for__connection`. |
| `packet_size__entries` is never updated via the available `set_size_of__tcp_packet` helper. | **State Desync** — the **Representation Invariant** of per-packet byte-count metadata is violated. |

### 1.2 `send_bytes_over__tcp_socket` — Incorrect

| Defect | Category |
|--------|----------|
| Discards the return value of `PLATFORM_tcp_send` (bytes sent or -1 on error). The function signature returns `void`, providing no **Postcondition** feedback. | **Semantic Alignment** — send operation cannot be verified by the caller. |
| No **Precondition** null checks on `p_tcp_socket`, `p_PLATFORM_tcp_socket`, or `p_bytes`. | **Conservative** invariant gap — inconsistent with `poll_tcp_socket_for__connection`. |

### 1.3 `initialize_tcp_socket` — Incorrect

| Defect | Category |
|--------|----------|
| `memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket))` writes `sizeof(TCP_Socket)` bytes starting at the offset of `queue_of__tcp_packet` (the **second** field, after `_serialization_header`). This overflows past the end of the struct by `sizeof(Serialization_Header)` (8 bytes). | **Boundary Condition** — heap/stack buffer overflow. **Representation Invariant** violation. |
| The sibling `initialize_tcp_socket_as__deallocated` correctly uses `memset(p_tcp_socket, 0, sizeof(TCP_Socket))`, confirming the correct pattern. | — |

### 1.4 `get_latest__delivery_from__tcp_socket` — Incorrect

| Defect | Category |
|--------|----------|
| No **Precondition** null checks on `p_tcp_socket` or `p_tcp_packet__returned`. Dereferencing either null pointer is undefined behavior. | **Conservative** invariant gap. |
| The ring-buffer dequeue logic (`index_of__enqueue_begin++` with bitmask wrap) is semantically correct. | — |

---

## 2. Impact Assessment

### 2.1 `receive_bytes_over__tcp_socket`

**Callers (rely on broken behavior):**

1. `core/source/multiplayer/server__default.c` —
   `m_poll_tcp_socket_manager_as__server__default` calls
   `receive_bytes_over__tcp_socket` and tests the result with
   `if (!receive_bytes_over__tcp_socket(...))`. This treats `0` as "no data"
   and `non-zero` as "data present." The inflated return value
   (`MAX_SIZE_OF__TCP_PACKET * count`) means the caller always sees a
   truthy value when any packet is enqueued, which happens to work for the
   "did we receive anything?" question but masks the true byte count.

2. `core/source/multiplayer/client__default.c` —
   `m_poll_tcp_socket_manager_as__client__default` has the identical coupling:
   `if (!receive_bytes_over__tcp_socket(...))` followed by a single dequeue.

**How correcting invalidates assumptions:**

- Fixing the swallowed error code means `TCP_ERROR__DESTINATION_OVERFLOW`
  will propagate as `-1` instead of `0`. Both callers use the return value
  as a falsy/truthy check; a negative value is truthy in C, so the callers
  would incorrectly proceed to dequeue even on error. **Callers must be
  updated** to distinguish negative error codes from `0` (no data) and
  positive (bytes received).
- Fixing the return value to actual byte counts preserves the falsy/truthy
  semantics (0 = no data, positive = data), so this part is **Lossless**
  with respect to existing callers.
- Fixing the `packet_size__entries` update means `get_size_of__tcp_packet`
  will return real values instead of `0`. Currently both helpers
  (`get_size_of__tcp_packet` / `set_size_of__tcp_packet`) are `static inline`
  and **dead code** (never called outside `tcp_socket.c`), so the immediate
  blast radius is nil, but the **Invariant** becomes meaningful for future
  consumers.

### 2.2 `send_bytes_over__tcp_socket`

**Callers:** None found. The function is declared in `tcp_socket.h` and
implemented in `tcp_socket.c` but is **not called** anywhere in `core/`,
`sdl/`, `no_gui/`, or `tests/`.

**How correcting invalidates assumptions:**

- Changing the return type from `void` to `i32` is a **breaking change** to
  the public API declared in `tcp_socket.h`. Since there are no callers,
  the blast radius is limited to the declaration itself.
- The `PLATFORM_tcp_send` signature (`i32`: bytes sent or -1 on error) is
  already defined in `platform.h`, so the change is **Lossless** and
  **Sound** with respect to the platform contract.

### 2.3 `initialize_tcp_socket`

**Callers (rely on broken behavior):**

1. `core/source/multiplayer/tcp_socket_manager.c` —
   `accept_socket_on__tcp_socket_manager__ipv4` (line ~94) calls
   `initialize_tcp_socket` after allocating a socket from the contiguous
   pool array `TCP_Socket_Manager.tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS]`.
2. `core/source/multiplayer/tcp_socket_manager.c` —
   `open_socket_on__tcp_socket_manager__ipv4` (line ~124) calls
   `initialize_tcp_socket` after connecting.
3. `tests/core/source/multiplayer/test_suite_multiplayer_tcp_socket.c` —
   every test calls `initialize_tcp_socket` on a stack-allocated
   `TCP_Socket`.

**How correcting invalidates assumptions:**

- The overflow currently corrupts the first 8 bytes of the **next** socket in
  the contiguous pool (its `_serialization_header`). In the pool context
  (`tcp_sockets` array), this can corrupt the UUID/size metadata of an
  adjacent socket, potentially causing `get_p_tcp_socket_for__this_uuid` or
  `get_next_available__allocation_in__contiguous_array` to misbehave.
- On the stack (tests), the overflow corrupts adjacent stack variables,
  which may be masked by the tests' narrow assertions (they only check
  individual fields set after the memset).
- Correcting to `memset(p_tcp_socket, 0, sizeof(TCP_Socket))` will now zero
  `_serialization_header` before `initialize_serialization_header` sets it.
  No caller relies on `_serialization_header` being left in an un-zeroed
  state after `initialize_tcp_socket`, so this is **Lossless**.
- `open_server_socket_on__tcp_socket_manager__ipv4` uses a correct partial
  memset (`sizeof(TCP_Packet) * MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET`),
  confirming the intended pattern and highlighting the inconsistency.

### 2.4 `get_latest__delivery_from__tcp_socket`

**Callers:**

1. `core/source/multiplayer/server__default.c` —
   `m_poll_tcp_socket_manager_as__server__default` calls it in a `while`
   loop to drain the receive queue.
2. `core/source/multiplayer/client__default.c` —
   `m_poll_tcp_socket_manager_as__client__default` calls it once per poll.
3. `tests/core/source/multiplayer/test_suite_multiplayer_tcp_socket.c` —
   `get_latest__delivery_from__tcp_socket__empty_queue__returns_false`.

**How correcting invalidates assumptions:**

- All callers pass non-null pointers, so adding null checks is a
  **Conservative** defensive change with **no behavioral impact** on
  existing callers.
- Returning `false` for null input is consistent with the existing
  "queue empty" return, so no caller logic needs to change.

---

## 3. Resolution Assessment

### 3.1 `receive_bytes_over__tcp_socket`

**Implementation changes (`core/source/multiplayer/tcp_socket.c`):**

1. **Accumulate actual bytes received:** Introduce a running total
   `i32 total_bytes_received = 0;` and add `quantity_received` to it on each
   successful `PLATFORM_tcp_recieve` (positive return). Replace the final
   `return MAX_SIZE_OF__TCP_PACKET * p_tcp_socket->quantity_of__received_packets;`
   with `return total_bytes_received;`.
2. **Propagate error codes:** In the `TCP_ERROR__DESTINATION_OVERFLOW` case,
   `return TCP_ERROR__DESTINATION_OVERFLOW;` instead of `return 0;`.
3. **Add null checks:** Add `if (!p_tcp_socket || !p_tcp_socket->p_PLATFORM_tcp_socket) return 0;`
   (or an appropriate error code) at function entry, consistent with
   `poll_tcp_socket_for__connection`.
4. **Update `packet_size__entries`:** Call `set_size_of__tcp_packet(p_tcp_socket, p_tcp_packet, quantity_received)`
   for each packet that receives a positive byte count, so the
   **Representation Invariant** of per-packet size metadata is maintained.

**Caller updates:**

- `server__default.c` and `client__default.c` must update their falsy/truthy
  checks to explicitly handle negative error codes:
  ```c
  i32 result = receive_bytes_over__tcp_socket(p_tcp_socket__client);
  if (result <= 0) { continue; } // 0 = no data, negative = error
  ```
  This preserves the existing control flow while making error handling
  **Lossless** and explicit.

**Tests:**

- Augment `test_suite_multiplayer_tcp_socket.c` with cases for:
  - Error propagation (overflow returns negative).
  - Actual byte count return (not inflated).
  - Null pointer handling.

### 3.2 `send_bytes_over__tcp_socket`

**Implementation changes (`core/source/multiplayer/tcp_socket.c`):**

1. **Change return type** from `void` to `i32`.
2. **Return `PLATFORM_tcp_send`'s result** directly:
   `return PLATFORM_tcp_send(p_tcp_socket->p_PLATFORM_tcp_socket, p_bytes, length_of__bytes);`
3. **Add null checks:** Return `-1` (or `TCP_ERROR__DESTINATION_OVERFLOW`)
   if `p_tcp_socket`, `p_PLATFORM_tcp_socket`, or `p_bytes` is null.

**Header changes (`core/include/multiplayer/tcp_socket.h`):**

- Update the declaration from `void send_bytes_over__tcp_socket(...)` to
  `i32 send_bytes_over__tcp_socket(...)`.

**Caller updates:** None — no current callers exist.

**Tests:**

- Add tests verifying that `PLATFORM_tcp_send`'s return value is propagated,
  and that null inputs return an error code.

### 3.3 `initialize_tcp_socket`

**Implementation changes (`core/source/multiplayer/tcp_socket.c`):**

1. **Fix the buffer overflow:** Replace
   ```c
   memset(&p_tcp_socket->queue_of__tcp_packet, 0, sizeof(TCP_Socket));
   ```
   with
   ```c
   memset(p_tcp_socket, 0, sizeof(TCP_Socket));
   ```
   This matches the correct pattern in `initialize_tcp_socket_as__deallocated`.

**Caller updates:** None — the post-conditions (fields set after memset)
remain unchanged.

**Tests:**

- Add a test that verifies the struct is fully zeroed before field assignment
  (e.g., check that `packet_size__entries` is all zeros after init).
- Run under **AddressSanitizer** or equivalent **Static Analysis** to confirm
  no out-of-bounds writes.

### 3.4 `get_latest__delivery_from__tcp_socket`

**Implementation changes (`core/source/multiplayer/tcp_socket.c`):**

1. **Add null checks:** Add
   ```c
   if (!p_tcp_socket || !p_tcp_packet__returned)
       return false;
   ```
   at function entry, consistent with `poll_tcp_socket_for__connection`.

**Caller updates:** None — all current callers pass valid pointers.

**Tests:**

- Add a test case for null pointer handling (returns `false`).

---

## 4. Summary of Changes

| Function | File | Change | Caller Impact |
|----------|------|--------|---------------|
| `receive_bytes_over__tcp_socket` | `core/source/multiplayer/tcp_socket.c` | Accumulate actual bytes; propagate errors; null checks; update `packet_size__entries` | `server__default.c`, `client__default.c` must handle negative returns |
| `send_bytes_over__tcp_socket` | `core/source/multiplayer/tcp_socket.c` + `core/include/multiplayer/tcp_socket.h` | Return `i32`; propagate `PLATFORM_tcp_send` result; null checks | None (no callers) |
| `initialize_tcp_socket` | `core/source/multiplayer/tcp_socket.c` | Fix `memset` to start at struct base | None |
| `get_latest__delivery_from__tcp_socket` | `core/source/multiplayer/tcp_socket.c` | Add null checks | None |

**Blast radius:** Low-to-moderate. The `initialize_tcp_socket` overflow is the
most severe (memory corruption in the contiguous pool), but has the smallest
caller surface. The `receive_bytes_over__tcp_socket` changes require
coordinated caller updates in `server__default.c` and `client__default.c`.
The `send_bytes_over__tcp_socket` API change is breaking but has no current
callers, making it safe to fix now before adoption.
