# Planning: sort_list.h — Incorrect Modules

**Review source:** `agents/core/review/include/sort/sort_list/sort_list.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/sort/sort_list/sort_list.h` (declares 9 functions; hosts `static inline run_sort__once`)
- `core/source/sort/sort_list/sort_list.c` (implements the non-inline functions)
- `core/include/sort/sort_list/sort_node.h`, `core/source/sort/sort_list/sort_node.c` (node helpers)
- `core/include/defines.h` (`Sort_Node_t`, `Sort_List_t`, `Sort_Data_t`)
- `core/source/sort/sort_list/heap_sort.c`, `core/source/sort/sort_list/sort_list_manager.c` (consumers)
- `tests/core/source/sort/sort_list/test_suite_sort_sort_list_sort_list.c`

---

## 1. Problem Identification

Nine functions were flagged **Incorrect**. They cluster into one root cause plus a set of
independent defects.

### Root cause — `get_p_sort_node_by__index_from__sort_list` (Mode Confusion / State Desync)
The accessor returns `0` when a node's `is_allocated` bit is false, in addition to its
bounds check. But the sort list's **within-list occupancy** model is `p_node_data == NULL`,
not `is_allocated`. `Sort_Node.is_allocated` is *pool-membership metadata* owned by
`Sort_List_Manager`; the list itself never sets it to `false` (`set_sort_node_as__deallocated`
is never called from list code). The accessor therefore conflates two distinct concepts — a
**Mode Confusion** — and hands `NULL` to callers for perfectly valid in-range, currently-empty
nodes. Every caller below that dereferences the result inherits a latent null-dereference UB.

### Per-function defects
- **`get_p_sort_node_by__index_from__sort_list`** — the conflated `is_allocated` check makes
  it non-total over in-range indices; Postcondition "returns pointer to node" is violated for
  empty nodes. Should be a pure, bounds-checked accessor.
- **`initialize_sort_list_as__allocated`** — (a) iterates via the broken accessor, so a node
  with `is_allocated == false` yields `NULL`, and `initialize_sort_node_as__empty(NULL)` is a
  null-deref; (b) leaves `m_sort` and `sort_data` stale — an incomplete Lavender-style reset
  (violates the intended **Representation Invariant** of "reset to initial conditions").
- **`point_sort_list__sort_nodes_to__this_range`** — dereferences the accessor result on the
  first unallocated node → null-deref; fails its "point the *entire* list" Postcondition.
- **`insert_into__sort_list`** — writes `p_node_data` via direct array access but never sets
  `is_allocated`; under the accessor's model the inserted node is invisible (State Desync).
  Also omits the debug null-check on `p_sort_list` that every sibling has.
- **`remove_from__sort_list`** — dereferences the accessor result without a null check →
  null-deref on any empty node; also never clears `is_allocated` on removal (inconsistent
  reset).
- **`append_into__sort_list`** — the binary search terminates on `p_current->p_node_data &&
  !p_next->p_node_data`, a *local* occupied→empty transition, not "first empty slot"; for a
  mostly-full list it resolves to an **occupied** slot and silently overwrites data (data loss).
  It also dereferences the accessor result (`p_current`/`p_next`) with no null guard.
- **`get_index_of__sort_node_in__sort_list`** — debug error paths `return true;` from a
  `uint16_t` function (implicit `1`, not the `INDEX__UNKNOWN__SORT_NODE` **Sentinel**); and it
  performs `p_sort_node - p_sort_list->p_node_list` without validating that `p_node_list` is
  non-null (UB for an empty-initialized list).
- **`initialize_sort_list_as__empty`** — resets only 4 of 7 fields; leaves `m_sort`,
  `p_sort_list__next`, and `sort_data` stale (incomplete reset). Inconsistent with
  `initialize_sort_list_as__allocated`, which does clear `p_sort_list__next`.
- **`run_sort__once`** (`static inline` in the `.h`) — calls `p_sort_list->m_sort(p_sort_list);`
  without `return`; falls off a `bool` function → indeterminate return (UB). Violates the
  Postcondition "return whether fully sorted."

---

## 2. Impact Assessment

**Who relies on the broken behavior, and what a fix invalidates:**

- **`heap_sort.c` (primary consumer of the accessor).** It calls
  `get_p_sort_node_by__index_from__sort_list` at 9 sites (left/right child accessors,
  `rotate_heap`, both `sift_down_in__heap` calls, root/leaf swaps, and
  `update_heap_sort_node__index_for__next_node`) and **dereferences every result without a null
  check**. Today it only works because the *manager* sets `is_allocated = true` on nodes it
  hands out — a **de facto contract** coupling heap correctness to the pool flag, not to real
  occupancy. Making the accessor a pure bounds accessor (the recommended fix) makes these call
  sites correct for *both* manager-allocated and caller-provided lists; no heap edit is strictly
  required, but heap silently depends on the broken flag being `true`.

- **`sort_list_manager.c` (owner of `is_allocated`).** It uses `is_allocated` as **pool
  membership**: `allocate_sort_nodes_in__sort_list_manager` sets it `true`; the release path
  (`release_sort_nodes_in__sort_list_manager`, line 185) has an **adjacent bug** — it calls
  `set_sort_node_as__allocated` instead of `set_sort_node_as__deallocated`, so released nodes
  keep `is_allocated == true`. That bug currently *masks* the accessor null-derefs in the common
  flow (released nodes still read as "allocated"). Under the resolution, `is_allocated` remains
  legitimate pool metadata (SSOT for pool membership); the release bug should be corrected to
  `set_sort_node_as__deallocated` so released nodes are correctly marked free. This is outside
  the nine flagged functions but is a coupled assumption being normalized.

- **Occupancy SSOT.** The codebase already uses `p_node_data == NULL` as the real occupancy
  signal (`insert`, `remove`, and `append` all branch on `p_node_data`). The accessor is the
  single outlier. Correcting it removes a **Non-Injective / dual-source** inconsistency: today
  two fields encode one fact. After the fix, `p_node_data` is the **Single Source of Truth (SSOT)**
  for within-list occupancy and `is_allocated` is pool-only — callers that already check
  `p_node_data` need no change.

- **Tests.** `test_suite_sort_sort_list_sort_list.c` builds stack arrays, prepares them with
  `initialize_sort_node_as__empty` (which leaves `is_allocated` indeterminate), then calls the
  flagged functions: `get_node_by_index` asserts a non-null pointer, and `point_nodes_to_range`
  dereferences each node. These **assert correct behavior** and currently flake/crash whenever
  stack garbage makes `is_allocated == false`. The accessor fix turns them into deterministic
  passes; the incomplete-reset fixes make `initialize_as_empty`/`_as_allocated` assertions stable.

- **`run_sort__once` consumers.** `static inline`, so every TU including `sort_list.h` that calls
  it currently receives an indeterminate value. Correcting it to `return p_sort_list->m_sort(...)`
  is purely corrective (callers ignoring the return are unaffected; callers reading it stop getting
  garbage). Note `run_sort_with__this_many_steps` already captures `m_sort`'s return directly and is
  *not* affected.

**De facto contracts invalidated:** (1) heap correctness via the pool flag → normalized to real
occupancy; (2) "released nodes still read as allocated" (manager release bug) → corrected.

---

## 3. Resolution Assessment

**Strategy — establish one SSOT for occupancy:** `p_node_data` = within-list occupancy;
`is_allocated` = pool membership (manager-owned). The pivotal change is making the accessor a
pure bounds-checked lookup; everything else follows.

Per function:

1. **`get_p_sort_node_by__index_from__sort_list`** — drop the `is_sort_node__allocated` branch;
   return `&p_sort_list->p_node_list[index]` after the bounds check (return `0` only when
   out-of-range). Occupancy is the caller's concern. *Callers:* heap/append/remove/point need no
   signature change but become safe. This unblocks all null-derefs.
2. **`initialize_sort_list_as__allocated`** — iterate via direct array access
   (`p_sort_list->p_node_list[i]`) rather than the accessor; additionally reset `m_sort = 0`,
   zero `sort_data`, and keep the existing field writes. Add debug null-checks on `p_sort_list`
   and `p_node_list` (consistency with siblings). *Callers:* none; *docs:* none.
3. **`point_sort_list__sort_nodes_to__this_range`** — replace the accessor call with direct array
   access `p_sort_list->p_node_list[i].p_node_data = ...`; keep the stride walk and loop bound.
4. **`insert_into__sort_list`** — keep the `p_node_data` write (correct under the new SSOT); add
   the missing debug null-check on `p_sort_list`. No occupancy-flag change required for list
   semantics.
5. **`remove_from__sort_list`** — use direct array access in the linear scan (no null-deref);
   clear `p_node_data = 0` on match (occupancy SSOT). Optionally document `p_data == NULL` as a
   no-op / add a debug guard so it cannot match empty slots.
6. **`append_into__sort_list`** — fix the search to find the *first empty* slot: loop while
   `pivot_left < pivot_right` (narrow the range), not on a local occupied→empty transition; use
   direct array access for `p_current`/`p_next`; add a full-list guard so an append to a full list
   is a defined no-op rather than silent overwrite.
7. **`get_index_of__sort_node_in__sort_list`** — return the `INDEX__UNKNOWN__SORT_NODE` Sentinel
   (not `true`) on both debug error paths; add a null validation of `p_sort_list->p_node_list`
   before the pointer subtraction (guard the empty-list UB).
8. **`initialize_sort_list_as__empty`** — reset all seven fields: add `m_sort = 0`,
   `p_sort_list__next = 0`, and zero `sort_data`; keep `p_node_list = 0`, `f_sort_heuristic = 0`,
   `size_of__p_node_list = 0`, `is_allocated = false`. Symmetric with `_as_allocated`.
9. **`run_sort__once`** (in `.h`) — change the last line to
   `return p_sort_list->m_sort(p_sort_list);`.

**Phased approach (recommended, given blast radius):**
- **Phase 1 (pivotal):** fix `get_p_sort_node_by__index_from__sort_list` (item 1). Eliminates every
  null-deref and stabilizes heap + the flaky tests.
- **Phase 2:** complete the two init resets (items 2, 8) and add debug validation (items 4, 7).
- **Phase 3:** direct-array access in `point`/`remove` (items 3, 5) and the `append` search + full
  guard (item 6).
- **Phase 4:** one-line `run_sort__once` return (item 9); adjacent manager release-flag fix.

---

## 4. Test Verification Checklist

- **Existing tests (`test_suite_sort_sort_list_sort_list.c`)** assert *correct* behavior and are
  currently flaky/crashing on the null-deref:
  - `sort_list__get_node_by_index` asserts `get_p_sort_node_by__index(...) == &nodes[i]`; with the
    accessor's `is_allocated` check it returns `NULL` whenever stack garbage makes the bit clear →
    **fix makes it pass deterministically** (Phase 1).
  - `sort_list__point_nodes_to_range` dereferences each node via the broken path → **crashes** today;
    passes after Phase 3.
  - `sort_list__initialize_as_empty` / `_as_allocated` are stable but do not yet cover the newly-reset
    `m_sort` / `sort_data` / `p_sort_list__next` fields.
- **New tests needed:**
  - **Property Based Testing** for the accessor: for all in-range indices of an allocated list, the
    returned pointer equals `&p_node_list[i]` regardless of node occupancy (invariant: bounds-only).
  - **Round Trip Check** for insert/remove: `insert(list, p, i)` then `remove(list, p)` leaves node
    `i` empty and all others unchanged; `get_index_of` round-trips a node back to its index.
  - **Equivalence Check** for `append`: appending to a partially-filled list places the element at
    the first empty slot and never overwrites an occupied slot (regression for the binary-search bug);
    verify against a linear reference model.
  - **Fuzzing** on `append_into__sort_list` occupancy patterns (0..N filled, gaps) to catch residual
    boundary/data-loss cases; and boundary cases for `get_index_of` (node == one-past-end → Sentinel,
    `p_node_list == NULL` → no UB).
  - **Mutation Testing** on the accessor to confirm the suite detects reintroduction of the
    `is_allocated` branch.
- **Blast radius (test impact): Medium.** Existing assertions are preserved (they target correct
  behavior); a handful of new cases are added. No phased test migration is required beyond landing
  them alongside Phases 1 and 3.

---

## 5. Blast Radius Summary

- **Files changed:** `core/source/sort/sort_list/sort_list.c` (accessor, both inits, point, insert,
  remove, append, get_index), `core/include/sort/sort_list/sort_list.h` (`run_sort__once`), and — as an
  adjacent coupled fix — `core/source/sort/sort_list/sort_list_manager.c` (release flag). **~3 files.**
- **Behavior-preserving for current callers?** For the dominant manager-allocated flow, behavior is
  preserved (and made well-defined). For caller-provided pre-allocated arrays — the documented
  contract — the fix *removes UB* rather than changing observable correct output. Net: corrective, not
  regressive.
- **Phased approach:** Yes — Phase 1 (accessor) is the unblocking change; Phases 2–4 layer resets,
  search correctness, and the trivial `return`.
- **De facto contracts invalidated:** heap's reliance on the pool flag as an occupancy proxy, and the
  "released nodes read as allocated" manager bug. Both are normalized to a single, explicit SSOT.
