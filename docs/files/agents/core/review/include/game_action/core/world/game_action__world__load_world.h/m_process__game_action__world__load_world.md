m_process__game_action__world__load_world — core/source/game_action/core/world/game_action__world__load_world.c, lines 22-105

## 1. Header
- **Function name**: `m_process__game_action__world__load_world`
- **File of origin**: `core/source/game_action/core/world/game_action__world__load_world.c`

## 2. Semantic
This is a process handler (`m_Process` signature) that orchestrates the loading of world data for a specific client. It uses a state machine encoded in `process_valueA__i16` (values 0, 1, 2) to progress through three phases: (1) stat the world directory to determine the path to world data, (2) load local space manager data at the client's current position, and (3) poll until the local space manager reports it is fully loaded.

## 3. Pre-conditions
1. `p_this_process` must be non-null. It is the process being driven by this handler.
2. `p_this_process->p_process_data` must be a valid `Game_Action*` pointing to a `Game_Action` initialized with `initialize_game_action_for__world__load_world`, so that the payload contains a valid `GA_World_Load__Client` with a populated `uuid_of__client__u32`.
3. `p_game` must be non-null and must have an allocated `World` (via `pM_world`).
4. `p_game` must have an initialized `Hitbox_Context` with an `AABB` hitbox manager registered for the world's UUID, so that `get_pV_hitbox_manager_from__hitbox_context` returns a valid `Hitbox_AABB_Manager*`.
5. `p_game` must have a client pool allocated (`pM_ptr_array_of__clients` non-null) and the client identified by `uuid_of__client__u32` must exist in that pool.
6. The client identified by the UUID must have an allocated `Hitbox_AABB` component in the hitbox manager, so that `get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager` returns a valid pointer.
7. The world directory must exist on the platform file system so that `stat_world_directory` returns a non-zero index.
8. `p_this_process->process_valueA__i16` must be 0 on the first invocation (initial state), 1 when resuming at `load_world_data`, or 2 when resuming at `poll_world_data`. The function uses `goto` labels to jump to the correct state.

## 4. Post-conditions
1. On the first invocation (state 0): The world directory is stat'd. If successful, `process_valueA__i16` is set to 1 and the function returns without completing the process (the process remains active). If `stat_world_directory` fails (returns 0), the process is failed via `fail_process`.
2. On the second invocation (state 1, `load_world_data`): The client's hitbox AABB is retrieved and its position is converted to a chunk vector. `load_local_space_manager_at__global_space_vector__3i32` is called to initiate loading of local space data. `process_valueA__i16` is set to 2 and the function returns (process remains active). If the client lacks a hitbox component, the process is failed.
3. On the third invocation (state 2, `poll_world_data`): The function checks `is_local_space_manager__loaded`. If the local space manager is not yet loaded, the function returns without completing (process remains active, allowing re-polling). If loaded, the process is completed via `complete_process`.
4. If the client is not found (null `p_client`), a bad request game action is dispatched and the process is failed.

## 5. Correctness Verdict
**Correct**

## 6. Semantic Alignment
The implementation correctly fulfills the semantic intent of loading world data for a client through a multi-phase process. The state machine using `process_valueA__i16` and `goto` labels is a valid pattern for coroutine-like process handlers in this engine. Each state performs its designated task:
- State 0: Stats the world directory (filesystem preparation).
- State 1: Loads local space manager data at the client's chunk position.
- State 2: Polls until loading is complete, then completes the process.

The control flow is coherent and the function correctly transitions between states. The use of `goto` for state resumption is consistent with the engine's process model. No semantic drift is present.

## 7. Implementation Correctness
- **Type compatibility**: All parameter types match their target fields. `p_this_process` is `Process*`, `p_game` is `Game*`. The cast of `p_this_process->p_process_data` to `Game_Action*` is appropriate given the process is registered with `GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS`. The cast of the hitbox manager to `Hitbox_AABB_Manager*` is valid given the engine uses an opaque vtable pattern for hitbox managers.
- **Undefined behavior**: No null pointer dereferences occur. Each pointer obtained from a getter function is null-checked before use (e.g., `p_client`, `p_hitbox_aabb`). The `p_hitbox_aabb_manager` is obtained without a null check, but this is acceptable as it is derived from the game's world UUID via the hitbox context, which is expected to be initialized by engine setup.
- **Validation**: Validation is appropriate for the function's role. The client existence check and hitbox component check are performed within this function because they are essential to the function's correctness and the function is the process handler (not a high-level dispatcher). The `stat_world_directory` result is checked and handled appropriately.
- **State machine correctness**: The `switch` on `process_valueA__i16` with `goto` labels correctly implements the state resumption. The default case falls through to the initial state (state 0), which is the expected behavior for first invocation.

## 8. Side Effects
- **Mutates** `p_this_process->process_valueA__i16` to advance the state machine (0→1→2).
- **Mutates** `p_this_process->the_kind_of_status__this_process_has` to `Process_Status_Kind__Fail` (via `fail_process`) on error paths, or to `Process_Status_Kind__Complete` (via `complete_process`) on success.
- **Calls** `dispatch_game_action__bad_request` when the client is not found, which may allocate and enqueue a new game action and process (out of scope to trace, but is an observable side effect).
- **Calls** `load_local_space_manager_at__global_space_vector__3i32`, which resets the local space manager center and triggers `set_center_of__local_space_manager`, which in turn may spawn processes for loading global spaces.
- **Reads** from the hitbox manager, client pool, and world directory (filesystem I/O via `stat_world_directory`).
- Does **not** directly mutate the `Game_Action` payload or the `Client` struct, but indirectly triggers world loading through the local space manager.
