# Function Review: poll_process_manager

- **Function name**: `poll_process_manager`
- **File of origin**: `core/source/process/process_manager.c`

## Semantic

Polls all active processes in the `Process_Manager`'s process table, executing each
process's run handler or completing/releasing finished processes. Returns the game's
elapsed tick count.

## Pre-conditions

1. `p_process_manager` must be non-null and initialized (via `initialize_process_manager`).
2. `p_game` must be non-null and initialized (via `initialize_game`).
3. The process table within `p_process_manager` must have been initialized (via
   `initialize_process_table` or `initialize_process_manager`).
4. `p_game->tick_accumilator__u32F20` must be in a valid state (set during game
   initialization and updated by `manage_game__post_render` / `reset__game_tick_timer`).

## Post-conditions

1. All non-enqueued, non-finished processes in the table have their `m_process_run__handler`
   invoked (if the handler is non-null).
2. Finished processes (Complete, Fail, Stopped) are released from the process manager
   via `release_process_from__process_manager`, which removes them from the table,
   invokes their dispose handler (if present), and reinitializes them as empty processes.
3. Enqueued processes (`Process_Status_Kind__Enqueued`) are skipped.
4. Processes without a run handler (`m_process_run__handler == 0`) are marked as
   Complete via `complete_process`.
5. `p_process_manager->p_process__latest` is set to `0`.
6. The return value is `get_elapsed_ticks__u32F20_of__game(p_game)`, which is
   `(p_game->tick_accumilator__u32F20 >> 15)`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation does not fulfill the apparent semantic intent suggested by the
`ticks_elapsed` variable and the `is_process__critical` check in the while loop
condition. The variable `ticks_elapsed` is initialized to `0` but is never modified
anywhere in the function body. This means `!ticks_elapsed` is always `true`, making
the `is_process__critical(p_process)` check in the `||` expression dead code. The
loop processes ALL processes in the table regardless of whether they are critical.

The apparent intent was to limit processing to critical processes plus at most one
non-critical process (or similar throttling behavior), but this was never implemented.
Since `ticks_elapsed` is never assigned, the loop effectively becomes
`while ((p_process = poll_next_p_process_from__process_table(...)) && true)`,
processing every process in the table in a single call.

Additionally, the header comment states "Returns quantity of ticks elapsed," but the
function returns `get_elapsed_ticks__u32F20_of__game(p_game)` (the game's accumulated
tick time), not the local `ticks_elapsed` variable. The return value is currently
unused by all callers (`manage_game__post_render` and `run_game` in `game.c`), so this
semantic mismatch has no immediate impact.

## Implementation Correctness

1. **No undefined behavior**: No null dereferences, out-of-bounds access, or type
   punning. The `poll_next_p_process_from__process_table` function returns a valid
   `Process*` or `0`, and the while condition guards against null.

2. **Redundant null check**: The `if (!p_process) break;` inside the loop body is
   dead code. The while loop condition already ensures `p_process` is non-null
   before entering the body (the assignment in the condition is checked with `&&`).

3. **Type compatibility**: All parameter types match their expected targets.
   `Quantity__u32` return type matches `uint32_t`. `Process*` and `Game*` pointers
   are used correctly throughout.

4. **No parameter validation**: The function does not validate that `p_process_manager`
   or `p_game` are non-null. However, the header marks this as "Don't invoke"
   (internal), and all callers pass valid pointers obtained from game/subsystem
   accessors.

5. **Enqueued process handling**: When a finished process has an `p_enqueued_process`,
   the enqueued process is dequeued (set to `Process_Status_Kind__Idle`) before the
   parent process is released. This is correct.

## Side Effects

1. **Mutates `p_process_manager->p_process__latest`**: Set to `0` at function entry.
2. **Mutates process table state**: The polling cursor
   (`process_table.p_process_priority_table_entry__current`) is advanced as processes
   are polled. Finished processes are removed from the table.
3. **Invokes process run handlers**: Each active process's `m_process_run__handler` is
   called with `(p_process, p_game)`, which may mutate game state, processes, or other
   subsystems.
4. **Releases finished processes**: Calls `release_process_from__process_manager`, which
   invokes dispose handlers and reinitializes processes as empty (Lavender-style
   initialization, returning them to the free pool).
5. **Completes handlerless processes**: Calls `complete_process` on processes with a
   null run handler, marking them as `Process_Status_Kind__Complete`.
6. **Reads `p_game` state**: Calls `get_elapsed_ticks__u32F20_of__game(p_game)` to
   obtain the return value, which reads `p_game->tick_accumilator__u32F20`.
