# Function Review: `m_process__game_action__entity__get__inbound_server`

**File of origin:** `core/source/game_action/core/entity/game_action__entity__get.c`

## Semantic

Server-side process handler for the `Entity__Get` game action. When a client requests an entity by UUID, this function looks up the entity on the server, then streams its `Entity_Data` to the requesting client via TCP delivery (packet-by-packet). The process remains active across multiple iterations until all TCP payload packets have been dispatched, at which point it is completed. If the entity cannot be found, a bad-request game action is dispatched back to the client and the process is failed.

## Pre-conditions

1. `p_this_process` is non-null and its `p_process_data` points to a valid `Game_Action` of kind `Game_Action_Kind__Entity__Get`.
2. `p_game` is non-null and its `pM_world` is allocated (required by `get_p_entity_manager_from__game`).
3. The `tcp_payload_bitmap` field within the game action's `GA_Entity__Payload` union has been zeroed by the corresponding `__init` function (`m_process__game_action__entity__get__inbound_server__init`), which runs before this handler on the first process iteration.
4. `p_game_action->uuid_of__client__u32` contains the UUID of the client that issued the `Entity__Get` request.
5. `p_game_action->_serialiation_header.uuid` contains the UUID of this game action, used as the response correlation ID for TCP delivery packets.
6. The entity manager is initialized and `MAX_QUANTITY_OF__ENTITIES` is sufficient for the hash table lookup.

## Post-conditions

1. If the entity is not found by UUID:
   - A `Bad_Request` game action is dispatched to the client (via `dispatch_game_action__bad_request`).
   - An error is logged via `debug_error`.
   - The process status is set to `Fail` via `fail_process`.
   - The function returns immediately.

2. If `poll_game_action_process__tcp_delivery` returns `PLATFORM_Write_File_Error__Max_Size_Reached`:
   - All TCP payload packets for the entity data have been dispatched.
   - The process status is set to `Complete` via `complete_process`.

3. If `poll_game_action_process__tcp_delivery` returns `PLATFORM_Write_File_Error__System_Busy`:
   - One or more (but not all) TCP payload packets have been dispatched.
   - The process status remains unchanged (still active/busy).
   - The function returns without completing or failing, allowing the process manager to re-invoke it on a subsequent iteration.

4. If `poll_game_action_process__tcp_delivery` returns any other value:
   - An error is logged via `debug_error`.
   - The process status is set to `Fail` via `fail_process`.

5. The `tcp_payload_bitmap` in the game action's payload is mutated: bits are set as each TCP delivery packet is dispatched.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent: it resolves an entity by UUID, streams its data to the requesting client via TCP delivery, and correctly manages the process lifecycle across multiple iterations. The use of `poll_game_action_process__tcp_delivery` to send data packet-by-packet is appropriate for the server-side response to an entity get request. The bitmap-based tracking of which packets have been sent is correctly zeroed in the `__init` function and consumed here.

The `Entity_Data` struct (containing `entity_flags` and `the_kind_of__entity`) is the correct payload to send — the client already knows the UUID it requested, so only the data portion is transmitted.

## Implementation Correctness

- **Type compatibility:** `sizeof(Entity_Data)` (type `size_t`) is passed where `Quantity__u32` is expected; this is safe for the small `Entity_Data` struct. The cast `(u16)TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity_Data)` matches the `Quantity__u16` parameter type of `poll_game_action_process__tcp_delivery`.
- **No undefined behavior:** No null pointer dereferences (pre-conditions guarantee valid pointers). No out-of-bounds array access. The bitmap pointer returned by `get_p_tcp_payload_bitmap__ga_entity__payload` is valid.
- **Switch handling:** All three meaningful return values of `poll_game_action_process__tcp_delivery` are handled. `Max_Size_Reached` breaks to completion, `System_Busy` returns early for re-invocation, and the `default` case catches any unexpected error. No fall-through issues.
- **Process state:** `complete_process` and `fail_process` are each called at most once per invocation path. There is no double-completion or double-failure.

## Side Effects

1. **TCP packet dispatch:** Calls `dispatch_game_action__tcp_delivery` (indirectly via `poll_game_action_process__tcp_delivery`) for each packet, sending `Entity_Data` to the client identified by `p_game_action->uuid_of__client__u32`.
2. **Bitmap mutation:** Sets bits in `tcp_payload_bitmap` within the game action's payload to track which packets have been sent.
3. **Process state change:** Calls `complete_process` or `fail_process` on `p_this_process`, modifying `p_this_process->the_kind_of_status__this_process_has`.
4. **Bad request dispatch (error path only):** Calls `dispatch_game_action__bad_request` which creates and dispatches a new game action to the client.
5. **Logging:** Emits debug error/info messages via `debug_error` and `debug_info`.

## Notes

- **Debug message mismatch (line 56):** The `debug_info` message reads `"m_process__game_action__entity__get__inbound_client, sent entity"` but this function is the **inbound_server** handler. This is a copy-paste error from the outbound client counterpart. It is misleading for debugging but does not affect functionality. The same error appears in the outbound client function (`m_process__game_action__entity__get__outbound_client`), suggesting the message was copy-pasted without correction.
- **Bad request code TODO (line 43):** `dispatch_game_action__bad_request` is called with `0` as the bad request code, with a `// TODO code` comment. A meaningful error code should be used instead.
- **Bitmap sizing:** The `tcp_payload_bitmap` field in `GA_Entity__Payload` is sized via `TCP_PAYLOAD_BITMAP(Entity, ...)` which uses `sizeof(Entity)` (the full struct including `Serialization_Header` and `Entity_Functions`), while the actual payload sent is `sizeof(Entity_Data)` only. Since `sizeof(Entity) >= sizeof(Entity_Data)`, the bitmap is always at least as large as needed. The init function zeroes the full bitmap via `SIZE_OF__TCP_PAYLOAD_BITMAP__ENTITY`, and the run handler uses only `TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(Entity_Data)` bits. This is safe but slightly wasteful — not a bug.
