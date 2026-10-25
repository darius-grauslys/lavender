# Planning: process_table.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/process_table.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/process_table.h`
- `core/source/process/process_table.c`
- `core/include/process/process_priority_table_entry.h`
- `core/source/process/process_priority_table_entry.c`
- `core/source/process/process_manager.c` (sole production caller)
- `tests/core/source/process/test_suite_process_process_table.c`
- `tests/core/source/process/test_suite_process_process_priority_table_entry.c`

---

## 1. Problem Identification

Four functions of the Process_Table were flagged **Incorrect**. All four violate the
module's central **Representation Invariant**: *priority entries are contiguous in
`ptr_array_of__processes`, and an entry's `oldest/youngest/swap` pointers always
address slots that actually hold the processes they delimit.*

### 1.1 `add_process_to__process_table` (process_table.c, ~L50–103)
- **Postcondition violation (lost process):** In the empty-entry path, the function
  calls `initialize_process_priority_table_entry` (which sets `oldest == youngest ==
  swap` to the target slot) and then returns `true` **without ever writing
  `p_process` into that slot**. The entry reads as non-empty (pointers non-null) but
  holds no process — a **State Desync** between the entry's pointers and the array.
  `get_quantity_of__processes_in__process_table` computes `oldest - youngest`, which
  is 0 for such an entry, so the table silently loses the process while reporting
  success.
- **Dead code:** The `if (!p_process_priority_table_entry)` null check after
  `get_p_process_priority_table_entry_by__priority` can never fire (that helper never
  returns NULL).
- **Coupled defect:** The insertion point depends on
  `get_lowest_used_p_process_priorty_table_entry`, which is itself broken (§1.2), so
  even a stored process may be placed at the wrong slot when only priority level 0 is
  used beneath it.

### 1.2 `get_lowest_used_p_process_priorty_table_entry` (process_table.c, L17–38)
- **Boundary Condition / off-by-one:** The loop condition `priority_level > 0` on an
  unsigned (`Index__u32`) counter **skips priority level 0 entirely**. When the only
  used entry beneath the new process's priority is level 0, the function returns NULL
  and `add_process_to__process_table` falls back to `ptr_array_of__processes[0]`,
  placing the new process over/adjacent to existing priority-0 processes.
- **Minor:** implicit narrowing of `Index__u32` into the helper's `uint8_t` priority
  parameter; no null validation of `p_process_table`.

### 1.3 `remove_process_from__process_table` (process_table.c, L105–133)
- **Non-Injective Translation / Mode Confusion in the callee:**
  `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes`
  returns `false` for two distinct outcomes: (a) process genuinely not found, and
  (b) the entry held exactly one process, which **was** successfully cleared. The
  table function treats both as "not found", logs a spurious `debug_error`, and
  returns early — **skipping the compaction loop**. A gap is left in
  `ptr_array_of__processes`, breaking the contiguity **Invariant** that add/shift
  rely on.
- **Callee defects (prerequisite fixes):** no `is_process_priority_table_entry__empty`
  guard (NULL dereference / UB on an already-empty entry — the guard every sibling
  function has, a **DRY** violation); the single-element branch does not verify
  `*oldest == p_process` before clearing; `p_ptr_process__current_priority_to__swap`
  is left stale after clearing (State Desync).

### 1.4 `poll_next_p_process_from__process_table` (process_table.c, L141–161)
- **Non-Injective Translation / Mode Confusion:** The callee
  `poll_next_p_process_from__process_priority_table_entry` collapses three outcomes —
  *entry empty* (returns false, writes nothing), *polled, entry continues* (returns
  false, writes process), *polled, entry exhausted* (returns true, writes process) —
  into one `bool`. The main loop cannot distinguish them:
  - Current entry empty → callee returns false → loop `break`s and returns a NULL
    (first call) or **stale** `p_process`, skipping all lower-priority entries that
    do hold processes.
  - Current entry exhausted followed by a non-empty entry → loop advances and
    `continue`s; the next poll **overwrites** `p_process`, silently losing the last
    process of the previous entry (a Lost Update of scheduling work).
- **Code smell:** the loop variable `process_priority` is never used inside the body;
  iteration rides entirely on `p_process_priority_table_entry__current`.

---

## 2. Impact Assessment

### Producers/consumers coupled to the broken behavior

| Consumer | Coupling | Effect of correction |
|---|---|---|
| `process_manager.c` — enqueue path (`add_process_to__process_table`, L79) | Relies on add to register processes for scheduling | Today, a first insert into an empty priority level is **lost** — the process never runs. Fixing add changes runtime scheduling behavior (processes that previously vanished will now execute). No signature change. |
| `process_manager.c` — release path (`remove_process_from__process_table`, L71) | Relies on removal to deregister + compact | Today, single-process removal skips compaction, leaving a gap. Any layout that accumulated gaps is a de facto state the rest of the table (shifts in add, poll's pointer walking) has been operating around. After the fix, tables are re-compacted; any code implicitly tolerating gaps is invalidated. No such tolerance was found in `./include`/`./source`, but the runtime layout changes. |
| `process_manager.c` — `poll_process_manager` (L153–175) | `while ((p_process = poll_next...) && ...)` loop assumes: each process returned exactly once, NULL iff table exhausted | Today the loop can receive a stale/duplicate process (re-execution) or NULL while processes remain (skipped work). After the fix the loop contract holds; no caller change needed. |
| `get_quantity_of__processes_in__process_table` (process_table.c, L163–177) | Computes `oldest - youngest` per entry — correct only if the **Representation Invariant** holds | Under the add bug it undercounts (0 for a "non-empty" empty-slotted entry); after the fix it becomes accurate. Its results feed `process_manager` bookkeeping. |
| `move_process_priorty_table_entry_up/down__one_in__ptr_array_of__processes` (process_priority_table_entry.c) | Precondition: entries contiguous, higher-priority moved first/after | Gaps from the remove bug invalidate their pointer arithmetic assumptions; fixing remove restores their Precondition. |
| `initialize_process_table` / `begin_polling_of__process_table` | Zero-init sets all entry pointers to 0; `current` to entry 0 | The empty **Sentinel** (all-zero entry) and the wrap **Sentinel** at index `PROCESS_MAX_PRIORITY_LEVEL` (the table is declared `[PROCESS_MAX_PRIORITY_LEVEL + 1]`) remain the emptiness/end markers. The poll fix must preserve both sentinel semantics. |

### Assumptions invalidated by the fixes
- Any de facto reliance on "first insert into an empty priority level returns true but
  stores nothing" is invalidated (none found; tests assert the opposite).
- Any de facto reliance on post-removal gaps in `ptr_array_of__processes` is
  invalidated (none found in `./include`/`./source`).
- **Latent hazard, out of scope but noted:** `get_p_process_priority_table_entry_by__priority`
  maps out-of-range priorities to entry 0 (`Aliasing Bug`) — the add-path null check
  being removed was dead *because of* this; the fix must not depend on that check for
  safety. Tracked separately in its own review file.

---

## 3. Resolution Assessment

No header signature changes are required; all fixes are internal to two `.c` files.
A phased approach is recommended (each phase independently testable).

### Phase 1 — `get_lowest_used_p_process_priorty_table_entry` + `add_process_to__process_table`
1. **Restructure the search loop** to include priority level 0 without unsigned
   underflow, e.g. a counting loop:
   ```c
   for (Index__u32 i = 0; i < priority_levels_beneath__this_one; i++) {
       uint8_t priority_level = (uint8_t)(priority_levels_beneath__this_one - 1 - i);
       ...
   }
   ```
   This also fixes the `Index__u32` → `uint8_t` narrowing. Optionally make the
   function `static` (it has no header declaration and one caller).
2. **Store the process in the empty-entry path** of `add_process_to__process_table`:
   after `initialize_process_priority_table_entry(...)`, write
   `*p_process_priority_table_entry->p_ptr_process__youngest_of__priority = p_process;`
   (oldest == youngest there). Restores the Postcondition "on success, the process is
   stored".
3. **Delete the dead null check** (`if (!p_process_priority_table_entry)`).
4. Callers: none need updating (signatures unchanged). `process_manager.c` enqueue
   simply starts working as specified.

### Phase 2 — remove path (helper first, then table function)
1. In `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes`
   (`core/source/process/process_priority_table_entry.c`):
   - Add the `is_process_priority_table_entry__empty` guard at entry (returns false;
     matches every sibling — removes the NULL-deref UB, restores **DRY**).
   - Single-element branch: verify `*oldest == p_process` before clearing; return
     **true** on success; also clear `p_ptr_process__current_priority_to__swap` to 0
     (removes stale-pointer State Desync). This makes the return value an Injective
     mapping of outcomes (found / not found).
2. In `remove_process_from__process_table`: no structural change required once the
   helper is correct — the compaction loop will now execute after a successful
   single-process removal, restoring contiguity. Optionally pre-check entry emptiness
   before calling the helper.
3. Callers: `process_manager.c` release path unchanged; the spurious `debug_error` on
   successful single removals stops firing.

### Phase 3 — `poll_next_p_process_from__process_table`
1. Keep the callee's contract (bool = "entry exhausted after this poll") but make the
   table function distinguish *empty* from *continuing* explicitly:
   ```c
   Process *p_process = 0;
   for (;;) {
       Process_Priority_Table_Entry *entry = p_process_table->p_process_priority_table_entry__current;
       if (entry >= &p_process_table->process_priority_table[PROCESS_MAX_PRIORITY_LEVEL])
           return 0;                                    /* Sentinel: all polled */
       if (is_process_priority_table_entry__empty(entry)) {
           ++p_process_table->p_process_priority_table_entry__current;   /* skip empty */
           continue;
       }
       bool entry_exhausted = poll_next_p_process_from__process_priority_table_entry(entry, &p_process);
       if (entry_exhausted)
           ++p_process_table->p_process_priority_table_entry__current;   /* advance, keep p_process */
       return p_process;                                   /* never return stale value */
   }
   ```
   (Advance past the last real entry lands on the `+1` Sentinel; the next call returns
   NULL, preserving the documented wrap-around Postcondition.)
2. Remove the unused `process_priority` loop variable.
3. Callers: `poll_process_manager` unchanged; its `while ((p = poll(...)) && ...)`
   loop now sees a faithful stream (each process once, NULL at exhaustion).

### Documentation / spec
- Update `docs/specs/core/process/process_table.h.spec.md` (referenced by the test
  suite) if it encodes the broken behaviors; align spec Postconditions with the fixed
  implementations (Contract-First).

---

## 4. Test Verification Checklist

Existing suite: `tests/core/source/process/test_suite_process_process_table.c` and
`test_suite_process_process_priority_table_entry.c`.

**Current assertions (pre-flag, assert *correct* behavior — several must be failing
today and will pass after the fix):**
- `add_process__increments_count`, `add_multiple__increments_count`,
  `add_mixed_priorities` — assert count reflects stored processes; currently defeated
  by the lost-process bug for first inserts into empty priorities. **Not invalidated**
  by the fix; they become green.
- `add_then_remove__decrements_count`, `remove_middle__...` — count-based; pass both
  before and after (count is pointer-arithmetic based), so they do **not** detect the
  compaction gap. New explicit assertions needed (below).
- Poll tests (`poll_returns_process`, `poll_exhausted__returns_null`,
  `poll_priority_order`, multi-process sequences) — assert correct ordering and NULL
  termination; some (priority-order across a skipped empty level) currently fail and
  will pass after Phase 3.

**New tests required:**
- **Boundary Condition (Phase 1):** table whose only used entry is priority level 0,
  then add a higher-priority process — assert correct slot placement (exercises the
  fixed `get_lowest_used`); add into an empty priority level — assert the slot actually
  holds the process (`*entry->p_ptr_process__youngest_of__priority == p_process`).
- **Round Trip Check (Phase 2):** add N processes across priorities, remove each,
  assert count returns to 0 *and* `ptr_array_of__processes` is fully zeroed (no gaps);
  single-process-per-priority removal specifically (the false-return regression).
- **Equivalence / sequence Check (Phase 3):** poll a table with an empty priority level
  between two used levels — assert all processes returned exactly once, then NULL;
  assert no process is returned twice and no stale pointer after an entry is emptied by
  removal mid-poll.
- **Property Based Testing:** for random add/remove/poll workloads, verify invariants
  after every op: contiguity of non-empty entries in `ptr_array_of__processes`,
  `oldest >= youngest` per entry, sum of per-entry quantities ==
  `get_quantity_of__processes_in__process_table`, and Conservation Law (count == live
  processes added − removed).
- **Fuzzing:** random priority values including the out-of-range boundary (level ≥
  `PROCESS_MAX_PRIORITY_LEVEL`) to confirm no out-of-bounds access once the dead null
  check is removed.

**Test blast radius: Medium.** No existing assertion encodes a broken behavior, so no
test needs weakening; work is additive plus turning currently-red tests green. Phase
with the implementation (Phase 1/2/3 test batches).

---

## 5. Blast Radius Summary

- **Files changed:** 2 — `core/source/process/process_table.c` (3 functions) and
  `core/source/process/process_priority_table_entry.c` (1 helper). No `.h` signature
  changes.
- **Behavior-preserving for current callers?** No — intentionally not. Callers in
  `process_manager.c` are unchanged but observe corrected behavior: lost processes now
  run, tables stay compact, polling returns a faithful stream. This is the intended
  contract, not a regression.
- **De facto contracts invalidated:** (a) success-without-storage on first insert into
  an empty priority level; (b) gaps persisting after single-process removal; (c)
  stale/early-NULL poll returns. No code in `./include` or `./source` was found to
  depend on any of these.
- **Phased approach:** Yes — three phases as above, each independently verifiable by
  its test batch; Phase 2 requires the helper fix before the table function benefits.
- **Residual risk / out of scope:** the out-of-range→entry-0 aliasing in
  `get_p_process_priority_table_entry_by__priority` (separate review file); consider a
  range-clamping Precondition guard on `process_priority__u8` in a follow-up so the
  removed dead null check is not load-bearing.
