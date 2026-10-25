# Planning: item_stack_allocation_specifier.h — Incorrect Modules

**Review source:** `agents/core/review/include/inventory/item_stack_allocation_specifier.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/inventory/item_stack_allocation_specifier.h`
- `core/source/inventory/item_stack_allocation_specifier.c`
- `core/include/defines.h` (struct `Item_Stack_Allocation_Specifier`, line 966)
- `core/source/inventory/item_stack_manager.c` (sole in-tree caller chain)
- `tests/core/source/inventory/test_suite_inventory_item_stack_allocation_specifier.c`

---

## 1. Problem Identification

One function flagged **Incorrect** by the review:

### `initialize_item_stack_allocation_specifier` (`core/source/inventory/item_stack_allocation_specifier.c`)
- **Defect (Translation Gap / incomplete Postcondition):** The name promises a full initialization — resetting the struct to its initial state — but the body assigns only 2 of the struct's 3 fields (`the_kind_of_item__this_specifier_is_for`, `f_item_stack__create`). `is_item_stack_allocation_specifier__allocated` is omitted, so a previously "allocated" specifier re-initialized through this function retains its stale flag: a **State Desync** between the reset kind/factory and the carried-over allocation bit.
- The sole caller, `initialize_item_stack_allocation_specifier_as__empty` (header inline wrapper), compensates by explicitly setting the flag to `false` after the call. That compensation **masks** the base-function defect and makes the wrapper a de facto contract for "fully initialized" state, violating **Single Source of Truth (SSOT)**: two places encode what initialization means.

No other functions in this module are flagged; `is_...__allocated`, `set_..._as__allocated`, `set_..._as__deallocated` are correct and unaffected.

## 2. Impact Assessment

**Who relies on the broken behavior:**
- **`core/source/inventory/item_stack_manager.c`** is the only in-tree consumer:
  - `initialize_item_stack_manager` (line 17) calls `initialize_item_stack_allocation_specifier_as__empty` on all 256 specifier slots — it never calls the base function directly.
  - `allocate_...` / `release_..._specification_in__item_stack_manager` read and write the flag via the correct `is_/set_...` accessors.
- No code in `core/include` or `core/source` outside the inventory module references the specifier, and no other top-level tree (`sdl/`, `nds/`, `no_gui/`) contains copies of these files.

**Assumptions invalidated by correcting the behavior:**
- The wrapper `_as__empty`'s explicit `= false` assignment becomes **redundant** (its only unique job was to patch the base function's hole). It does not become *wrong* — setting `false` twice is **Idempotence**-safe — but it is now duplicated state management (DRY violation) and should be removed as cleanup.
- No caller relies on the stale-flag retention: nothing in-tree calls the base function directly, so no de facto contract is broken by making initialization total.
- The **Representation Invariant** "allocated flag reflects actual allocation state after any initialize" becomes enforceable; `initialize_item_stack_manager`'s 256-slot loop becomes robust even if slots previously held `allocated == true`.

**Blast radius:** 1 line added in one `.c` file; optional 3-line removal in one inline wrapper. Behavior-preserving for every current caller.

## 3. Resolution Assessment

### Step 1 — Fix the base function (`core/source/inventory/item_stack_allocation_specifier.c`)
Add the missing assignment so initialization is total:
```c
p_item_stack_allocation_specifier
    ->is_item_stack_allocation_specifier__allocated = false;
```
- Postcondition becomes: all three fields are assigned (caller values for kind/factory, `false` for the allocation flag). Initialization becomes **Idempotent** and safe on pool-reused / recycled structs.

### Step 2 — Remove the masking compensation (`core/include/inventory/item_stack_allocation_specifier.h`)
- Delete the explicit `->is_item_stack_allocation_specifier__allocated = false;` line from `initialize_item_stack_allocation_specifier_as__empty`; the base function now guarantees it. Restores SSOT: one place defines initialization semantics.

### Step 3 — Tests (`tests/core/source/inventory/test_suite_inventory_item_stack_allocation_specifier.c`)
Existing tests are stateless (fresh stack `spec`, indeterminate flag) and assert only kind/factory after base-init; none assert the broken flag-retention, so **no existing assertion is invalidated**. Add:
- **Property Based Testing:** for any prior state `(kind', flag', factory')`, `initialize(spec, k, f)` yields `(k, false, f)` — the allocated bit never survives initialization.
- **Round Trip Check:** `initialize_as__empty` → `set_allocated` → `initialize` (any) ⇒ flag is `false`; verify the wrapper's **Equivalence Check** with the base function (both produce identical structs for `Item_Kind__None, 0`).
- Boundary case: base-init on a spec with flag pre-set `true` clears it (the exact regression the review identified).

### Phasing
Not needed. Single atomic change (Steps 1+2 land together; Step 3 lands with or immediately after). The change is behavior-preserving for all current callers, so no coordination with other modules is required.

## 4. Blast Radius Summary

- **Files changed:** 2 source files (`item_stack_allocation_specifier.c`, `item_stack_allocation_specifier.h`) + 1 test file.
- **Behavior-preserving for current callers:** Yes — the only caller chain (`initialize_item_stack_manager` → `_as__empty`) already observes `allocated == false`; the fix merely makes that guaranteed by the base function.
- **De facto contracts invalidated:** None — the masking compensation in `_as__empty` is removed, not broken.
- **Test impact:** Low — no assertions invalidated; ~2 new test cases added.
