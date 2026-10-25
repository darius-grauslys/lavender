# Planning: inventory_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/inventory/inventory_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/inventory/inventory_manager.h`
- `core/source/inventory/inventory_manager.c`
- `core/include/serialization/serialization_header.h` (helper contract)
- `core/source/serialization/serialization_header.c` (helper impl)
- `core/include/inventory/inventory.h`, `core/source/inventory/inventory.c` (init/reset callees)
- `core/include/defines.h` (`Inventory`, `Inventory_Manager`, `MAX_QUANTITY_OF__INVENTORY`)
- `core/source/entity/entity.c` (caller of the allocator)
- `tests/core/source/inventory/test_suite_inventory_inventory_manager.c`

**Flagged as Incorrect:**
- `release_inventory_in__inventory_manager`
- `allocate_p_inventory_using__this_uuid_in__inventory_manager`

---

## 1. Problem Identification

### 1.1 `allocate_p_inventory_using__this_uuid_in__inventory_manager`
**Defect class: Translation Gap / Surface-form leakage / State Desync — and a hard compile failure.**

The name promises to *allocate an inventory slot and brand it with the given `uuid`*. The body instead calls
`get_next_available__allocation_in__contiguous_array(...)`, which **does not exist anywhere in the codebase** (implicit
function declaration → build failure), and passes it a 3rd argument (`uuid`) that no real helper accepts. Consequences:

- **Compile error.** `inventory_manager.c` (and every TU that `#include`s it, e.g. the test suite) fails to build.
- **Dead parameter / State Desync.** Even if a helper resolved, `uuid` is never written to the returned slot's
  `_serialization_header`. The slot is left `IDENTIFIER__UNKNOWN__u32` (deallocated), so it violates the intended
  *Representation Invariant* that an allocated slot carries its uuid.
- **Lookup contract broken.** Because the header uuid is never set, `get_inventory_by__uuid_in__inventory_manager`
  can never find a slot this function "allocated."

### 1.2 `release_inventory_in__inventory_manager`
**Defect class: Boundary Condition defect + undefined behavior — confined to debug validation.**

The core reset is **correct**: it calls `initialize_inventory_as__empty`, which sets the header uuid to
`IDENTIFIER__UNKNOWN__u32` (deallocated) and clears all item stacks. The only defect is the `#ifndef NDEBUG` bounds check:

```c
if (p_inventory - p_inventory_manager->inventories >= MAX_QUANTITY_OF__INVENTORY) { ... }
```

- **One-sided Boundary Condition.** A pointer *before* the array start yields a negative difference, which is `< 64`,
  so the check incorrectly *passes* — it only catches pointers too far *past* the end.
- **Undefined behavior.** Pointer subtraction between pointers not belonging to the same array object (an unrelated
  `Inventory` not drawn from this manager's `inventories`) is UB.

---

## 2. Impact Assessment

### Who relies on the broken behavior

- **`allocate_p_inventory_using__this_uuid_in__inventory_manager`**
  - Caller: `core/source/entity/entity.c` (`m_entity_deserialization_handler__default`, ~line 348) calls it with
    `get_p_inventory_manager_from__game(p_game)` and the entity's uuid, then null-checks the result. Because the
    function does not compile, **this deserialization path is already broken**; there is no working de-facto contract
    to preserve — correcting it *restores* the intended contract rather than invalidating one.
  - The test suite `tests/.../test_suite_inventory_inventory_manager.c` `#include`s the `.c`, so the compile error
    currently blocks the **entire** inventory_manager test file from building.
- **`release_inventory_in__inventory_manager`**
  - No production caller found in `./source` (only the test suite references it). The flawed check is debug-only, so
    **no release-build behavior depends on it**. Callers do not rely on the check *passing* for out-of-range pointers.

### Assumptions invalidated by the fix

- **Allocator:** The de-facto (intended) contract is *"allocate returns a slot whose `_serialization_header.uuid` equals
  the requested uuid and is retrievable via `get_inventory_by__uuid`."* The current code fails it silently. Correcting it
  makes that contract real. Critically, `get_next_available_p_serialization_header` **re-returns the same first-deallocated
  slot on every call and does not mark it allocated**; therefore the fix *must* brand the slot (set uuid) as a side effect,
  otherwise repeated allocations collapse onto one slot (breaking distinctness). No caller needs signature changes.
- **Release:** Fixing the bounds check only changes *debug* error reporting for out-of-range/foreign pointers. It does not
  alter the reset postcondition, so no coupled assumption in `./include` or `./source` is invalidated.
- **Related latent instance (out of scope, flagged for awareness):** the same one-sided pointer-arithmetic pattern
  (`p_item_stack - p_inventory->items >= INVENTORY_ITEM_MAXIMUM_QUANTITY_OF`) appears in
  `remove_p_item_stack_from__inventory` (`core/source/inventory/inventory.c`). Not part of this review, but shares the
  identical UB / boundary flaw and should be corrected with the same range-check idiom.

---

## 3. Resolution Assessment

Both fixes are localized to **`core/source/inventory/inventory_manager.c`**. No header signature changes are required
(the `.h` already declares the correct shapes).

### 3.1 Fix `allocate_p_inventory_using__this_uuid_in__inventory_manager`
Replace the phantom call with the real helper plus an explicit allocation step:

```c
Inventory *allocate_p_inventory_using__this_uuid_in__inventory_manager(
        Inventory_Manager *p_inventory_manager,
        Identifier__u32 uuid) {
    Serialization_Header *p_header = get_next_available_p_serialization_header(
            (Serialization_Header *)p_inventory_manager->inventories,
            MAX_QUANTITY_OF__INVENTORY);
    if (!p_header) {
        return 0; // pool exhausted
    }
    Inventory *p_inventory = (Inventory *)p_header; // valid: header is first member
    initialize_inventory(p_inventory, uuid);        // brand uuid + clear stacks (marks allocated)
    return p_inventory;
}
```

- Uses `get_next_available_p_serialization_header` (2-arg, declared in `serialization/serialization_header.h`), which is
  `Correct` per review and pure (returns first deallocated slot or NULL).
- `initialize_inventory(p, uuid)` (`core/source/inventory/inventory.c`) sets the header uuid **and** clears item stacks —
  this single call both brands the slot and satisfies the allocated postcondition, and its uuid write makes the next
  `get_next_available_p_serialization_header` call advance to a *different* slot. (Equivalent: `ALLOCATE_P` macro +
  `remove_all_unequiped_item_stacks_from__inventory`.)
- **Callers:** none need changes (`entity.c` call is signature-compatible and now actually works).
- **Prerequisite:** grep the whole tree for `get_next_available__allocation_in__contiguous_array` during implementation to
  confirm no other TU references the phantom name.

### 3.2 Fix `release_inventory_in__inventory_manager`
Replace the one-sided pointer-arithmetic check with a proper range check (debug block only):

```c
if (p_inventory < p_inventory_manager->inventories
        || p_inventory >= p_inventory_manager->inventories + MAX_QUANTITY_OF__INVENTORY) {
    debug_error("release_inventory_in__inventory_manager, p_inventory was not allocated with this manager.");
    return;
}
```

- Removes the UB (no cross-array subtraction) and closes the low-side boundary gap.
- **Callers:** none to update; release-behavior postcondition is unchanged.

### 3.3 Documentation / spec
- Tests reference `docs/specs/core/inventory/inventory_manager.h.spec.md` (not present in tree). If that spec is authored,
  ensure the allocation postcondition ("returned slot's header uuid == requested uuid; retrievable by uuid") and the
  release preconditions are stated explicitly.

---

## 4. Test Verification Checklist

Existing suite: `tests/core/source/inventory/test_suite_inventory_inventory_manager.c` (8 stateless tests). It
**currently cannot compile** because it `#include`s the broken `.c`. Its assertions are written for the **correct**
behavior, so **no assertion changes are required** — the fix should make them pass as-is:

- `allocate__returns_non_null`, `allocate__can_retrieve_by_uuid` → require the uuid to actually be assigned (confirms §3.1).
- `allocate_multiple__different_uuids` / `each_retrievable` → require each allocation to *advance* the pool (confirms the
  allocate step must mark the slot allocated; a lookup-only helper would fail these).
- `release__cannot_retrieve_after`, `release_and_reallocate__works` → require release to set uuid to deallocated (already
  satisfied by `initialize_inventory_as__empty`).

**New / strengthened cases to add:**
- **Property Based Testing:** for any sequence of allocate/release ops, invariant holds — a slot is deallocated iff its
  header uuid == `IDENTIFIER__UNKNOWN__u32`; allocate of a fresh uuid yields a distinct, retrievable slot.
- **Boundary Condition (allocator):** fill all `MAX_QUANTITY_OF__INVENTORY` (64) slots, then assert the next allocate
  returns NULL (pool-exhausted path).
- **Boundary Condition / Fuzzing (release, debug build):** call release with a pointer before the array and with a
  foreign `Inventory*`; assert the range check now rejects both (previously the low-side case leaked through).
- **Round Trip Check:** allocate → add items → serialize → deserialize path in `entity.c` re-allocates by uuid and round-trips.

**Blast radius of tests:** Low. One test file; assertions unchanged, a few edge cases added. No phased rollout needed.

---

## 5. Blast Radius Summary

- **Files changed:** 1 source file (`core/source/inventory/inventory_manager.c`). Header `inventory_manager.h` unchanged.
- **Behavior-preserving for callers?**
  - Allocator: not a behavior change for existing callers — the function does not compile today; the fix *establishes*
    the intended contract. `entity.c` deserialization becomes functional with no caller edits.
  - Release: fully behavior-preserving in release builds; only debug validation is corrected.
- **De-facto contracts invalidated:** None broken — the allocator's intended contract is *restored*, not overturned.
- **Phased approach needed?** No. Both fixes are independent, local, and low-risk; they can land together. Recommend also
  scheduling the analogous bounds-check fix in `remove_p_item_stack_from__inventory` as a follow-up (separate review).
