# Outstanding Item 1 — Neighbor checks orphan chunks and saturate the process pool

**Question:** Can chunk-generator processes remain idle forever waiting on neighbors? Is that what orphans chunks and saturates the pool?
**Answer: Yes — and the investigation found 5 distinct mechanisms. Two are pre-existing design
gaps, and two are bugs introduced by the performance work (currently uncommitted in this tree).
The "forever wait" is real, but the dominant saturation mechanism in the current tree is the
4096-frame cutoff in `poll_process_manager`, not the neighbor polling itself.**

Date: 2026-09-17. All line numbers refer to the working tree at the time of writing.

---

## 1. Baseline architecture (current state)

- A chunk generator process is not spawned directly. The
  `game_action__global_space__resolve` process **mutates itself** into the generator:
  `core/source/game_action/core/global_space/game_action__global_space__resolve.c:141-161`
  (sets `p_global_space->p_generation_process`, clears `PROCESS_FLAG__IS_CRITICAL`,
  re-points the run handler). Registration is `PROCESS_PRIORITY__0_MAXIMUM` +
  `PROCESS_FLAG__IS_CRITICAL` (line 176-177) — i.e. **the generator runs non-critical, in the
  highest non-critical priority band**.
- Generator state machine
  (`AncientsGame/source/world/implemented/ag__chunk_generator_overworld.c`):
  - `Terrain` (first poll, lines 774/797-939): generates the entire 8×8×8 chunk in one poll,
    sets `CHUNK_FLAG__MODDABLE_0` (`CHUNK_FLAG__IS_DONE_TERRAIN`, line 696), moves to
    `Awaiting_Neighbors`.
  - `Awaiting_Neighbors` (lines 776-794): calls `poll_global_space_neighbors` (8 dehash
    lookups, lines 721-752). While flags ≠ 0xFF it checks
    `is_global_space__awaiting_deconstruction` (escape hatch, line 785) and returns.
    At 0xFF it swaps the handler to `m_process__chunk_generator__slope_resolver`.
  - `slope_resolver` (lines 942-1021): re-polls the 8 neighbors; needs all 8 neighbor
    `Global_Space`s **and** all 8 neighbor `Chunk`s non-NULL (lines 980-996); if any neighbor
    chunk is NULL it swaps the handler **back** to the overworld handler (line 991-993).
    Otherwise it resolves slopes across all 8 z-layers and completes.
- Per-process timeout (perf work, uncommitted): `Process.process_timer__ticks_u16`
  (`core/include/defines.h`), initialized to `PROCESS_TICK_TIMEOUT_U16F4 = BIT(13)` (u16F4 ⇒
  512 ticks ≈ 16 s) in `initialize_process` (`core/source/process/process.c`), advanced in
  `poll_process_manager` (`core/source/process/process_manager.c:194-197`), checked by the
  overworld handler (line 765-770 → `fail_process`). The slope resolver's timeout check is
  **commented out** (lines 954-962, "TODO: ensure we dont need timeout").
- Pool size: `PROCESS_MAX_QUANTITY_OF = BIT(14) = 16384` (AncientsGame
  `engine_config.h`, bumped from BIT(11)=2048 in commit `9a982aa`). Global-space pool:
  `QUANTITY_OF__GLOBAL_SPACE = 648 × 4 = 2592`.
- The manager polls **once per engine frame** from `manage_game__post_render`
  (`core/source/game.c:745-748`); the engine frame = one 32 Hz tick (busy-wait scene loop).

---

## 2. Mechanism A (pre-existing, by design): edge-of-volume waiters

The local-space volume is 9×9×8 chunks around the client
(`local_space_manager.c`; `LOCAL_SPACE_MANAGER__{WIDTH,HEIGHT,DEPTH} 9/9/8`).
A chunk at the volume's outer shell has horizontal neighbors **outside** the volume; those
neighbor global spaces are only allocated when a local space references them
(`hold_global_space_within__global_space_manager`, `global_space_manager.c:150-201`), so they
are never allocated. `poll_global_space_neighbors` then never sees those bits set (a missing
neighbor fails `is_global_space__finished_terrain` at `ag__chunk_generator_overworld.c:700-708`),
and the chunk sits in `Awaiting_Neighbors` **indefinitely** — until the player moves the chunk
out of the volume, at which point the `awaiting_deconstruction` check (line 785) completes it
without slope resolution.

Impact: bounded and recoverable by design, but a stationary player keeps a persistent ring of
~300 edge chunks re-running 8 dehashes per tick each. This is the steady-state cost the
callgrind pointed at — but it does **not** by itself saturate a 16384-slot pool (max 648
waiters, one per in-volume chunk).

## 3. Mechanism B (pre-existing): slope-resolver ping-pong

In `slope_resolver`, "all neighbors terrain-finished" (0xFF) is checked before fetching
neighbor chunks. If a neighbor's `Global_Space` exists but its `Chunk` was never allocated
(pool allocation failure, or the neighbor generator never ran), the handler swaps back to the
overworld handler (line 991-993) — which, seeing 0xFF again, immediately swaps back to the
resolver on the next poll. **Infinite ping-pong, never completes, slot occupied forever**
(pre-cutoff). Each cycle is cheap (~16 dehashes + 8 pointer reads), so this is a slot leak,
not a CPU burn. The commented-out timeout check (line 954-962) means this state has **no
escape hatch at all** — unlike the overworld handler, which at least fails on timeout.

## 4. Mechanism C (perf-work BUG — the big one): the 4096-frame cutoff

`poll_process_manager` (`process_manager.c:159-166`, uncommitted perf work):

```c
Quantity__u32 ticks_elapsed = get_ticks_elapsed__game(p_game);
while ((p_process = poll_next_p_process_from__process_table(...))
        && (is_process__critical(p_process) || (ticks_elapsed < 4096))) { ... }
```

- `get_ticks_elapsed__game` = `get_time_elapsed_from__timer_u32(&p_game->tick__timer_u32)`
  (`core/include/game.h:146-148`).
- **`tick__timer_u32` is never initialized.** `initialize_game` (`core/source/game.c:97-127`)
  memsets the Game and initializes `time__seconds__u32` / `time__nanoseconds__u32` — but no
  `initialize_timer_u32` call ever touches `tick__timer_u32` (verified by exhaustive grep;
  only `loop_timer_u32` at `game.c:756` writes it).
- With `start = remaining = 0`, `loop_timer_u32` (`timer.h:118-123`) underflows:
  frame 1 → `remaining = 0xFFFFFFFF`, `elapsed = 0 − remaining = 1`; frame N → `elapsed = N`.
  So `ticks_elapsed` initializes to **the raw frame counter**.
- The loop budget `ticks_elapsed < 4096` is therefore **true for frames 1–4095 and false for
  every frame from 4096 onward** (4096 frames = 128 s at 32 Hz). The in-loop accumulation
  (`ticks_elapsed += ... >> 20`, line 191-193) adds at most 0–1 per process (a frame is one
  tick of u32F20) and cannot compensate.

**Consequence: after ~128 s of gameplay, `poll_process_manager` never runs any non-critical
process again, ever.** All pending chunk generators freeze mid-state. Because processes are
only *released inside the poll loop* (`process_manager.c:169-178`), every frozen process
occupies its pool slot **forever**; every `p_generation_process` back-pointer dangles; new
allocations start failing as the pool fills (`allocate_process_in__process_manager`,
lines 119-131). Meanwhile, critical processes (resolve, store, TCP) keep running: post-cutoff,
a newly requested chunk's resolve process runs, allocates the chunk, **mutates itself into a
generator and clears the critical flag** — then the generator is never polled again. Each
such chunk is a zombie pair (frozen process + never-completed global space).

This single mechanism explains "orphaned chunks + saturated pool" in the current tree:
the world generation doesn't just slow down — it **halts at frame 4096**, and the pool locks
full of un-releasable processes.

## 5. Mechanism D (perf-work BUG): the per-process timeout is unit-mangled

`progress_timer__guard_restart__u16(timer, ticks_elapsed >> 4, false)` (line 194-197)
advances a **u16F4** timer (start `BIT(13)` = 8192 = 512.0 ticks) by `ticks_elapsed >> 4`,
where `ticks_elapsed` is the **frame counter** (see Mechanism C). The correct advance for a
u16F4 timer is `ticks_delta << 4`. As written, the timer decays at a rate proportional to
*game age*: a continuously-polled process times out after ≈ `8192·16/F` frames, where F is
the current frame — i.e. **~41 s at F=100, ~4 s at F=1000, ~1 s at F=4096** (then latched:
`progress_timer__guard_restart` with `is_restarting=false` sets `remaining = 0` permanently,
`timer.c:28-51`).

So in the second minute of a session, a chunk that enters `Awaiting_Neighbors` — the
*normal* state for an edge chunk (Mechanism A) — is failed by the timeout after ~1–4 s,
leaving a terrain-only, **slope-less** chunk. The overworld handler's timeout path carries an
unresolved `// TODO: ensure chunk does not get serialized.` (line 766) — a failed chunk is
still *active*, so when it is later dropped it goes through the **store** path and its
slope-less terrain is persisted (see Item 3). And critically: the timeout only advances while
the process is **polled** — once Mechanism C stops polling, no frozen process can ever time
out. The rescue mechanism is blind to the very processes it was added for.

## 6. Mechanism E (pre-existing, latent → live once C is fixed): drop-path UAF

`release_global_space` (`global_space_manager.c:76-110`, taken by the *inactive* drop branch
at lines 211-216) frees the chunk + collision node and then calls
`fail_process(p_global_space->p_generation_process)` — but `fail_process` only *marks* the
process; the actual release happens on a **future** poll of the process manager. In the
meantime `release_global_space_in__global_space_manager` re-initializes the global space
in place (`global_space_manager.c:112-131`). The generator process still holds
`p_process_data = <freed global space>`:

- Next poll: the handler dereferences the freed slot (lines 761-762).
- On release: the dispose handler writes `p_global_space->p_generation_process = 0`
  (`game_action__global_space__resolve.c:24-25`) into a slot that may now be **re-allocated to
  a different chunk** — corrupting the new global space's back-pointer, which its future
  `release_global_space` will then `fail_process` on a random process.

Today this UAF is masked by Mechanism C (frozen processes don't poll). **Any fix that
restores polling must also fix this**, or the drop path starts executing the dangling
dereference for real.

---

## 7. Pool-saturation summary

| Mechanism | Origin | Bounded? | Saturates 16384 pool? |
|---|---|---|---|
| A. Edge-of-volume Awaiting_Neighbors | pre-existing, by design | yes (deconstruction escape) | no (≤648 waiters) |
| B. Resolver ↔ overworld ping-pong (NULL neighbor chunk) | pre-existing | no (no timeout in resolver) | slowly, one zombie per stuck pair |
| C. 4096-frame cutoff freezes all non-criticals | **perf work** | no — permanent from t=128 s | **yes — locks the pool full of zombies** |
| D. u16F4 timeout unit-mangled (frame/16 advance) | **perf work** | n/a | no (releases slots) but fails healthy edge chunks early, persisting slope-less chunks |
| E. Drop-path deferred-fail UAF | pre-existing | masked by C; live once C is fixed | n/a (memory safety) |

## 8. Recommended fixes (for the implementation pass)

1. **Delete the `ticks_elapsed < 4096` gate.** It measures game age, not loop time. If a
   budget is wanted, accumulate a *local* u32F20 from `poll_elapsed_time__u32F20_of__game`
   (already reset by `reset__game_tick_timer` right before the poll, `game.c:745-748`) and
   compare against the tick quantum `BIT(20)`. Critical processes bypass the budget as today.
2. **Initialize `tick__timer_u32`** in `initialize_game` (or stop reading it for this purpose).
3. **Fix or remove the per-process u16F4 timer.** If kept: advance by
   `(ticks_delta << 4)` using a *per-process* delta (track last-advanced value in the
   process), not the cumulative frame counter. Then the 512-tick (16 s) intent holds.
   Also decide the slope-resolver policy: either enable its timeout too (with the
   serialize-safety TODO resolved) or document that resolver waiters are only released by
   deconstruction.
4. **Make the drop path release the generation process synchronously** —
   `release_process_from__process_manager` (it exists, `process_manager.c:84-105`) instead of
   the deferred `fail_process` — and guard the dispose handler against a released global space
   (verify the slot is still allocated and still references this process before writing
   `p_generation_process = 0`).
5. **Optional (bigger):** invert the neighbor protocol — a completing chunk notifies the
   (bounded) list of waiters instead of each waiter polling 8 dehashes per tick.

## 9. Suggested verification (when implementing)

- Log/counter: processes in `Awaiting_Neighbors` per tick; assert pool occupancy < 75%
  after 10 min of stationary play.
- Soak test: stand at a chunk-boundary edge for > 16 s and > 128 s; assert no
  `timeout` spam, no `allocate_process` failures, no zombie growth after frame 5000.
- GDB watchpoint on a dropped global space's slot to confirm no post-release access
  (Mechanism E) once polling is restored.
- Note: `process_manager.c:162` currently emits a `debug_info` line **every frame** —
  remove or gate it, or the log will drown any of the above.
