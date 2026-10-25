# Planning: ui_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/ui/ui_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/ui/ui_manager.h`
- `core/source/ui/ui_manager.c`
- `tests/core/source/ui/test_suite_ui_ui_manager.c`

---

## 1. Problem Identification

Fifteen functions in the UI_Manager module are flagged as **Incorrect**. They fall into two categories: **critical safety defects** (undefined behavior, crashes, infinite loops) and **semantic/behavioral defects** (broken contracts, state desync, incomplete linkage).

### Critical Safety Defects

| # | Function | Core Defect |
|---|----------|-------------|
| 1 | `allocate_ui_manager__members` | Copy-paste error: second NULL check tests `pM_ui_element_pool` instead of `pM_ptr_array_of__ui_elements`. On second-malloc failure, `memset(NULL, …)` is undefined behavior; function returns `true` on failure. |
| 2 | `allocate_ui_element_from__ui_manager` | (a) Pool-full path logs via `debug_error` but does **not** `return 0`; execution falls through to allocation. (b) The null-check on the allocation result is guarded by `#ifndef NDEBUG`; in release builds a null result causes dereference of NULL in `initialize_ui_element`. |
| 3 | `get_ui_element__priority` | When the element is absent from the ptr array, `get_p_ptr_ui_element_from__ptr_array_in__ui_manager` returns NULL. The subsequent pointer subtraction `NULL − base` is undefined behavior (C standard: pointer arithmetic requires both operands within the same array). No null guard exists. |
| 4 | `swap_priority_of__ui_elenents_within__ui_manager` | Dereferences the return of `get_p_ptr_ui_element_from__ptr_array_in__ui_manager` without a null check. If either element is not in the array, `*NULL = …` is undefined behavior. |
| 5 | `detect_focus__strictly_under_cursor_in__ui_manager` | Passes the result of `get_p_hitbox_aabb_of__ui_element` directly to `is_vector_3i32_inside__hitbox_aabb` without a null check. A focused element without a registered hitbox causes a null dereference (release) or use of uninitialized vectors (debug). |
| 6 | `allocate_many_ui_elements_from__ui_manager` | Loop counter is `Quantity__u8` but the bound is `Quantity__u16`. When quantity > 255, the u8 counter wraps and the loop condition remains perpetually true → **infinite loop** with out-of-bounds writes. |
| 7 | `allocate_many_ui_elements_from__ui_manager_in__succession` | Same u8/u16 type mismatch as #6 (infinite loop). Additionally, no NULL check on any allocation result: a failed mid-chain allocation causes `p_current = NULL` then next-iteration `p_current->p_next` is undefined behavior. |
| 8 | `allocate_many_ui_elements_from__ui_manager_as__recursive_children` | No NULL check on allocation results (same pattern as #7). Additionally, a **Translation Gap**: the function name implies a bidirectional parent-child hierarchy, but the implementation only sets `p_child` pointers and never calls `set_ui_element_as__the_parent_of__this_ui_element`, leaving every child with `p_parent == NULL`. No priority ordering is established. |

### Semantic / Behavioral Defects

| # | Function | Core Defect |
|---|----------|-------------|
| 9 | `detect_focus_in__ui_manager` | **State Desync**: `set_p_ui_element_as__focused_in__ui_manager` assigns the manager's focused-pointer but never sets `UI_FLAGS__BIT_IS_FOCUSED` on the element. On the next call, `is_ui_element__focused` returns false, the cache is invalidated, and focus is re-detected every frame. Asymmetric with `drop_ui_element_focus_for__ui_manager` which clears both flag and pointer. |
| 10 | `get_highest_priority_ui_element_thats__under_the_cursor` | When an element has no registered hitbox, the function does `return 0` instead of `continue`. A non-interactive or container element at a lower index (higher priority) aborts the entire search, preventing discovery of a valid interactive element behind it. |
| 11 | `handle_drop_in__ui_manager` | **Aliasing Bug / State Desync**: In three locations the function uses `p_ui_manager->p_ui_element__focused` (the member) instead of the parameter `p_ui_element__focused`. Currently safe because the caller sets the member before calling, but creates a fragile implicit contract — any handler that mutates focus mid-invocation would cause incorrect behavior. |
| 12 | `release__ui_element_from__ui_manager` | **Stale focus pointer**: When the released element is the currently focused element, `p_ui_manager->p_ui_element__focused` is not cleared. After `DEALLOCATE_P`, the pointer dangles; `does_ui_manager_have__focused_ui_element` still returns true and subsequent polls invoke handlers on a deallocated element. |
| 13 | `set_ui_element_as__the_parent_of__this_ui_element` | In the `p_parent == p_child` degenerate case, the function sets `p_parent->p_parent = 0` (destroying an unrelated parent link) instead of clearing `p_parent->p_child` (the field that would create a self-referential cycle). Inconsistent with sibling functions in `ui_element.c`. |
| 14 | `get_p_ui_element_by__index_from__ui_manager` | Debug bounds check compares against compile-time `MAX_QUANTITY_OF__UI_ELEMENTS` (128) rather than the runtime-allocated size `p_ui_manager->max_quantity_of__ui_elements`. A manager allocated with capacity < 128 allows out-of-bounds array access for indices in `[capacity, 127]`. No null validation on `p_ui_manager` or the ptr array. |
| 15 | `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` | Stores the `Quantity__u16` return of `get_ui_element__priority` into `Quantity__u8` locals (narrowing conversion; safe today at MAX=128 but a latent **Boundary Condition** violation if the cap is raised). Propagates the NULL-pointer-arithmetic UB from #3 and the NULL-dereference from #4. |

---

## 2. Impact Assessment

### Internal Call Graph (within `ui_manager.c`)

The defects form a **coupled** cluster with cascading dependencies:

```
allocate_ui_manager__members  ──►  allocate_ui_element_from__ui_manager
        │                                    │
        │                                    ├──► allocate_many_…_in__succession
        │                                    ├──► allocate_many_…_as__recursive_children
        │                                    ├──► allocate_ui_element_from__ui_manager_as__child
        │                                    └──► release_all__ui_elements_from__ui_manager
        │
        └──► (all pool/array operations depend on correct allocation)

allocate_ui_element_from__ui_manager  ──►  (all batch allocators)
get_p_ptr_ui_element_from__ptr_array_in__ui_manager  ──►  get_ui_element__priority
                                                            swap_priority_of__ui_elenents…
                                                            set_ui_element_priority_higher_than…
                                                            release__ui_element_from__ui_manager

detect_focus_in__ui_manager  ──►  detect_focus__strictly_under_cursor_in__ui_manager
                                   poll_ui_manager__update_for__drag / held / clicked_and_dropped
get_highest_priority_ui_element_thats__under_the_cursor  ──►  detect_focus_in__ui_manager
handle_drop_in__ui_manager  ──►  poll_ui_manager__update_for__clicked_and_dropped
```

### External Callers (across `./include` and `./source`)

- **`poll_ui_manager__update`** (public API, called from game loop / rendering layer): internally invokes `detect_focus_in__ui_manager`, `detect_focus__strictly_under_cursor_in__ui_manager`, `handle_drop_in__ui_manager`, and all poll sub-functions. Every defect in the focus/detection/drop chain propagates to every UI interaction in the game.
- **`allocate_ui_element_from__ui_manager_as__child`** (public API, called by NDS UI window constructors): calls both `allocate_ui_element_from__ui_manager` and `set_ui_element_as__the_parent_of__this_ui_element`. The NULL-fallthrough in `allocate_ui_element_from__ui_manager` means a child can be NULL, and the subsequent `set_ui_element_as__the_parent_of__this_ui_element` call with a NULL child is handled (child==null detaches), but the element is silently missing.
- **`release_all__ui_elements_from__ui_manager`** (public API, called on scene teardown): calls `release__ui_element_from__ui_manager` in a loop. The stale-focus-pointer bug means if the focused element is released mid-loop, subsequent iterations may operate on a dangling pointer.
- **`foreach_ui_element_in__ui_manager`** and **`compose_all_ui_elements_in__ui_manager`**: use `get_p_ui_element_by__index_from__ui_manager`. The wrong bounds check means a manager with capacity < 128 can be over-read.
- **NDS UI layer** (`nds/source/ui/…`): UI windows, buttons, sliders, drop zones all allocate elements via the public API and register handlers. The `detect_focus_in__ui_manager` flag bug causes re-detection every frame (performance degradation). The `get_highest_priority_ui_element_thats__under_the_cursor` early-return bug means container/logical elements at lower indices block hit detection for interactive children.

### Assumptions Invalidated by Corrections

| Correction | Invalidated Assumption |
|------------|----------------------|
| Fix `allocate_ui_element_from__ui_manager` to `return 0` on full pool | Callers that do not check for NULL return (e.g., `allocate_many_…_in__succession`, `allocate_many_…_as__recursive_children`) will dereference NULL. They **must** also be fixed. |
| Fix `get_ui_element__priority` to guard against NULL | `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` currently relies on the (broken) pointer arithmetic; it must add its own null guard or propagate a sentinel. |
| Fix `swap_priority_of__ui_elenents_within__ui_manager` to null-check | `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` calls this; the caller must tolerate a no-op when elements are not found. |
| Fix `detect_focus_in__ui_manager` to set IS_FOCUSED flag | Any code that currently compensates for the missing flag (e.g., by re-detecting every frame) will see changed behavior. The caching becomes effective, which is the intended semantics but changes timing of input-mode resets. |
| Fix `get_highest_priority_ui_element_thats__under_the_cursor` to `continue` | Callers that assumed a NULL return means "no element under cursor" are fine (the function still returns NULL if truly nothing matches). However, callers that assumed the function would abort on the first non-hitbox element (unlikely but possible) would see different results. |
| Fix `handle_drop_in__ui_manager` to use parameter consistently | No external behavior change at current call sites (member and parameter are always in sync). The fix is **behavior-preserving** for current callers but removes a latent fragility. |
| Fix `release__ui_element_from__ui_manager` to clear focus | `poll_ui_manager__update_for__clicked_and_dropped` and other poll functions that check `does_ui_manager_have__focused_ui_element` after a release will now correctly see no focus. This is the intended behavior. |
| Fix `allocate_ui_manager__members` second check | The function will now correctly return `false` on second-malloc failure. Callers (e.g., `allocate_p_ui_manager_from__ui_context`) already check the return value, so this is **behavior-preserving** for the success path and **fixes** a silent corruption on the failure path. |

### De Facto Contracts

- The **packed-array invariant** (all non-null pointers contiguous from index 0) is relied upon by `get_highest_priority_ui_element_thats__under_the_cursor` (breaks on first null), `release__ui_element_from__ui_manager` (swap-remove), and `is_ui_manager__empty`. None of the defects break this invariant, but the `allocate_ui_element_from__ui_manager` full-pool fall-through **does** corrupt it (writes NULL into the array and advances the cursor past the end).

---

## 3. Resolution Assessment

### Phase 1: Critical Safety Fixes (independent, no API changes)

These fixes prevent undefined behavior and crashes. They are **behavior-preserving** for all valid inputs.

| Function | Change | Callers Need Updating? |
|----------|--------|----------------------|
| `allocate_ui_manager__members` | Change line 155: `if (!p_ui_manager->pM_ui_element_pool)` → `if (!p_ui_manager->pM_ptr_array_of__ui_elements)`. Additionally, initialize the randomizer via `initialize_repeatable_psuedo_random(&p_ui_manager->randomizer, (Identifier__u32)p_ui_manager)` after both allocations succeed. | No. Callers already check the bool return. |
| `allocate_ui_element_from__ui_manager` | (a) Add `return 0;` immediately after the full-pool `debug_error` (line 600). (b) Remove `#ifndef NDEBUG` / `#endif` around the null check on `p_ui_element` (lines 613–618) to make it unconditional. | No change needed for callers that already handle NULL (e.g., `allocate_ui_element_from__ui_manager_as__child`). Callers that do NOT check NULL (batch allocators) are fixed in Phase 2. |
| `get_ui_element__priority` | Add a null guard: if `p_ptr_ui_element` is NULL, return a **Sentinel** value (e.g., `MAX_QUANTITY_OF__UI_ELEMENTS`) or add a debug assertion. The function's contract is that the element IS in the array; the guard makes the violation explicit rather than UB. | Yes — see Phase 3. |
| `swap_priority_of__ui_elenents_within__ui_manager` | Add null checks on both `p_ptr_ui_element__this` and `p_ptr_ui_element__other`. If either is NULL, log a debug error and return (no-op). Add `set_ui_manager_as__dirty` call on successful swap (priority change affects rendering order). | No. The no-op is safe for all current callers. |
| `detect_focus__strictly_under_cursor_in__ui_manager` | Store the result of `get_p_hitbox_aabb_of__ui_element` in a local, check for NULL before calling `is_vector_3i32_inside__hitbox_aabb`. If NULL, treat as "not inside" (drop focus and re-detect), matching the pattern in `get_highest_priority_ui_element_thats__under_this_ui_element` which does `if (!p_hitbox_aabb) continue;`. | No. |

### Phase 2: Loop / Batch Allocator Fixes

These fix the infinite-loop and NULL-dereference bugs in batch allocators. They are **behavior-preserving** for valid inputs (quantity ≤ capacity, quantity ≤ 255).

| Function | Change | Callers Need Updating? |
|----------|--------|----------------------|
| `allocate_many_ui_elements_from__ui_manager` | Change loop counter from `Quantity__u8 buffer_index` to `Quantity__u16 buffer_index`. The existing pre-check (`quantity > max_quantity`) already prevents out-of-capacity allocation; the type fix prevents the wrap-around infinite loop. | No. The public signature is unchanged. |
| `allocate_many_ui_elements_from__ui_manager_in__succession` | (a) Change loop counter from `Quantity__u8` to `Quantity__u16`. (b) Add NULL check after each `allocate_ui_element_from__ui_manager` call: if NULL, break out of the loop and return the partial list (or NULL if the head failed). Add an upfront capacity check (`quantity > max_quantity → return 0`). | No. Return type unchanged; callers already handle NULL return. |
| `allocate_many_ui_elements_from__ui_manager_as__recursive_children` | (a) Add NULL check after each allocation: if NULL, break and return the partial chain. (b) **Replace** the direct `p_current->p_child = allocate_ui_element_from__ui_manager(…)` with a call to `set_ui_element_as__the_parent_of__this_ui_element(p_ui_manager, p_current, p_new_child)` to establish the bidirectional link and priority ordering. This closes the **Translation Gap** between the function name's semantic intent and the implementation. | Yes — callers that previously received a chain with `p_parent == NULL` on children will now get properly linked parent-child pairs with priority ordering. This is the **intended** behavior per the function name. |

### Phase 3: Semantic / Behavioral Fixes

These fix broken contracts and state desync. Some change observable behavior (correctly).

| Function | Change | Callers Need Updating? |
|----------|--------|----------------------|
| `detect_focus_in__ui_manager` | In `set_p_ui_element_as__focused_in__ui_manager` (the static inline helper at line 40), add a call to `set_ui_element_as__focused(p_ui_element)` so that the IS_FOCUSED flag is set atomically with the pointer assignment. This makes the helper symmetric with `drop_ui_element_focus_for__ui_manager`. | No external API change. The caching now works as intended. Input-mode resets will occur less frequently (only on actual focus changes), which is a **performance improvement**. |
| `get_highest_priority_ui_element_thats__under_the_cursor` | Change line 278–279: `if (!p_hitbox_aabb) return 0;` → `if (!p_hitbox_aabb) continue;`. Remove the stray semicolon at line 257. | No. The function still returns NULL if no element matches; it simply no longer aborts on non-hitbox elements. |
| `handle_drop_in__ui_manager` | Replace all three uses of `p_ui_manager->p_ui_element__focused` with the parameter `p_ui_element__focused`. Specifically: (a) line 461: pass `p_ui_element__focused` to `get_highest_priority_ui_element_thats__under_this_ui_element`; (b) line 469: pass `p_ui_element__focused` as second arg to `m_ui_receive_drop_handler`; (c) lines 476–477: pass `p_ui_element__focused` as first arg to `m_ui_dropped_handler`. | No. At current call sites the member and parameter are always identical; the fix is **behavior-preserving** but removes the implicit coupling. |
| `release__ui_element_from__ui_manager` | After `DEALLOCATE_P` and before the swap-remove, add: `if (p_ui_manager->p_ui_element__focused == p_ui_element) { drop_ui_element_focus_for__ui_manager(p_ui_manager); }`. This clears both the flag and the pointer, preventing a dangling reference. | No. Callers that release elements and then poll for input will now correctly see no focus rather than a stale pointer. |
| `set_ui_element_as__the_parent_of__this_ui_element` | In the `p_parent == p_child` branch (line 866–869), change `p_parent->p_parent = 0;` to `return;` (no modification), matching the pattern in `set_child_of__ui_element` and `set_parent_of__ui_element` in `ui_element.c`. The self-referential case is a no-op by design. | No. This is a degenerate case that should never occur in practice; the fix prevents corruption if it does. |
| `get_p_ui_element_by__index_from__ui_manager` (in `.h`) | Change the debug bounds check from `index_of__ui_element >= MAX_QUANTITY_OF__UI_ELEMENTS` to `index_of__ui_element >= p_ui_manager->max_quantity_of__ui_elements`. Add a null check on `p_ui_manager` (debug-only, consistent with codebase convention). | No. Callers that pass valid indices (< actual capacity) are unaffected. The fix only tightens the debug assertion to the correct bound. |
| `set_ui_element_priority_higher_than__this_ui_element_in__ui_manager` | (a) Change local variables from `Quantity__u8` to `Quantity__u16` to match the return type of `get_ui_element__priority`. (b) Add null checks: if either element is not found (detected via the sentinel from the Phase-1 fix in `get_ui_element__priority`, or by checking the ptr-array lookup directly), log a debug error and return. | No. The function's observable behavior for valid inputs is unchanged. |

### Phase 4: Test Updates

**Existing test impact:**
- `allocate_ui_manager__members__succeeds`: Currently passes because both mallocs succeed in the test environment. After the fix, the test still passes (success path unchanged). **No change needed.**
- `allocate_ui_element__exhaust_pool__returns_null`: Currently passes in debug builds (the `#ifndef NDEBUG` guard catches the null). After making the null check unconditional, the test still passes. **No change needed.** However, this test will now also pass in release builds.
- `allocate_many_ui_elements_in__succession__links_elements`: Uses quantity=3 with capacity=8. Well within u8 range. **No change needed** for the type fix.

**New tests required:**

| Test | Strategy | Purpose |
|------|----------|---------|
| `allocate_many_ui_elements__exceeds_u8_max` | **Property Based Testing**: allocate with quantity=300, capacity=400. Assert loop terminates and exactly 300 elements are allocated. | Catches the u8 wrap-around infinite loop. |
| `allocate_many_ui_elements__pool_exhausted_mid_batch` | **Boundary Condition** test: allocate capacity-1 elements, then request one more via batch allocator. Assert NULL return (or partial list), no crash. | Catches NULL-dereference on pool exhaustion. |
| `allocate_many_recursive_children__bidirectional_links` | **Round Trip Check**: allocate 3 recursive children, verify `p_head->p_child->p_parent == p_head`, `p_head->p_child->p_child->p_parent == p_head->p_child`, and priority ordering is established. | Closes the Translation Gap verification. |
| `get_ui_element__priority__element_not_in_array` | **Fuzzing**: pass a UI_Element not allocated from this manager. Assert no crash, sentinel/error return. | Catches NULL pointer arithmetic UB. |
| `swap_priority__element_not_in_array` | **Boundary Condition**: pass an element not in the ptr array. Assert no-op, no crash. | Catches NULL dereference. |
| `detect_focus__strictly_under_cursor__no_hitbox` | **Boundary Condition**: focus an element, remove its hitbox, call the function. Assert no crash, focus is dropped and re-detected. | Catches null hitbox dereference. |
| `detect_focus__caches_flag` | **Equivalence Check**: call `detect_focus_in__ui_manager` twice with cursor stationary. Assert the second call returns the cached element without resetting input mode. Verifies the IS_FOCUSED flag fix. | Verifies State Desync correction. |
| `get_highest_priority_under_cursor__non_hitbox_element_skipped` | **Property Based Testing**: place a non-interactive element (no hitbox) at index 0, an interactive element with hitbox under cursor at index 1. Assert the function returns the index-1 element. | Catches the premature `return 0` bug. |
| `release__focused_element__clears_focus` | **Round Trip Check**: focus an element, release it, assert `does_ui_manager_have__focused_ui_element == false` and `p_ui_element__focused == NULL`. | Catches stale focus pointer. |
| `set_parent_of_self__no_corruption` | **Boundary Condition**: call with p_parent == p_child. Assert no field is modified (or only p_child cleared). | Catches the wrong-field-clear bug. |
| `allocate_ui_manager__members__second_malloc_fails` | **Fuzzing** / mock: inject a malloc failure for the second allocation. Assert function returns `false`, first allocation is freed, no UB. | Catches the copy-paste pointer check bug. |

**Blast radius of test updates:** **Medium.** The existing 12 tests remain valid (no assertions invalidated). ~11 new tests are needed, all in `tests/core/source/ui/test_suite_ui_ui_manager.c`. No changes to other test suites are required.

---

## 4. Blast Radius Summary

| Dimension | Assessment |
|-----------|-----------|
| **Files requiring changes** | 2 source files: `core/source/ui/ui_manager.c` (14 of 15 fixes), `core/include/ui/ui_manager.h` (1 fix: `get_p_ui_element_by__index_from__ui_manager`). 1 test file: `tests/core/source/ui/test_suite_ui_ui_manager.c`. |
| **Behavior-preserving for current callers?** | Phase 1 and the `handle_drop_in__ui_manager` / `release__ui_element_from__ui_manager` fixes are behavior-preserving. The `detect_focus_in__ui_manager` flag fix changes timing (reduces redundant re-detection) — a performance improvement, not a behavioral regression. The `get_highest_priority_ui_element_thats__under_the_cursor` fix changes which element is returned when non-hitbox elements are present — this is the **correct** behavior per the function's semantic intent. The `allocate_many_…_as__recursive_children` fix changes the linkage from unidirectional to bidirectional — this is the **correct** behavior per the function name. |
| **Phased approach needed?** | Yes. Phase 1 (safety) must land before Phase 2 (batch allocators) because the batch allocators depend on `allocate_ui_element_from__ui_manager` returning NULL cleanly. Phase 3 (semantic) is independent of Phases 1–2 but should land after them to avoid conflating safety fixes with behavioral changes in review. |
| **De facto contracts invalidated?** | The `detect_focus_in__ui_manager` caching-not-working behavior is a de facto contract that external code may have adapted to (e.g., by not relying on focus persistence between frames). After the fix, focus will persist, which is the intended design. No external code in the NDS layer was found to explicitly compensate for this bug. The `get_highest_priority_ui_element_thats__under_the_cursor` early-return-on-no-hitbox behavior could be a de facto contract if UI layouts were designed assuming container elements block hit detection — unlikely but should be verified during integration testing. |
