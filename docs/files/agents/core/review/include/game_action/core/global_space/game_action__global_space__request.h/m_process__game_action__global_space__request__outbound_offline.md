m_process__game_action__global_space__request__outbound_offline — core/source/game_action/core/global_space/game_action__global_space__request__offline.c, lines 16-47

Processes a global space request in offline (singleplayer) mode. Extracts the requested global space vector from the game action's payload, looks up the corresponding Global_Space via the Global_Space_Manager, holds a reference to it (incrementing its reference count), and dispatches a Global_Space__Resolve game action.

Pre-conditions:
1. p_this_process must be a non-null pointer to a valid Process whose p_process_data points to a Game_Action of kind Game_Action_Kind__Global_Space__Request.
2. p_game must be a non-null pointer to a valid Game with an initialized World and Global_Space_Manager.
3. The Game_Action payload must contain a valid Global_Space_Vector__3i32 (gsv_3i32) identifying the requested global space.

Post-conditions:
1. The process status is set to Process_Status_Kind__Complete via complete_process(p_this_process), called early before the global space lookup.
2. If the global space is not found (p_global_space == NULL), the process status is overridden to Process_Status_Kind__Fail via fail_process(p_this_process), and an error is logged.
3. If the global space is found and is NOT deconstructing: the global space's quantity_of__references is incremented (via hold_global_space), and a Global_Space__Resolve game action is dispatched to the server handler.
4. If the global space is found but IS deconstructing: the process remains Complete, no resolve is dispatched, and no reference is held. (TODO: timeout not yet implemented.)

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of processing a global space request in offline mode. The function correctly extracts the global space vector from the game action payload, retrieves the global space from the manager, holds a reference to it, and dispatches a resolve action. This matches the expected behavior for the offline/singleplayer codepath.

The early complete_process() call is a deliberate design difference from the multiplayer server variant (m_process__game_action__global_space__request__outbound_server), which calls complete_process only after all setup is done. In the offline variant, complete_process is called optimistically before the lookup; if the lookup fails, fail_process overrides the status. This is valid since complete_process and fail_process simply set a status enum field with no transition validation.

The deconstructing case returns silently (process stays Complete) rather than dispatching a bad_request and failing as the server variant does. This is consistent with the offline mode having no server to report errors to, and is marked as a TODO.

Implementation Correctness:
Type compatibility — All types are fully compatible:
- get_gsv_3i32_from__ga_global_space__request returns Global_Space_Vector__3i32, which is a typedef for struct Vector__3i32_t (defined in defines_weak.h).
- The local variable gsv__3i32 is declared as Vector__3i32, also a typedef for struct Vector__3i32_t. Identical type, no conversion needed.
- get_p_global_space_from__global_space_manager accepts Chunk_Vector__3i32, also a typedef for struct Vector__3i32_t. Compatible.
- dispatch_game_action__global_space__resolve accepts Global_Space_Vector__3i32, also a typedef for struct Vector__3i32_t. Compatible.
No implicit conversions or truncation occur.

Undefined behavior — None. No broken pointer arithmetic, no null dereference (p_global_space is null-checked before use; p_this_process and p_game are validated by callee debug assertions), no type punning, no out-of-bounds access.

Validation — Appropriate for the function's role. The function checks for null p_global_space and for the deconstructing flag. Null validation on p_this_process and p_game is delegated to the callee functions (complete_process/fail_process have debug-mode null checks; get_p_global_space_manager_from__game would fail gracefully if p_game were null). This is consistent with the codebase pattern where low-level process handlers rely on debug assertions for parameter validation.

Side Effects:
1. Mutates p_this_process: sets the_kind_of_status__this_process_has to Process_Status_Kind__Complete (line 25). If the global space lookup fails, it is overridden to Process_Status_Kind__Fail (line 34).
2. Mutates Global_Space: increments quantity_of__references via hold_global_space(p_global_space) (line 43). This is a reference-counting side effect — the caller (or the dispatched resolve action) is responsible for eventually releasing this reference.
3. Dispatches a new game action (Global_Space__Resolve) via dispatch_game_action__global_space__resolve(p_game, gsv__3i32) (line 45), which creates a stack-local Game_Action and routes it through the game's dispatch handler.
4. Logs an error message via debug_error if the global space is not found (line 31).
