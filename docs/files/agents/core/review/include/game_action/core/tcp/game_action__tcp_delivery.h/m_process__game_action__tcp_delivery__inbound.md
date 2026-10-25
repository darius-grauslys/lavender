## Function Review: m_process__game_action__tcp_delivery__inbound

**File of origin:** `core/source/game_action/core/tcp/game_action__tcp_delivery.c`

## Semantic

Processes an inbound TCP delivery game action by copying the action's payload into the corresponding Serialization_Request's destination buffer at the correct offset, marking the packet as received in the bitmap, and completing the process.

## Pre-conditions

1. `p_this_process` must be a non-null `Process*` whose `p_process_data` points to a valid `Game_Action` of kind `Game_Action_Kind__TCP_Delivery`.
2. `p_game` must be a non-null `Game*` with a valid `process_manager`.
3. The `Game_Action`'s `uuid_of__game_action__responding_to` must reference an existing `Process` in the game's process manager.
4. The referenced process must have `Process_Kind__Serialized` (the only valid kind for a TCP payload receiver).
5. The referenced process's `p_process_data` must point to a valid, properly activated `Serialization_Request` with its TCP union fields initialized (`p_tcp_packet_destination`, `pM_packet_bitmap`, `quantity_of__bytes_in__destination`, `quantity_of__tcp_packets__anticipated`).
6. `packet_index__u16` (extracted from the game action) must be less than `quantity_of__tcp_packets__anticipated` to pass the bounds check.

## Post-conditions

1. The payload bytes from the game action are copied into `p_serialization_request->p_tcp_packet_destination` at offset `GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * packet_index__u16`.
2. The corresponding bit in `p_serialization_request->pM_packet_bitmap` is set to indicate this packet has been received.
3. `p_this_process` is marked as `Process_Status_Kind__Complete` via `complete_process`.
4. If any validation fails, `p_this_process` is marked as `Process_Status_Kind__Fail` via `fail_process` and the function returns early.

## Correctness Verdict

Incorrect

## Semantic Alignment

The function's intent is to receive a TCP-delivered payload chunk and place it into the correct position within a serialization request's destination buffer, then mark it as received. The overall flow (lookup receiver process, validate kind, extract payload and index, copy data, set bitmap bit, complete process) aligns with this intent. However, the computation of `quantity_of__bytes_to__copy` contains an off-by-one error that causes the function to deviate from its intended behavior.

## Implementation Correctness

**Off-by-one bug in `quantity_of__bytes_to__copy` (CRITICAL):**

The second branch of the ternary computes the number of bytes to copy as:

```c
min__u32(
    GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES,
    p_serialization_request->quantity_of__bytes_in__destination
    - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
        * (packet_index__u16 + 1)));
```

The formula uses `(packet_index__u16 + 1)` instead of `packet_index__u16` when computing the remaining bytes in the destination buffer. The correct formula should compute the remaining bytes **for** this packet:

```
remaining = quantity_of__bytes_in__destination - (PAYLOAD_SIZE * packet_index__u16)
```

By using `(packet_index__u16 + 1)`, the code computes the remaining bytes **after** this packet's slot, not the remaining bytes **for** this packet. This produces two failure modes:

- **Second-to-last packet (data truncation):** When `total_bytes` is not a multiple of `PAYLOAD_SIZE`, the second-to-last packet copies fewer bytes than it should. For example, with `total_bytes=100`, `PAYLOAD_SIZE=32`, `packet_index=2`: the code computes `min(32, 100 - 96) = 4`, but should copy `min(32, 100 - 64) = 32`. Only 4 bytes are copied instead of 32, corrupting the destination buffer with missing data.

- **Last packet (buffer overflow):** For the last packet, the subtraction underflows (unsigned arithmetic wraps to a very large value), and `min(PAYLOAD_SIZE, huge_value)` returns `PAYLOAD_SIZE`, causing a `memcpy` that writes `PAYLOAD_SIZE` bytes when only a few remain. For example, with `total_bytes=100`, `PAYLOAD_SIZE=32`, `packet_index=3`: the code computes `min(32, 100 - 128)` → unsigned underflow → `min(32, ~huge) = 32`, but only 4 bytes of space remain. This is a buffer overflow writing 28 bytes past the end of the destination buffer.

The corresponding outbound function `poll_game_action_process__tcp_delivery` (in `core/source/process/tcp_game_action_process.c`) correctly uses `PAYLOAD_SIZE * index_of__bitmap_bit` (without the `+1`), confirming the intended formula.

**Type compatibility:** `packet_index__u16` is `u16` (uint16_t) and `quantity_of__bytes_in__destination` is `Quantity__u16` (uint16_t). The multiplication `PAYLOAD_SIZE * (packet_index + 1)` involves `size_t` (from `sizeof`) and `int` (promoted from uint16_t), resulting in `size_t`. The subtraction `quantity_of__bytes_in__destination - size_t_result` converts the uint16_t to `size_t` (unsigned), so when the result would be negative, it wraps around to a large positive value. This unsigned underflow is what enables the buffer overflow. The `min__u32` function takes `u32` parameters; the `size_t` argument may be truncated on 64-bit platforms, but since the values involved are small in practice, this is not an issue.

**Missing null checks:** The function does not validate that `p_serialization_request->p_tcp_packet_destination` or `p_serialization_request->pM_packet_bitmap` are non-null before use. While the `Process_Kind__Serialized` check provides some assurance that these fields are properly initialized (since `set_game_action_process_as__tcp_payload_receiver` is the only function that sets this kind and also activates the serialization request), explicit null checks would improve robustness.

**No null check on `p_this_process` or `p_game`:** The function dereferences both without validation. This is consistent with the codebase pattern where null checks for process and game pointers are handled by the caller or debug assertions in helper functions.

**First branch of ternary is correct:** When `quantity_of__bytes_in__destination < PAYLOAD_SIZE`, the entire destination fits within a single packet (index 0). The `quantity_of__tcp_packets__anticipated` check earlier ensures only `packet_index = 0` can reach this branch, so copying `quantity_of__bytes_in__destination` bytes is correct.

**Bitmap operations are correct:** `TCP_PAYLOAD_BYTE(index)` = `index >> 3` correctly computes the byte index, and `TCP_PAYLOAD_BIT(index)` = `index & MASK(3)` correctly computes the bit position within that byte.

**`min__u32` dependency:** The `min__u32` function/macro is not defined within the core module's headers. It is likely provided by a platform/backend implementation. This is not a bug in the function itself but is a dependency that should be documented.

## Side Effects

1. **Mutates `p_serialization_request->p_tcp_packet_destination`** — writes `quantity_of__bytes_to__copy` bytes starting at offset `PAYLOAD_SIZE * packet_index__u16`.
2. **Mutates `p_serialization_request->pM_packet_bitmap`** — sets the bit corresponding to `packet_index__u16`.
3. **Mutates `p_this_process`** — sets `the_kind_of_status__this_process_has` to `Process_Status_Kind__Complete` (or `Process_Status_Kind__Fail` on error paths).
4. **No other side effects** — no other global state is modified.
