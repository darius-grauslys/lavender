m_process__game_action__global_space__request__outbound_client — core/source/game_action/core/global_space/game_action__global_space__request__multiplayer.c, lines 181-245

## Semantic

Polls for TCP reception of a global space request response from the server on behalf of the client. On successful reception (EOF), marks the global space as no longer constructing and completes the process. On bad request or failure, drops the global space and fails the process. On system busy with no timeout elapsed, returns early to retry on the next tick.

## Pre-conditions

1. `p_this_process` must be a non-null pointer to a valid `Process` whose `p_process_data` is a `Serialization_Request*`.
2. `p_game` must be a non-null pointer to a valid `Game`.
3. `p_serialization_request->p_data` must be a non-null `Game_Action*` containing a valid `GA_Global_Space__Request` payload (i.e., the global space vector and timeout timer fields must be accessible).

## Post-conditions

1. If the game action is flagged as a bad request: the global space at the request's vector is dropped via `drop_global_space_within__global_space_manager`, and the process is failed.
2. If `poll_game_action_process__tcp_receive` returns `PLATFORM_Read_File_Error__End_Of_File`: the TCP reception is considered complete. The function then looks up the global space; if found, it marks it as NOT constructing via `set_global_space_as__NOT_constructing` and completes the process. If the global space is not found, the process is failed.
3. If `poll_game_action_process__tcp_receive` returns `PLATFORM_Read_File_Error__System_Busy`: the timeout timer is polled with the elapsed game time. If the timer has not elapsed, the function returns early (process remains active/idle). If the timer has elapsed, the process is failed with a timeout error.
4. For any other return value from `poll_game_action_process__tcp_receive` (default case): the process is failed with a reception-failed error.

## Correctness Verdict

Incorrect

## Semantic Alignment

The implementation does not fully fulfill its semantic intent due to a critical type confusion bug in the `get_p_timeout_timer_u32_from__ga_global_space__request` accessor function (defined in `include/types/core/game_action/global_space/ga_type__global_space__request.h`, line 75-80). That function is declared to return `Timer__u32*` but instead returns `&...->gsv_3i32`, pointing into the `Global_Space_Vector__3i32` field rather than the `timeout__timer_u32` field. The struct `GA_Global_Space__Request` has three fields:

```c
Global_Space_Vector__3i32 gsv_3i32;
TCP_PAYLOAD_BITMAP(Chunk, chunk_payload_bitmap);
Timer__u32 timeout__timer_u32;
```

The by-value accessor `get_timeout_timer_u32_from__ga_global_space__request` correctly accesses `->timeout__timer_u32`, but the pointer-returning variant `get_p_timeout_timer_u32_from__ga_global_space__request` erroneously accesses `->gsv_3i32`. This means:

- In this function, `poll_timer_by__this_duration_u32` receives a `Timer__u32*` that actually points to a `Global_Space_Vector__3i32`. The timer function reads `remaining__u32` and `start__u32` which alias the first two `i32` components (`x__i32`, `y__i32`) of the vector. This is undefined behavior and means the timeout logic operates on corrupted/incorrect data.
- In the `_init` function (`m_process__game_action__global_space__request__outbound_client__init`), `initialize_timer_u32` writes timer start/remaining values into the `gsv_3i32` field, corrupting the global space vector used elsewhere in the function.

The semantic intent is to poll a timeout timer initialized during the init phase. Due to this bug, the timer is never actually initialized or polled against the correct memory, so the timeout mechanism is non-functional.

## Implementation Correctness

- **Type compatibility:** The `poll_timer_by__this_duration_u32` function expects `Timer__u32 *` and `u32`. The first argument comes from `get_p_timeout_timer_u32_from__ga_global_space__request` which returns `Timer__u32*` but actually points to `gsv_3i32` (a `Global_Space_Vector__3i32`). This is a type mismatch — the returned pointer aliases the wrong struct member. The second argument `get_elapsed_time__u32F20_of__game` returns `u32F20`, which is a typedef for `uint32_t` (same as `u32`), so that conversion is fine.
- **Undefined behavior:** The type confusion in `get_p_timeout_timer_u32_from__ga_global_space__request` constitutes undefined behavior. Reading `Timer__u32` fields (`remaining__u32`, `start__u32`) from memory that actually holds a `Global_Space_Vector__3i32` is a type-punning violation. The `remaining__u32` field aliases `x__i32` and `start__u32` aliases `y__i32` of the vector struct. This means the timeout check uses the global space vector's x and y coordinates as timer values, producing nonsensical results.
- **Null dereference:** No null dereference issues in this function itself — `p_global_space` is checked before use, and `p_game_action` is obtained from the serialization request (pre-condition).
- **Validation:** The function appropriately checks for bad requests, null global space, and handles TCP receive errors. The validation logic is sound in structure, but the timeout mechanism it relies on is broken due to the accessor bug.

## Side Effects

1. May call `drop_global_space_within__global_space_manager` (mutates global space manager state) when the request is a bad request.
2. Calls `poll_game_action_process__tcp_receive` which mutates the serialization request's internal packet tracking state.
3. May call `poll_timer_by__this_duration_u32` which mutates the timer's `remaining__u32` field (though due to the bug, it mutates the `gsv_3i32` field instead).
4. May call `set_global_space_as__NOT_constructing` which mutates the global space's flags (clears the constructing flag and awaiting-construction flag).
5. Calls `fail_process` or `complete_process` which mutate the process status.
6. Calls `debug_error` which produces log output.
