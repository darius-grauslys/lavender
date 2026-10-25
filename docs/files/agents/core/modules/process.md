# Process — The Engine's Execution Engine

**Sources:** `core/source/process/` + `core/include/process/`

## Surface Concerns

The process system is the **execution engine** for the entire Lavender codebase. Every state mutation in the game — triggered by player input, networking, save/load, or game actions — is represented as a **Process**. The process manager is polled every frame; its `run_handler` executes per-tick logic and its `dispose_handler` performs the actual world mutation, decoupling **when** a mutation happens from **what** it does. Layer: L2 (engine services). Called from `game.c`'s frame loop (`poll_process_manager`), game-action resolution, `client.c` (save/load), and `multiplayer/` (TCP delivery).

- **Process status lifecycle** — a state machine: None → Enqueued → Idle → Busy → (Complete/Fail/Stopped) → None. `is_process__active()` returns true for Busy, Idle, and Stopping; `is_process__finished()` for Complete, Fail, and Stopped. Controlled by `process.h` inline helpers.
- **Priority table** — a fixed pool of 512 processes managed across 4 priority levels (0 = maximum). FIFO ordering within each priority via pointer-delimiter arrays in `Process_Priority_Table_Entry`. Confirmed source values override CHECKPOINT.md's stale "256 procs, 16 priority levels".
- **Criticality and poll loop** — the poll loop's continue condition is `is_process__critical(p_process) || !ticks_elapsed`, but the local `ticks_elapsed` is initialized to 0 and never incremented, so the condition is always true and **every** process in the table is visited on each poll. The per-tick budget the guard implies is not in effect, and `PROCESS_FLAG__IS_CRITICAL` has no observable effect today (the budget idiom appears to have been left unwired).
- **Enqueue links** — `enqueue_process(to, behind)` defers `to`'s execution until `behind` finishes. Enqueued processes are skipped during polling and dequeued automatically when their predecessor completes.
- **Subprocess links** — sub-processes are flagged via `set_process_as__sub_process()`; the parent manages the child's lifecycle.
- **Dispose semantics** — `release_process_from__process_manager` removes the process from the priority table, calls the dispose handler (which typically performs the final world mutation), then resets the slot to None.
- **UUID assignment** — `run_process()` assigns a random UUID from a seeded PRNG; `run_process_with__uuid()` accepts an explicit UUID for deterministic identity (e.g., game actions). The manager also maintains `next__uuid__u32`, an auto-incrementing counter.
- **Game-action wrapping** — the primary usage pattern. A `Game_Action` is dispatched via `dispatch_game_action_process()`, which creates a process with a dispose handler that resolves the action back to its kind via `Game_Action_Logic_Table`.

## Key Types

**`Process`** — defined in `defines.h`. The central struct. Key members:
- `Serialization_Header _serialization_header` — UUID identity via hash.
- `m_Process m_process_run__handler` / `m_process_dispose__handler` — per-tick and completion function pointers.
- `p_enqueued_process` / `p_sub_process` — union for enqueue links and sub-process references.
- `void *p_process_data` — opaque data passed to handlers.
- `process_valueA__i32` / `process_valueB__i32` — union with sub-state fields; free for handler use.
- `the_kind_of_status__this_process_has` — `Process_Status_Kind` enum state.
- `process_flags__u8` — bitflags including `PROCESS_FLAG__IS_CRITICAL`, `PROCESS_FLAG__IS_SUB_PROCESS`.
- `process_priority__u8` — priority level.

**`Process_Manager`** — defined in `defines.h`. Fixed-size pool of 512 embedded `Process` entries plus a `Process_Table` for priority management and a pointer to the latest allocated process.

**`Process_Table`** — embeds `process_priority_table[PROCESS_MAX_PRIORITY_LEVEL + 1]` (5 entries, index 4 is fallback for invalid priorities) and `ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF]`.

**`Process_Priority_Table_Entry`** — contains three `Process**` delimiters (`youngest_of_priority`, `oldest_of_priority`, `current_priority_to__swap`) into the process array for lock-free FIFO ordering.

## Key Functions

From `process_manager.h`:
- `void initialize_process_manager(Process_Manager *p_process_manager);`
- `void release_process_from__process_manager(Game *p_game, Process_Manager *p_process_manager, Process *p_process);` — teardown: remove from table, call dispose handler, reset slot.
- `Process *allocate_process_in__process_manager(Process_Manager *p_process_manager, Identifier__u32 uuid, uint32_t priority_level);` — returns process pointer or 0 on exhaustion.
- `Quantity__u32 poll_process_manager(Process_Manager *p_process_manager, Game *p_game);` — walks the process table once per poll; returns the game's elapsed ticks (`get_elapsed_ticks__u32F20_of__game`), not a per-poll count.
- `Process *run_process_with__uuid(Process_Manager *p_process_manager, m_Process m_process, Identifier__u32 uuid, Process_Priority__u8 process_priority__u8, Process_Flags__u8 process_flags__u8);` — returns process or 0.
- `Process *run_process(Process_Manager *p_process_manager, m_Process m_process, uint32_t priority_level, Process_Flags__u8 process_flags__u8);` — returns process or 0.
- `static inline Process *get_p_process_by__uuid(Process_Manager *p_process_manager, Identifier__u32 uuid__u32);` — returns process or 0 (defined in `process_manager.h`, not `process.h`).

From `process.h` (all `static inline`):
- `void initialize_process(Process *p_process, Identifier__u32 uuid__u32, m_Process m_process_run__handler, void *p_process_data, Process_Priority__u8 process_priority__u8, Process_Flags__u8 process_flags__u8);`
- `static inline void initialize_process_as__empty_process(Process *p_process);`
- `static inline void complete_process(Process *p_process);` / `void fail_process(Process *p_process);` / `void stop_process(Process *p_process);` — set terminal states.
- `static inline bool is_process__active(Process *p_process);` / `bool is_process__finished(Process *p_process);`
- `static inline bool is_process__critical(Process *p_process);` / `void set_process_as__critical(Process *p_process);`
- `static inline bool is_process__sub_process(Process *p_process);` / `void set_process_as__sub_process(Process *p_process);`
- `static inline void enqueue_process(Process *p_process_to__enqueue, Process *p_process_to__enqueue_behind);`
- `static inline bool is_process__enqueued(Process *p_process);`
- `static inline void set_process_as__enqueued(Process *p_process);` / `void set_process_as__dequeued(Process *p_process);`
- `static inline void set_process__dispose_handler(Process *p_process, m_Process m_process__dispose_handler);`
- `static inline void set_process__sub_state(Process *p_process, u8 sub_state__u8);`
- `static inline Process_Priority__u8 get_process_priorty_of__process(Process *p_process);` — load-bearing typo ("priorty").

## Known Rough Edges

- **`get_process_priorty_of__process`** — load-bearing typo. Must not be renamed without a project-wide search.
- **`is_process__finished` default case** — returns false (not finished) for unlisted statuses; a new status added without handling will therefore *never* be treated as finished, so its process is never released and its run handler keeps being polled.
- **`p_enqueued_process` / `p_sub_process` union** — two distinct semantics in one slot; not checked that an enqueued process is not also a sub-process.
- **The `|| !ticks_elapsed` guard** — reads like a per-tick budget idiom, but `ticks_elapsed` is never incremented inside `poll_process_manager`, so the guard is a no-op (always true) and the loop walks the entire table every poll. If a per-tick budget is ever intended, `ticks_elapsed` must actually be advanced.

## Key Files Table

| File | Role |
|------|------|
| `core/source/process/process.c` | `initialize_process` — zero-init + header setup |
| `core/source/process/process_manager.c` | `poll_process_manager`, `allocate`, `release`, UUID management |
| `core/source/process/process_table.c` | Priority table management, insertion/removal/polling |
| `core/source/process/process_priority_table_entry.c` | Pointer delimiter management for FIFO within priorities |
| `core/source/process/game_action_process.c` | Game action process wrapper + default dispose handler |
| `core/source/process/tcp_game_action_process.c` | TCP multi-packet receive/send for game actions |
| `core/source/process/filesystem_process.c` | Filesystem process wrapper + dispose handlers |
| `core/include/process/process.h` | Process state machine, flags, inline utilities |
| `core/include/process/process_manager.h` | Process manager API surface |
| `core/include/process/process_table.h` | Priority table public API |
| `core/include/process/process_priority_table_entry.h` | Priority table entry inline utilities |
| `core/include/process/game_action_process.h` | Game action process type |
| `core/include/process/tcp_game_action_process.h` | TCP payload receiver/delivery |
| `core/include/process/filesystem_process.h` | Filesystem process type |
| `core/include/defines.h` | Process, Process_Manager, Process_Table, Process_Priority_Table_Entry structs |
