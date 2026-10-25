# Planning: heap_sort.h — Incorrect Modules

**Review source:** `agents/core/review/include/sort/sort_list/heap_sort.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/sort/sort_list/heap_sort.h`
- `core/source/sort/sort_list/heap_sort.c`
- `core/include/sort/sort_list/sort_list.h` (driver: `run_sort`, `run_sort__once`, `run_sort_with__this_many_steps`)
- `core/include/defines.h` (`Sort_Node`, `Sort_List`, `Sort_Data`, `INDEX__UNKNOWN__SORT_NODE`)
- `tests/core/source/sort/sort_list/test_suite_sort_sort_list_heap_sort.c`

---

## 1. Problem Identification

Two functions in `core/source/sort/sort_list/heap_sort.c` were flagged **Incorrect**.

### 1a. `initialize_sort_list_as__heap` — spurious even-length Precondition
The initializer carries a debug-only guard that rejects odd-length lists:
```c
if (get_length_of__sort_list(p_sort_list) & 0b1) {
    debug_abort("...p_sort_list has odd length."); return;
}
```
Heap sort is **Total** over any element count; there is no algorithmic `Boundary Condition` requiring an even length. This guard is an invalid `Precondition` that aborts on valid inputs. Two secondary defects ride on it:
- **Mode Confusion (debug vs release):** the guard is inside `#ifndef NDEBUG`, so debug builds abort while release builds silently proceed — the function's observable contract differs by build mode.
- **Null-deref risk:** the per-node loop passes `get_p_sort_node_by__index_from__sort_list(...)` straight into `update_heap_sort_node__index_for__next_node`, which does pointer arithmetic and a field write. If a node is not `is_allocated` (its declared Precondition #4), that pointer is null → undefined behavior. No guard exists.
- **Cosmetic:** the debug message names the function `initialize_sort_list_as__heap_sort` while the symbol is `initialize_sort_list_as__heap`.

### 1b. `m_sort__heap_sort__sort_list` — self-recursion instead of heapify delegation (non-Terminating)
On the "not yet heapified" branch the function calls **itself**:
```c
if (!is_heap__heapifed(p_sort_list)) {
    m_sort__heap_sort__sort_list(p_sort_list);  // BUG: should be m_sort__heapify__sort_list
    return false;
}
```
Because the recursive call makes no state change, `is_heap__heapifed` stays false and the call recurses without a base case → unbounded recursion / stack overflow. This is a `State Desync`: the function mis-dispatches the **heapify phase** to its own **extraction phase**, violating the `Terminating` contract that every `m_Sort` step must eventually return `true`.

---

## 2. Impact Assessment

### Coupling to the broken behavior
- **`initialize_sort_list_as__heap_sort`** (same file) contains an *identical* odd-length guard and then calls `initialize_sort_list_as__heap`, which re-checks. The two initializers are `Coupled`: fixing only `initialize_sort_list_as__heap` leaves the duplicate guard in `initialize_sort_list_as__heap_sort`. Both must drop the guard to preserve a single `Precondition` (DRY / SSOT of the "valid input" contract).
- **Driver loop** (`sort_list.c::run_sort` = `while (!p_sort_list->m_sort(p_sort_list)) {}`). The self-recursion defect means that for any list initialized via `initialize_sort_list_as__heap_sort`, the *first* `m_sort` invocation (state: `index_of__heapification != INDEX__UNKNOWN__SORT_NODE`, i.e. not heapified) recurses infinitely. Correcting it to delegate to `m_sort__heapify__sort_list` restores the intended single-entry-point dispatch (heapify-then-extract) and makes the driver loop `Terminating`.
- **De-facto contract invalidated:** any caller that (a) passes an odd-length list, or (b) drives a `__heap_sort`-initialized list through `run_sort*`, currently relies on abort/crash in debug. After the fix these callers succeed where they previously failed — behavior is *corrected*, not preserved. No correct caller depends on the broken behavior, so no legitimate assumption is broken.

### Callers / consumers
- **Test suite** `test_suite_sort_sort_list_heap_sort.c` is the primary consumer:
  - `heap_sort__single_element` uses length **1** (odd) → currently trips the debug guard.
  - `heap_sort__heap_sort_completes`, `..._produces_sorted_order`, `..._already_sorted`, `..._reverse_sorted`, `..._run_sort_with_steps` all init via `initialize_sort_list_as__heap_sort` then run → currently stack-overflow on the first step.
- **Latent production consumer:** `Path_List` (`defines.h`) holds `p_min_heap_for__paths` / `p_max_heap_for__paths` (`Sort_List*`) for A* open/closed heaps. No pathfinding source is shipped yet, so there is no live caller — but any future pathfinding that heap-sorts an odd number of paths would hit the same guard. Low confidence, no action required now.

---

## 3. Resolution Assessment

### Fix 1a — `initialize_sort_list_as__heap` (and its twin)
- **Remove** the `& 0b1` even-length guard from **both** `initialize_sort_list_as__heap` and `initialize_sort_list_as__heap_sort`. Keep the null-`p_sort_list` guard.
- **Add a Precondition assertion** in the node loop: before calling `update_heap_sort_node__index_for__next_node`, assert `p_sort_node != 0` (covers Precondition #4, eliminates the null-deref UB).
- **Correct the debug message** string to `initialize_sort_list_as__heap`.
- Callers: none need signature changes. Tests: existing assertions remain valid; the odd-length cases now pass.

### Fix 1b — `m_sort__heap_sort__sort_list`
- **Replace the self-call** with delegation to the heapify phase:
  ```c
  if (!is_heap__heapifed(p_sort_list)) {
      m_sort__heapify__sort_list(p_sort_list);   // delegate, do NOT recurse into self
      return false;                              // not yet extracted; keep stepping
  }
  ```
- Keep `return false` (not the heapify return value): when heapify reports complete it flips `index_of__heapification` to `INDEX__UNKNOWN__SORT_NODE`; the *next* invocation then sees `is_heap__heapifed == true` and proceeds to extraction. Returning heapify's `true` here would falsely signal "fully sorted."
- No signature or caller changes; the header declaration is unchanged.

### Phasing
Both fixes are local to `heap_sort.c`, independent, and small. A single phase suffices; apply 1b first (it is the crash), then 1a. No other `.h`/`.c` file needs modification.

### Test verification checklist
- **Existing tests assert correct behavior (pre-flag)** and are currently failing/crashing: after the fixes they should pass unchanged. No assertion encodes the broken behavior, so nothing must be rewritten for correctness.
- **New coverage to add:**
  - **Property Based Testing:** for random lengths `n ∈ [0..64]` (incl. odd) and random value permutations, run to completion and assert the `Representation Invariant` (list ascending per `f_sort_heuristic`) and termination within a bounded step count.
  - **Boundary Condition** cases: length 0, 1, and 511/512 (near the 15-bit `index_for__next_node` limit) to confirm no truncation and no abort.
  - **Differential Testing:** compare `m_sort__heap_sort__sort_list` output against a reference sort on identical inputs to confirm the extraction phase is faithful.
  - **Mutation Testing:** confirm the suite catches the two original mutations (re-introducing the odd-length guard; reverting delegation to self-recursion).
- **Blast radius (tests):** Low — one suite file, additions only. No phased test rollout needed.

---

## 4. Blast Radius Summary
- **Files changed:** 1 (`core/source/sort/sort_list/heap_sort.c`); header and all callers unchanged.
- **Behavior-preserving for correct callers?** No — it *corrects* behavior: odd-length inputs and `__heap_sort`-driven runs change from abort/crash to correct, `Terminating` sorts. No valid caller depends on the broken behavior, so no legitimate de-facto contract is invalidated.
- **Phased approach needed?** No; two small, independent edits in one file.
- **Risk:** Low. Residual watch-item: the latent `Path_List` heaps should be re-checked if pathfinding is later shipped.
