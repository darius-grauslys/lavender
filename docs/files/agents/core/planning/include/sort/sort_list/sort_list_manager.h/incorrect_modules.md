# Planning: Incorrect Modules in `sort_list_manager`

## Overview

Four functions/modules in the `Sort_List_Manager` subsystem are flagged
**Incorrect**. Two are **Pure** inline query helpers in
`core/include/sort/sort_list/sort_list_manager.h` that contain a
**transposition** of allocated-resource counters. Two are in
`core/source/sort/sort_list/sort_list_manager.c` — one depends on the
broken helpers, one contains an arithmetic sign error and delegates to
a callee with three additional defects. Together these violate the
**Representation Invariant** that the manager's two bookkeeping counters
(`quantity_of__allocated_sort_lists` and `quantity_of__allocated_sort_nodes`)
always reflect the true allocation state of the pools.

---

## 1. Problem Identification

### 1a. `get_quantity_of__available_sort_lists_in__sort_list_manager`
*(inline, `core/include/sort/sort_list/sort_list_manager.h`)*

**Defect**: The function calls
`get_quantity_of__allocated_sort_nodes_in__sort_list_manager()` (returns the
allocated-**node** count) when it should call
`get_quantity_of__allocated_sort_lists_in__sort_list_manager()` (returns the
allocated-**list** count). It computes:

```
SORT_LIST__MAXIMUM_QUANTITY_OF (64) - allocated_nodes
```

instead of the intended:

```
SORT_LIST__MAXIMUM_QUANTITY_OF (64) - allocated_lists
```

Since `allocated_nodes` can reach 512, the unsigned subtraction **underflows**
(**Boundary Condition** violation), wrapping to a very large value. The
result is a **Non-Injective Translation** of the true available-list count.

### 1b. `get_quantity_of__available_sort_nodes_in__sort_list_manager`
*(inline, `core/include/sort/sort_list/sort_list_manager.h`)*

**Defect**: The function calls
`get_quantity_of__allocated_sort_lists_in__sort_list_manager()` (returns the
allocated-**list** count) when it should call
`get_quantity_of__allocated_sort_nodes_in__sort_list_manager()` (returns the
allocated-**node** count). It computes:

```
SORT_NODE__MAXIMUM_QUANTITY_OF (512) - allocated_lists
```

instead of the intended:

```
SORT_NODE__MAXIMUM_QUANTITY_OF (512) - allocated_nodes
```

Functions 1a and 1b have their subtract terms **swapped** — a
**transposition** defect. Both are otherwise **Pure** and
**Referentially Transparent** accessors; the defect is purely semantic
(aliasing the wrong counter).

### 1c. `allocate_sort_list_in__sort_list_manager`
*(implementation, `core/source/sort/sort_list/sort_list_manager.c`)*

**Defect**: The function's own logic is sound, but it is **Coupled** to the
two broken helpers above. Its two **Precondition** guards are invalidated:

1. The "no available sort list entries" guard
   (`if (!get_quantity_of__available_sort_lists_in__sort_list_manager(...))`)
   computes `64 - allocated_nodes`. When `allocated_nodes > 64`, this
   underflows to a large non-zero value, so the guard **always passes** —
   the pool-exhaustion check is defeated.

2. The "node size exceeds available" guard
   (`if (quantity_of__remaining_nodes < quantity_of__nodes)`) computes
   `512 - allocated_lists`. Since `allocated_lists` maxes at 64, this
   grossly **overestimates** available nodes, potentially permitting
   allocations that exceed the true remaining node capacity.

### 1d. `release_sort_list_in__sort_list_manager`
*(implementation, `core/source/sort/sort_list/sort_list_manager.c`)*

**Defect A (arithmetic sign error)**: The function increments
`quantity_of__allocated_sort_nodes` using `+=` when it must **decrement**
using `-=`. Releasing a sort list returns nodes to the pool, so the
**Conservation Law** is violated: the counter diverges from the actual
allocation state (**State Desync**).

**Defect B (three bugs in the callee
`release_sort_nodes_in__sort_list_manager`)**:

| # | Bug | Current | Correct |
|---|-----|---------|---------|
| B1 | Loop bound constant | `SORT_LIST__MAXIMUM_QUANTITY_OF` (64) | `SORT_NODE__MAXIMUM_QUANTITY_OF` (512) |
| B2 | Node state setter | `set_sort_node_as__allocated` | `set_sort_node_as__deallocated` |
| B3 | Target node selection | Ignores `p_sort_nodes`; indexes from slot 0 of the manager pool | Use `p_sort_nodes` pointer arithmetic to target the actual allocated block |

Bug B2 means released nodes remain marked **allocated**, so
`allocate_sort_nodes_in__sort_list_manager` (which skips allocated nodes)
will never reclaim them — causing **premature pool exhaustion**.
Bug B3 means the wrong nodes are cleared (always nodes 0..N-1 of the pool
rather than the released sort list's actual block).
Bug B1 caps the release loop at 64, so sort lists with >64 nodes are only
partially released.

---

## 2. Impact Assessment

### Direct callers (within `./core/source/sort/sort_list/sort_list_manager.c`)

| Caller | Calls | Reliance on broken behavior |
|--------|-------|-----------------------------|
| `allocate_sort_list_in__sort_list_manager` | Both 1a and 1b helpers | Its **Precondition** guards are silently defeated; the function may proceed past resource exhaustion, or fail to detect node shortage. |
| `release_sort_list_in__sort_list_manager` | `release_sort_nodes_in__sort_list_manager` | The `+=` sign error (Defect A) directly corrupts the shared counter. The callee's three bugs (B1–B3) prevent node reclamation and corrupt node state. |

### `./core/include/sort/sort_list/sort_list_manager.h`

- `get_p_sort_node_by__index_in__sort_list_manager` — used by both
  `allocate_sort_nodes_in__sort_list_manager` and
  `release_sort_nodes_in__sort_list_manager`. After fixing B2, this
  accessor will correctly skip nodes that are marked deallocated (it
  checks `is_sort_node__allocated` indirectly via the node's flag).
  No change needed here, but its **Postcondition** (returning nullptr for
  deallocated nodes) becomes meaningful only once B2 is fixed.
- `get_p_sort_list_by__index_in__sort_list_manager` — used by
  `get_next_available__p_sort_list_in__sort_list_manager`. Not directly
  affected by the counter bugs, but will behave correctly once the
  list-exhaustion guard (1a) is restored.
- `is_sort_node_a__sort_list` — not directly affected.

### `./core/include/sort/sort_list/sort_list.h` and
### `./core/source/sort/sort_list/sort_list.c`

- `get_p_sort_node_by__index_from__sort_list` checks
  `is_sort_node__allocated` on each node it returns. Because Bug B2 leaves
  released nodes marked allocated, this function currently returns
  "released" nodes as if they were still valid. Once B2 is corrected,
  released nodes will be properly deallocated and this accessor will
  return nullptr for them — restoring the **Round Trip Property**
  (allocate → use → release → reallocate yields a clean state).

### `./core/include/defines.h`

- The `Sort_List_Manager` struct definition and the constants
  `SORT_LIST__MAXIMUM_QUANTITY_OF` (64) and `SORT_NODE__MAXIMUM_QUANTITY_OF`
  (512) define the **Representation Invariant**. The bugs cause the
  concrete counters to diverge from the invariant's intent.

### `./core/include/game.h`

- `get_p_sort_list_manager_from__game` returns `&p_game->sort_list_manager`.
  This is the sole **Information Hiding** boundary through which external
  code obtains the manager. All callers transitively depend on the
  manager's counters being correct.

### `./tests/core/source/sort/sort/list/test_suite_sort_sort_list_sort_list_manager.c`

- `sort_list_manager__release_sort_list` — asserts
  `quantity_of__allocated_sort_nodes == 0` after release. With Defect A
  (`+=` instead of `-=`), this assertion **fails** (counter becomes 4, not 0).
- `sort_list_manager__release_and_reallocate` — relies on the
  interplay of multiple bugs (Defect A inflates the node counter; Bug B2/B3
  leave nodes marked allocated; 1a/1b swap counters). This test currently
  "passes" only because the bugs cancel out in a narrow scenario. Correcting
  any subset of bugs without correcting all of them will expose latent
  failures. The test must be revalidated after the full fix set is applied.
- `sort_list_manager__allocate_sort_list` and
  `sort_list_manager__allocate_multiple` — allocate small counts (4, 8, 12
  nodes) where `allocated_nodes` (≤12) < 64, so the 1a underflow does not
  trigger. These tests pass today but will continue to pass after the fix,
  since the corrected guards produce the same pass/fail outcome for small
  allocations.

### `./core/source/sort/sort_list/heap_sort.c`

- `heap_sort.c` operates on `Sort_List` objects (via `p_sort_list->p_node_list`)
  but does not directly call the manager's allocate/release/available
  functions. It is **Coupled** transitively: it depends on nodes being
  correctly marked deallocated after release so that
  `get_p_sort_node_by__index_from__sort_list` returns valid (non-null)
  pointers for in-use nodes.

### Assumption invalidation summary

Correcting the broken behavior **invalidates** the following de-facto
contracts that callers currently rely on:

1. **Defeated exhaustion guard**: `allocate_sort_list_in__sort_list_manager`
   currently never aborts via the "no available sort list entries" path
   (due to 1a underflow). After the fix, this guard will fire when all 64
   list slots are consumed — callers that assumed unlimited list
   allocation will now hit the debug abort path.

2. **Inflated node availability**: `allocate_sort_list_in__sort_list_manager`
   currently overestimates available nodes (due to 1b). After the fix,
   allocations near the 512-node limit will be correctly rejected.

3. **Counter monotonicity on release**: `quantity_of__allocated_sort_nodes`
   currently **increases** on release (Defect A). After the fix, it
   **decreases**. Any code that read this counter and assumed it was
   monotonically increasing during release will break.

4. **Node reuse after release**: Nodes remain marked allocated after
   release (Bug B2). After the fix, they are properly deallocated and
   become eligible for reallocation. The **Round Trip Property**
   (allocate → release → reallocate) is restored.

---

## 3. Resolution Assessment

### Fix 1 — `get_quantity_of__available_sort_lists_in__sort_list_manager`
**File**: `core/include/sort/sort_list/sort_list_manager.h`
**Change**: Replace the callee call
`get_quantity_of__allocated_sort_nodes_in__sort_list_manager(...)`
with
`get_quantity_of__allocated_sort_lists_in__sort_list_manager(...)`.
**Callers**: `allocate_sort_list_in__sort_list_manager` — no caller-side
change needed; the fix is transparent to callers.

### Fix 2 — `get_quantity_of__available_sort_nodes_in__sort_list_manager`
**File**: `core/include/sort/sort_list/sort_list_manager.h`
**Change**: Replace the callee call
`get_quantity_of__allocated_sort_lists_in__sort_list_manager(...)`
with
`get_quantity_of__allocated_sort_nodes_in__sort_list_manager(...)`.
**Callers**: `allocate_sort_list_in__sort_list_manager` — no caller-side
change needed.

### Fix 3 — `allocate_sort_list_in__sort_list_manager`
**File**: `core/source/sort/sort_list/sort_list_manager.c`
**Change**: No direct code change required. The function's logic is correct;
it becomes correct automatically once Fixes 1 and 2 are applied.
**Verification**: After Fixes 1–2, the two **Precondition** guards will
function as intended. Re-run the existing test suite to confirm no
regressions for small allocations, and add a **Property Based Testing**
case that exhausts the list pool and node pool to verify the guards fire.

### Fix 4 — `release_sort_list_in__sort_list_manager` (Defect A)
**File**: `core/source/sort/sort_list/sort_list_manager.c`
**Change**: Change
`->quantity_of__allocated_sort_nodes += p_sort_list->size_of__p_node_list`
to
`->quantity_of__allocated_sort_nodes -= p_sort_list->size_of__p_node_list`.
**Callers**: Tests that assert the counter after release — these will now
pass correctly.

### Fix 5 — `release_sort_nodes_in__sort_list_manager` (Bugs B1–B3)
**File**: `core/source/sort/sort_list/sort_list_manager.c`
**Changes**:
- **B1**: Change the loop bound from `SORT_LIST__MAXIMUM_QUANTITY_OF` to
  `SORT_NODE__MAXIMUM_QUANTITY_OF`.
- **B2**: Change `set_sort_node_as__allocated(p_sort_node)` to
  `set_sort_node_as__deallocated(p_sort_node)`.
- **B3**: Index nodes via the `p_sort_nodes` parameter (pointer arithmetic
  from the base of the allocated block) instead of indexing from slot 0 of
  the manager's pool. The loop should iterate
  `p_sort_nodes[0 .. quantity_of__nodes-1]`.

**Callers**: `release_sort_list_in__sort_list_manager` — no caller-side
change needed; the fix is transparent.

### Fix ordering / blast radius

The fixes should be applied as a **single coherent change set** — not
piecemeal — because the bugs currently mask each other:

- Fixing only 1a/1b without fixing 4/5 leaves the release path broken,
  causing the corrected "available" queries to return incorrect values
  after any release.
- Fixing only 4/5 without fixing 1a/1b leaves the allocation guards
  defeated, so the corrected counters are never properly checked.

**Recommended order**: Fix 1 → Fix 2 → Fix 5 (B1, B2, B3) → Fix 4 (Defect A)
→ Fix 3 (verification). This restores the **Conservation Law** (counters
are conserved across allocate/release) before re-enabling the allocation
guards.

### Test updates

- `sort_list_manager__release_sort_list` — will pass once Fix 4 is applied.
- `sort_list_manager__release_and_reallocate` — must be revalidated after
  all fixes; the test should continue to pass with correct behavior.
- Add a **Round Trip Check** test: allocate N lists of varying node counts,
  release them in reverse order, and assert both counters return to 0 and
  all nodes are marked deallocated.
- Add a **Property Based Testing** case: exhaust the sort-list pool (64
  allocations) and verify the "no available sort list entries" guard
  triggers; exhaust the sort-node pool (512 nodes) and verify the
  "node size exceeds available" guard triggers.

### Documentation

No documentation updates are required — the function contracts
(**Preconditions**/**Postconditions**) in the review files already describe
the intended (correct) behavior. The implementation simply needs to match.
