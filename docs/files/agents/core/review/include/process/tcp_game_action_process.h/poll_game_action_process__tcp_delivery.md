# Function Review: poll_game_action_process__tcp_delivery

**File of origin:** `core/source/process/tcp_game_action_process.c`

## Semantic

Polls/delivers TCP game action packets by finding the next unsent packet (using a bitmap), dispatching it via `dispatch_game_action__tcp_delivery`, marking it as sent in the bitmap, and returning `System_Busy`. When all packets have been sent (bitmap fully set), returns `Max_Size_Reached`.

## Pre-conditions

1. `p_game` must be non-null — it is passed to `dispatch_game_action__tcp_delivery` which dereferences it.
2. `p_payload__source` must be non-null and contain at least `quantity_of__bytes_in__payload__source` bytes of valid data.
3. `p_payload__bitmap` must be non-null and have enough bytes to represent `quantity_of__bits_in__payload__bitmap` bits (i.e., at least `(quantity_of__bits_in__payload__bitmap + 7) / 8` bytes).
4. `quantity_of__bits_in__payload__bitmap` must correctly represent the number of TCP packets needed to deliver the payload (i.e., `ceil(quantity_of__bytes_in__payload__source / GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES)`).
5. The bitmap must be initialized to all zeros (no bits set) before the first call, so that `get_tcp_packet__bitmap_data` returns 0 (the first packet index).
6. `uuid_of__client_to__send_to` and `uuid_of__game_action__responding_to` must be valid identifiers for the target client and the game action being responded to.

## Post-conditions

1. If all packets have already been sent (i.e., `index_of__bitmap_bit >= quantity_of__bits_in__payload__bitmap`), the function returns `PLATFORM_Write_File_Error__Max_Size_Reached` without dispatching anything or modifying the bitmap.
2. Otherwise, the function dispatches the next unsent packet via `dispatch_game_action__tcp_delivery`, which creates a `Game_Action` of kind `TCP_Delivery` containing the packet's payload data and dispatches it for network transmission.
3. The bitmap is updated to mark the dispatched packet as sent: `p_bitmap[TCP_PAYLOAD_BYTE(index_of__bitmap_bit)] |= BIT(TCP_PAYLOAD_BIT(index_of__bitmap_bit))`.
4. The function returns `PLATFORM_Write_File_Error__System_Busy` to indicate more packets may remain.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent described in the header comment: "Returns System_Busy until it finishes with Max_Size_Reached."

### Byte count calculation analysis

The function computes the number of bytes to send for the current packet (at index `index_of__bitmap_bit`) as follows:

1. First, it computes the cumulative size if all packets from 0 to `index_of__bitmap_bit` were full-sized:
   ```
   quantity_of__bytes_to__send = GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * (index_of__bitmap_bit + 1)
   ```

2. Then it checks if this cumulative size exceeds the total source payload size:
   - **If yes** (current packet is the last, partial packet): sends the remaining bytes:
     ```
     quantity_of__bytes_in__payload__source - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * index_of__bitmap_bit)
     ```
     This correctly computes `source_size - (packet_size * packet_index)`, which is the number of remaining bytes in the source for this final packet.
   - **If no** (current packet is a full packet): sends `GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES` bytes.

This logic is correct. The check `cumulative_size > source_size` properly identifies the last (potentially partial) packet.

### Payload offset calculation

The dispatch call uses:
```
p_payload__source + (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * index_of__bitmap_bit)
```
This correctly computes the starting offset of the current packet's data within the source payload.

### Bitmap update

The bitmap update correctly marks the sent packet:
- `TCP_PAYLOAD_BYTE(index) = index >> 3` selects the correct byte in the bitmap.
- `TCP_PAYLOAD_BIT(index) = index & MASK(3)` selects the correct bit within that byte.
- `BIT(n) = 1 << n` sets the appropriate bit.

This is consistent with how `get_tcp_packet__bitmap_data` scans the bitmap to find the next unset bit.

### Consistency with receiving side

The receiving side (`m_process__game_action__tcp_delivery__inbound` in `game_action__tcp_delivery.c`) uses the same `TCP_PAYLOAD_BYTE` and `TCP_PAYLOAD_BIT` macros with the packet index received from the dispatched `Game_Action`, and performs the same bitmap marking. The offset calculation on the receiving side (`GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * packet_index`) matches the sending side. This confirms semantic consistency.

## Implementation Correctness

### Type compatibility

- `index_of__bitmap_bit` is `Index__u32` (uint32_t). It is compared against `quantity_of__bits_in__payload__bitmap` (Quantity__u16 / uint16_t). The uint16_t is promoted to uint32_t for the comparison — no truncation or implicit conversion issues.
- `GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES` is a `size_t` expression (`sizeof(TCP_Packet) - sizeof(_Game_Action_Header) - sizeof(uint64_t)`). When multiplied by `index_of__bitmap_bit` (uint32_t), the result is `size_t`. Assignment to `quantity_of__bytes_to__send` (uint32_t) is safe in practice since the values are bounded by the TCP packet size and packet count.
- `index_of__bitmap_bit` (Index__u32 / uint32_t) is passed to `dispatch_game_action__tcp_delivery` as `Index__u16` (uint16_t). This is an implicit narrowing conversion, but it is safe because `index_of__bitmap_bit` is bounded by `quantity_of__bits_in__payload__bitmap` (which is `Quantity__u16`, max 65535), and the early return at line 147-150 ensures `index_of__bitmap_bit < quantity_of__bits_in__payload__bitmap` before the dispatch call.
- `quantity_of__bytes_to__send` (Quantity__u32 / uint32_t) is passed to `dispatch_game_action__tcp_delivery` as `u32` (uint32_t) — exact type match.

### Undefined behavior

- No null pointer dereferences: the function does not check for null pointers, but this is consistent with the codebase's pattern — validation is the caller's responsibility (the header comment states "You >>DO NOT<< have to set your process as a tcp process to call this function," implying the caller provides valid arguments).
- No out-of-bounds access within this function: the bitmap access `p_bitmap[TCP_PAYLOAD_BYTE(index_of__bitmap_bit)]` is within bounds because `index_of__bitmap_bit < quantity_of__bits_in__payload__bitmap` (guaranteed by the early return check), so `TCP_PAYLOAD_BYTE(index_of__bitmap_bit) < (quantity_of__bits_in__payload__bitmap + 7) / 8`.
- No null dereference: `p_bitmap` is used directly from `p_payload__bitmap` without null check, but this is the caller's responsibility.
- The pointer arithmetic `p_payload__source + (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES * index_of__bitmap_bit)` is within bounds of the source payload (the early-return check and the byte-count calculation ensure we don't read past `quantity_of__bytes_in__payload__source`).

### Validation

Validation is appropriate for the function's role. The function trusts the caller to provide valid pointers and consistent sizes, which is the codebase's established pattern. The function does validate the bitmap state (checking if all packets are sent) and computes correct byte counts and offsets.

## Side Effects

1. **Network dispatch**: Calls `dispatch_game_action__tcp_delivery`, which creates a stack-allocated `Game_Action`, initializes it with the packet payload data, and dispatches it via `dispatch_game_action` (which calls the game's `m_game_action_handler__dispatch` handler). This results in a TCP packet being sent to the specified client.
2. **Bitmap mutation**: Modifies `p_payload__bitmap` by setting the bit corresponding to the dispatched packet at index `index_of__bitmap_bit`.
3. No other global state is modified. The function does not allocate or deallocate memory.

## Lavender-Specific Semantics Note

This function is **not** an initialization/reset function. It is a polling/delivery function that dispatches TCP packets. The Lavender-specific "initialization ≠ RAII" semantic does not apply here.
