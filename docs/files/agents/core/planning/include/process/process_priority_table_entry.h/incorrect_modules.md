# Planning: process_priority_table_entry.h — Incorrect Modules

**Review source:** `agents/core/review/include/process/process_priority_table_entry.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/process/process_priority_table_entry.h`
- `core/source/process/process_priority_table_entry.c`
- `core/include/process/process_table.h`
- `core/source/process/process_table.c`
- `core/include/defines.h` (struct definitions for `Process_Priority_Table_Entry` and `Process_Table`)
- `tests/core/source/process/test_suite_process_process_priority_table_entry.c`
- `tests/core/source/process/test_suite_process_process_table.c`

---

## 1. Problem Identification

Two functions in `core/source/process/process_priority_table_entry.c` are flagged
**Incorrect**.

### 1.1 `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes`

Three distinct defects violate the function's `Postcondition` contract:

1. **Missing `Boundary Condition` guard — null-pointer dereference.** The function
   never calls `is_process_priority_table_entry__empty` before proceeding. When the
   entry is empty (`p_ptr_process__oldest_of__priority == 0` and
   `p_ptr_process__youngest_of__priority == 0`, as set by `initialize_process_table`'s
   `memset`), the comparison `oldest < youngest` evaluates to `0 < 0` (false) and
   `oldest == youngest` evaluates to `0 == 0` (true). The single-element branch then
   executes `*oldest = 0`, dereferencing a null `Process**`. Every sibling function
   (`move_up`, `move_down`, `poll_next`) guards with `is_process_priority_table_entry__empty`
   at entry; this function does not, violating the established `Invariant`.

2. **Wrong return value — `State Desync`.** In the single-element case
   (`oldest == youngest`), the entry is correctly cleared but the function returns
   `false`. The caller `remove_process_from__process_table` treats `false` as
   "process not found," logs a misleading `debug_error`, and returns early. This is a
   `Mode Confusion`: a successful removal is indistinguishable from a not-found result.

3. **Stale `current_priority_to__swap` — `Representation Invariant` violation.** The
   single-element branch clears `oldest` and `youngest` to null but leaves
   `p_ptr_process__current_priority_to__swap` pointing at the old (now-cleared) slot.
   All three pointer fields should be null when the entry is empty, per the
   `Representation Invariant` established by `initialize_process_table` (which
   `memset`s the entire table to zero).

### 1.2 `move_process_priorty_table_entry_up__one_in__ptr_array_of__processes`

**`Stub-real divergence` / `Surface-form leakage`.** The function's docstring states it
"will move the pointer delimiters of the entry up by one," and `add_process_to__process_table`
relies on it to shift **all** processes in the range `[youngest, oldest]` towards higher
indices, making room at the `youngest` position for a new process.

The two-line body:

```c
*++p_process_priority_table_entry->p_ptr_process__oldest_of__priority =
    *p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
*p_process_priority_table_entry->p_ptr_process__youngest_of__priority = 0;
```

only copies the `youngest` element to one-past-the-oldest and clears `youngest`.
Intermediate elements (`youngest+1` through `oldest-1`) are left in place.

For `[P1, P2, P3]` at indices `[youngest=2, oldest=4]`, the result is
`[NULL, P2, P3, P1]` at `[youngest=2, oldest=5]` instead of the correct
`[NULL, P1, P2, P3]` at `[youngest=2, oldest=5]`.

For single-element entries the behavior is coincidentally correct (no intermediates
to shift), which masks the bug in the existing test suite.

---

## 2. Impact Assessment

### 2.1 Callers of `move_up`

| Caller | File | How it relies on `move_up` |
|--------|------|---------------------------|
| `add_process_to__process_priorty_table_entry_in__ptr_array_of__processes` | `process_priority_table_entry.c` (~line 75) | Calls `move_up` then writes the new process at `youngest`. The bug **reorders** processes within a priority entry — the newest process ends up at the `oldest` end instead of the `youngest` end. |
| `add_process_to__process_table` | `process_table.c` (~line 59) | Calls `move_up` directly for every higher-priority (lower-index) entry before inserting a new process. The bug **scrambles** the `ptr_array_of__processes` layout for all priority levels above the insertion point, breaking the contiguity invariant that `add_process_to__process_table` depends on. |

### 2.2 Callers of `remove`

| Caller | File | How it relies on `remove` |
|--------|------|---------------------------|
| `remove_process_from__process_table` | `process_table.c` (~line 71) | Calls `remove` on the target priority entry, then runs a compaction loop calling `move_down` on all higher-priority entries to close the gap. The wrong `false` return in the single-element case causes the compaction loop to be **skipped entirely**, leaving a gap in `ptr_array_of__processes`. |

### 2.3 Data structures and downstream consumers

- **`ptr_array_of__processes`** (`Process_Table`): The `move_up` bug corrupts the
  relative ordering of processes within and across priority entries. `poll_next_p_process_from__process_table`
  iterates this array via `current_priority_to__swap`; scrambled ordering produces
  incorrect polling sequence.
- **`p_ptr_process__current_priority_to__swap`** (`Process_Priority_Table_Entry`): The
  `remove` bug leaves this pointer stale after emptying an entry. `poll_next_p_process_from__process_priority_table_entry`
  dereferences this pointer without an emptiness check on the cursor itself — it only
  checks `is_process_priority_table_entry__empty` (which tests `oldest`/`youngest`,
  not `current_priority_to__swap`). A stale cursor can therefore cause a null dereference
  or poll a freed slot.
- **`get_quantity_of__processes_in__process_priority_table_entry`**: Computed as
  `oldest - youngest`. After a buggy `move_up`, the range is correct in size but the
  contents are scrambled; the count itself is unaffected, which is why existing count-based
  tests pass despite the ordering bug.

### 2.4 De facto contracts coupled to the broken behavior

- `remove_process_from__process_table` has implicitly come to rely on `remove` returning
  `false` for the single-element case. The `debug_error` log and early return (skipping
  compaction) are a **de facto contract** built on top of the wrong return value. Fixing
  the return value to `true` will cause the compaction loop to execute for single-process
  removals, which it currently never does.
- `add_process_to__process_table`'s empty-entry path (`initialize_process_priority_table_entry`
  followed by `return true`) never stores the first process — a separate bug flagged in
  its own review. This masks the `move_up` bug for single-element entries (the shift is
  never exercised), which is why no existing test catches the reordering.

### 2.5 `move_down` consideration (not flagged, but coupled)

`move_process_priorty_table_entry_down__one_in__ptr_array_of__processes` is flagged
**Correct** in its review, described as the "proper inverse" of `move_up`. However, the
review describes both functions as single-element copy-and-clear operations, not full
shifts. Once `move_up` is corrected to perform a full shift, `move_down` must also
perform a full shift to remain a true inverse. Additionally, the actual `move_down`
code operates on `oldest_of__priority` (not `youngest_of__priority` as the review
describes), producing a self-assignment and clearing the wrong slot. This discrepancy
should be verified before or alongside the `move_up` fix, because the compaction loop in
`remove_process_from__process_table` depends on `move_down`.

---

## 3. Resolution Assessment

### 3.1 `remove_process_from__process_priority_table_entry_from__ptr_array_of__processes`

**What needs to change in the implementation:**

1. **Add `Boundary Condition` guard at entry.** Insert an
   `is_process_priority_table_entry__empty` check as the first statement, returning
   `false` (process not found in an empty entry). This matches the pattern used by all
   sibling functions and prevents the null-pointer dereference.

2. **Fix the return value in the single-element case.** Change `return false` to
   `return true` when the sole process is successfully removed.

3. **Clear `current_priority_to__swap`.** In the single-element branch, set
   `p_ptr_process__current_priority_to__swap = 0` alongside `oldest` and `youngest`
   to restore the `Representation Invariant` (all three pointers null when empty).

**Caller updates:**

- `remove_process_from__process_table`: The compaction loop will now execute after
  single-process removals. The `debug_error` message for "process not found" will no
  longer fire spuriously. The unchecked return value of `move_down` in the compaction
  loop should be considered for error propagation, though `move_down`'s review marks it
  Correct (see §2.5).

**Documentation/test updates:** None for this function's interface; the signature and
`Precondition`/`Postcondition` contracts already describe the correct behavior.

### 3.2 `move_process_priorty_table_entry_up__one_in__ptr_array_of__processes`

**What needs to change in the implementation:**

Replace the two-line copy-and-clear with a proper full-shift loop:

```c
for (Process **p = p_process_priority_table_entry->p_ptr_process__oldest_of__priority;
     p >= p_process_priority_table_entry->p_ptr_process__youngest_of__priority;
     p--) {
    *(p + 1) = *p;
}
*p_process_priority_table_entry->p_ptr_process__youngest_of__priority = 0;
p_process_priority_table_entry->p_ptr_process__oldest_of__priority++;
```

This iterates from `oldest` down to `youngest` (reverse order to avoid overwriting),
copies each element one slot higher, clears the vacated `youngest` position, and
increments `oldest`.

**Caller updates:** None required. `add_process_to__process_priorty_table_entry_in__ptr_array_of__processes`
and `add_process_to__process_table` already call `move_up` before writing the new process
at `youngest`; once the shift is correct, the insertion order will be correct.

**Pre-`Precondition`/`Postcondition`:** The existing emptiness check and bounds check
(`oldest + 1 > &ptr_array_of__processes[MAX-1]`) remain valid and must be preserved.

### 3.3 `move_down` (consideration, not in scope but coupled)

If `move_up` is corrected to a full shift, `move_down` should be corrected to a
symmetric full shift (iterate from `youngest` to `oldest`, copy each element one slot
lower, clear the vacated `oldest` position, decrement `youngest`). The current code
operates on the wrong pointer field. This should be addressed as part of the same change
set, since `remove_process_from__process_table`'s compaction loop depends on it.

---

## 4. Test Verification Checklist

### 4.1 Existing tests — impact analysis

**`tests/core/source/process/test_suite_process_process_priority_table_entry.c`:**

| Test | Affected by fix? | Notes |
|------|-----------------|-------|
| `remove_process__decreases_count` | No | Uses 2 processes; exercises the multi-element remove path (already returns `true`). Should continue to pass. |
| `poll_next__returns_process_from_entry` | No | Does not call `remove` or `move_up` directly. |
| `poll_next__wraps_around_single_process` | No | Does not call `remove` or `move_up`. |
| `poll_next__empty_entry_returns_true_immediately` | No | Tests `poll_next` on an empty entry, not `remove`. |
| `add_process__increases_count` | Indirectly | Depends on `add_process_to__process_table`'s empty-entry path (separate bug). The `move_up` fix does not affect this test. |

**`tests/core/source/process/test_suite_process_process_table.c`:**

| Test | Affected by fix? | Notes |
|------|-----------------|-------|
| `remove_process__decrements_count` | **Yes** | Single-process removal. Currently passes despite the `false` return (entry is cleared, count is 0). After fix, `remove` returns `true`, compaction loop runs (no higher-priority entries to shift). Should continue to pass. |
| `add_remove_add__count_is_correct` | Indirectly | Affected by the separate `add_process_to__process_table` empty-entry bug (first process not stored). Out of scope. |
| `remove_from_different_priority__maintains_other_priorities` | **Yes** | Removes a process from priority 1; compaction loop shifts priorities 2–3 (empty). After fix, `remove` returns `true` instead of `false` for single-process entries, so compaction runs correctly. Should pass. |

### 4.2 New tests needed

| Test | Technique | Rationale |
|------|-----------|-----------|
| `remove__empty_entry_returns_false_without_crash` | **`Boundary Condition`** / **`Fuzzing`** | Verify the new `is_process_priority_table_entry__empty` guard prevents null dereference. |
| `remove__single_process_returns_true` | **`Property Based Testing`** | Verify the corrected return value (`true`) for the single-element case. |
| `remove__clears_current_priority_to__swap` | **`Property Based Testing`** | Verify all three pointers are null after emptying an entry (`Representation Invariant`). |
| `move_up__preserves_order_multi_element` | **`Property Based Testing`** / **`Equivalence Check`** | Insert 3+ processes, call `move_up`, verify `[P1, P2, P3]` shifts to `[NULL, P1, P2, P3]` (not `[NULL, P2, P3, P1]`). |
| `add_process__preserves_insertion_order` | **`Round Trip Check`** | Add processes one at a time, poll them, verify FIFO order within a priority level. |
| `add_then_remove_then_add__compaction` | **`Round Trip Check`** | Add process, remove it, add another; verify the table remains contiguous and count is correct. |
| `move_up__boundary_at_array_end` | **`Boundary Condition`** | Fill the array to `PROCESS_MAX_QUANTITY_OF - 1` and verify `move_up` returns `false` (bounds check). |

### 4.3 Test impact summary

- **Blast radius:** **Medium**. No existing assertions are invalidated by the fixes
  (the fixes make behavior match the documented contracts). New tests are required to
  cover the edge cases that were previously untested or masked by the `add` bug.
- **Phased approach:** Not required. Both fixes are localized to
  `process_priority_table_entry.c`. The `move_down` fix (if pursued) should be
  implemented in the same change set to maintain the up/down symmetry.

---

## 5. Blast Radius Summary

- **Files requiring changes:** 1 source file — `core/source/process/process_priority_table_entry.c`.
  Optionally 1 additional file — `core/source/process/process_table.c` (if the compaction
  loop's unchecked `move_down` return value is addressed, and if the spurious `debug_error`
  in `remove_process_from__process_table` is cleaned up).
- **Behavior-preserving for current callers:** **No.** The fixes change observable
  behavior: process ordering within priority entries changes (correct order), `remove`
  returns `true` for single-process removals (enabling compaction), and the null-dereference
  crash is eliminated. Any code that has come to rely on the scrambled ordering or the
  spurious `false` return is coupled to the broken behavior (`Coupled`).
- **Phased approach:** Not required. Both fixes are in a single translation unit.
  However, the `move_down` correction (§3.3) should be co-developed with the `move_up`
  fix to preserve the `Duality` between the two operations.
- **De facto contracts invalidated:**
  1. `remove_process_from__process_table`'s assumption that `remove` returns `false`
     for single-process removals (the compaction loop will now run).
  2. Any polling-order assumptions based on the scrambled process layout produced by
     the buggy `move_up`.
- **Test files requiring changes:** `test_suite_process_process_priority_table_entry.c`
  and `test_suite_process_process_table.c` — add new test cases per §4.2.
