# Planning: inventory.h — Incorrect Modules

**Review source:** `agents/core/review/include/inventory/inventory.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/inventory/inventory.h`
- `core/include/inventory/item_stack.h`
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/source/inventory/inventory.c`
- `core/source/inventory/item_stack.c`
- `core/source/inventory/inventory_manager.c`
- `tests/core/source/inventory/test_suite_inventory_inventory.c`
- `tests/core/source/inventory/test_suite_inventory_inventory_manager.c`

---

## Overview

Ten functions/modules in `core/include/inventory/inventory.h` and
`core/source/inventory/inventory.c` were flagged as **Incorrect**. The defects
fall into four thematic clusters:

| Cluster | Terminology | Modules |
|---|---|---|
| Stale `quantity_of__item_stacks` counter | **Conservation Law** violation, **Representation Invariant** breach | `initialize_inventory`, `initialize_inventory_as__empty`, `add_item_to__inventory` |
| Missing implementations / type mismatch | **Translation Gap**, **Stub-real divergence**, **Mode Confusion** | `remove_all_item_stacks_from__inventory`, `remove_item_stack_from__inventory_using__identifier_for__item_stack` |
| Logic bugs (item loss, over-removal) | **State Desync**, **Lost Update** | `move_p_item_stack_to__inventory`, `remove_this_many_item_kinds_from__inventory` |
| Validation / safety gaps | **Boundary Condition**, **Precondition** gap, **Conservative** | `copy_p_item_stack_to__inventory`, `deserialize_inventory` |

The shared field at the center of most defects is
`Inventory.quantity_of__item_stacks` (`Quantity__u8`), which tracks the number
of occupied item-stack slots. It is **incremented** by
`get_next_available_item_stack_in__inventory` (line 224), **decremented** by
`remove_p_item_stack_from__inventory` (line 346), **set** by
`deserialize_inventory` (line 161), and **read** by
`does_inventory_have__available_item_stacks` (line 473). It is the **Single
Source of Truth (SSOT)** for "how many slots are occupied" — yet three
functions fail to maintain it correctly.

---

## 1. Problem Identification

### 1.1 `initialize_inventory` — Incorrect

**Conservation Law / Representation Invariant violation.** The function clears
all 27 item stacks via `remove_all_unequiped_item_stacks_from__inventory` but
**never resets** `p_inventory->quantity_of__item_stacks` to 0. Since every
slot is emptied, the occupied-count invariant demands a value of 0, yet the
field retains whatever stale value it held prior to the call. This is a
**State Desync** between the actual slot contents (all empty) and the
counter (stale non-zero).

### 1.2 `initialize_inventory_as__empty` — Incorrect

**Conservation Law / Representation Invariant violation.** Identical defect to
1.1: the function marks the `Serialization_Header` as deallocated
(`IDENTIFIER__UNKNOWN__u32`) and clears all item stacks, but does **not** reset
`quantity_of__item_stacks` to 0. This is the Lavender-style "reset to pool"
initializer, so a stale counter directly violates the **Postcondition** that
the inventory be returned to a fully empty state.

### 1.3 `add_item_to__inventory` — Incorrect

**Conservation Law violation / State Desync.** When the function places a new
item into a previously empty slot (`Item_Kind__None`), it calls
`set_item_stack` directly — **bypassing** `get_next_available_item_stack_in__inventory`
— and therefore **never increments** `quantity_of__item_stacks`. The counter
becomes stale immediately after any addition to a fresh slot. Additionally,
the docstring is inaccurate: it claims the function "does nothing if the
inventory is already full," but the code actually calls `debug_abort` and
returns null.

### 1.4 `copy_p_item_stack_to__inventory` — Incorrect

**Precondition / Boundary Condition gap.** The function performs **no
null-pointer validation** on either `p_inventory` or
`p_item_stack__copy_origin`. If `p_inventory` is NULL, the call chain
`get_next_available_item_stack_in__inventory` →
`get_p_item_stack_from__inventory_by__index` dereferences
`&p_inventory->items[index]`, causing undefined behavior. If
`p_item_stack__copy_origin` is NULL, the inline `copy_item_stack` dereferences
the null source when reading `p_item_stack__source->item`,
`->quantity_of__items`, and `->max_quantity_of__items`. This is inconsistent
with peer functions `add_item_to__inventory` and `remove_p_item_stack_from__inventory`,
which both include `#ifndef NDEBUG` null checks.

### 1.5 `move_p_item_stack_to__inventory` — Incorrect

**Lost Update / State Desync (item loss).** The function composes a copy
(`copy_p_item_stack_to__inventory`) followed by an origin clear
(`initialize_item_stack_as__empty`). However, `copy_p_item_stack_to__inventory`
is **void** and provides no success/failure signal. When the inventory is full,
the copy silently returns (after a `debug_warning`), but `move_p_item_stack_to__inventory`
**unconditionally** clears the origin — destroying the item without relocating
it. This violates the move semantic: the origin is consumed but the data is
not preserved anywhere, resulting in **permanent item loss**.

### 1.6 `remove_this_many_item_kinds_from__inventory` — Incorrect

**State Desync (over-removal).** The function declares and initializes
`quantity_of__items_remaining_to__remove` to track the unmet remainder, but
**passes the original** `quantity_of__items_to__remove` to
`remove_quantity_of_items_from__item_stack` instead of the remaining value:

```c
quantity_of__items_remaining_to__remove =
    remove_quantity_of_items_from__item_stack(
            p_item_stack,
            quantity_of__items_to__remove);  // BUG: should be remaining
```

Every iteration attempts to remove the full original quantity from each stack
rather than the diminishing remainder, causing **over-removal** across
multiple stacks. For example, removing 10 items when the first stack holds 3
correctly empties it (returns 7 remaining), but the next stack receives 10
again (not 7), depleting more than intended. A secondary issue: the
`Quantity__u32` parameter is implicitly narrowed to `Quantity__u8` by
`remove_quantity_of_items_from__item_stack`, truncating values > 255.

### 1.7 `deserialize_inventory` — Incorrect

**Boundary Condition / Representation Invariant violation.** The function reads
`quantity_of__serialized_item_stacks` (a `Quantity__u8`, range 0–255) directly
from the file and uses it as a loop bound **without validating** it against
`INVENTORY_ITEM_MAXIMUM_QUANTITY_OF` (27). A corrupted or maliciously crafted
file containing a count > 27 causes the loop to call
`get_p_item_stack_from__inventory_by__index` with an out-of-bounds index,
performing `&p_inventory->items[index]` beyond the 27-element array —
**undefined behavior / buffer overflow**. Additionally, `deserialize_item_stack`
returns `void` and logs errors internally without propagating them, yet
`quantity_of__item_stacks` is set to the file-read count unconditionally,
potentially reporting more valid stacks than were actually deserialized.
Finally, the function lacks `#ifndef NDEBUG` null checks for `p_inventory`
and `p_serialization_request`, inconsistent with peer functions.

### 1.8 `remove_all_item_stacks_from__inventory` — Incorrect

**Translation Gap / Stub-real divergence.** The function is **declared** in
`core/include/inventory/inventory.h` (line 59) but has **no implementation**
in `core/source/inventory/inventory.c` or any other source file. Any call to
it produces a **linker error** (undefined reference). The related sibling
function `remove_all_unequiped_item_stacks_from__inventory` (inventory.c line
15) is implemented and used by `initialize_inventory` /
`initialize_inventory_as__empty`, but it also **fails to reset**
`quantity_of__item_stacks` to 0 — a semantic gap that the missing
implementation would have closed. The test
`inventory__remove_all__becomes_empty` is already disabled (`MUNIT_FAIL`)
with a TODO noting the missing implementation.

### 1.9 `remove_item_stack_from__inventory_using__identifier_for__item_stack` — Incorrect

**Translation Gap / Stub-real divergence + Mode Confusion.** The function is
**declared** in `core/include/inventory/inventory.h` (lines 50–52) but has
**no implementation** in any source file. Additionally, the declared parameter
type is `Identifier__u16` (`uint16_t`), but the lookup function it would
delegate to — `get_p_item_stack_from__inventory` — expects `Identifier__u32`
(`uint32_t`). The UUID system encodes the item-stack index in bits 26–31
(`UUID_BIT_SHIFT__INVENTORY__ITEM_STACK = 26`, `UUID_MASK__INVENTORY__ITEM_STACK`
= `MASK(6) << 26`). A `u16` parameter cannot represent bits 16–31; when
zero-extended to `u32`, the item-stack index bits are always 0, so the lookup
would always resolve to `items[0]`. The parameter type should be
`Identifier__u32` to match `get_p_item_stack_from__inventory`.

---

## 2. Impact Assessment

### 2.1 Stale `quantity_of__item_stacks` counter (Modules 1.1, 1.2, 1.3)

The `quantity_of__item_stacks` field is the **SSOT** for the number of
occupied item-stack slots. Three functions fail to maintain it:

- **`initialize_inventory`** (1.1) and **`initialize_inventory_as__empty`**
  (1.2) are the Lavender-style reset functions. Every consumer that calls
  them expects a fully empty inventory with `quantity_of__item_stacks == 0`.
  - **Caller:** `release_inventory_in__inventory_manager`
    (`core/source/inventory/inventory_manager.c`) calls
    `initialize_inventory_as__empty` when releasing an inventory back to the
    pool. A stale counter means the released inventory falsely reports
    occupied slots, causing `does_inventory_have__available_item_stacks` to
    return `false` even though all slots are empty.
  - **Caller:** `deserialize_inventory` (1.7) sets the counter correctly from
    the file, but if the inventory was previously initialized via
    `initialize_inventory`/`initialize_inventory_as__empty` (with a stale
    counter) and then deserialized, the counter is only correct *after*
    deserialization — any code reading the counter *between* initialization
    and deserialization sees stale data.

- **`add_item_to__inventory`** (1.3) bypasses
  `get_next_available_item_stack_in__inventory` (the only function that
  increments the counter) and calls `set_item_stack` directly. This means
  every slot occupation via `add_item_to__inventory` goes uncounted.
  - **Caller:** `does_inventory_have__available_item_stacks` reads the stale
    counter and will falsely report available slots even when slots are
    occupied (counter stays at 0 or stale value).
  - **Caller:** `get_next_available_item_stack_in__inventory` increments the
    counter — but since `add_item_to__inventory` doesn't use it, the counter
    can diverge from the actual number of non-empty stacks.

**De facto contract:** The current broken behavior is already being relied
upon as a de facto contract in the test suite. The test
`inventory__add_multiple__has_available_until_full` adds 27 items and asserts
`does_inventory_have__available_item_stacks` returns `false` at the end —
this **fails** because the counter is never incremented. The test
`inventory__add_when_full__returns_null` would also fail because the counter
never reaches 27, so the inventory is never detected as full. Correcting the
counter will **invalidate** these tests' current (broken) pass/fail
behavior — they must be updated to assert on the corrected counter.

### 2.2 Missing implementations (Modules 1.8, 1.9)

- **`remove_all_item_stacks_from__inventory`** (1.8): Declared but undefined.
  No production caller was found (it would fail to link). The only reference
  is a **disabled** test (`inventory__remove_all__becomes_empty`,
  `MUNIT_FAIL`). Implementing it will require the test to be re-enabled.
  - **Coupled** to `remove_all_unequiped_item_stacks_from__inventory`
    (inventory.c line 15), which is the existing clearing loop. The new
    implementation should delegate to or mirror this function and additionally
    reset `quantity_of__item_stacks` to 0.

- **`remove_item_stack_from__inventory_using__identifier_for__item_stack`**
  (1.9): Declared but undefined. No production caller was found. The type
  mismatch (`Identifier__u16` vs `Identifier__u32`) affects any future
  caller that passes a full UUID. The delegate
  `get_p_item_stack_from__inventory` (`Identifier__u32`) masks and shifts the
  identifier to extract the item-stack index from bits 26–31 — a `u16`
  parameter cannot carry those bits.

### 2.3 Logic bugs (Modules 1.5, 1.6)

- **`move_p_item_stack_to__inventory`** (1.5): Depends on
  `copy_p_item_stack_to__inventory` (1.4) for its copy step and
  `initialize_item_stack_as__empty` for the origin clear. The item-loss bug
  is triggered when the inventory is full. No production caller was found,
  but any game-action or entity code that moves items into a full inventory
  would silently destroy items.
  - **Coupled** to `copy_p_item_stack_to__inventory` — fixing the void-return
    problem requires changing `copy_p_item_stack_to__inventory`'s return type
    (or adding an out-parameter), which is a **Coupled** signature change
    affecting `move_p_item_stack_to__inventory` and any future callers.

- **`remove_this_many_item_kinds_from__inventory`** (1.6): Depends on
  `remove_quantity_of_items_from__item_stack` (item_stack.c, returns
  `Quantity__u32` remainder) and `remove_p_item_stack_from__inventory`
  (which decrements the counter). The over-removal bug means the function
  removes more items than requested across multiple stacks.
  - **Caller:** `does_inventory_have_this_many_of__item_kind` (inventory.c)
    reads the same stacks and would report incorrect totals after an
    over-removal.
  - **Test impact:** `inventory__remove_this_many__removes_correct_quantity`
    and `inventory__remove_this_many__removes_all_empties_inventory` would
    **fail** because the bug removes too many items.

### 2.4 Validation / safety gaps (Modules 1.4, 1.7)

- **`copy_p_item_stack_to__inventory`** (1.4): Missing null checks are
  **Coupled** to `get_next_available_item_stack_in__inventory` (which
  dereferences `p_inventory`) and `copy_item_stack` (which dereferences
  `p_item_stack__copy_origin`). No production caller was found outside of
  `move_p_item_stack_to__inventory` (1.5), which passes its own parameters
  through.

- **`deserialize_inventory`** (1.7): The out-of-bounds read on the count
  field is a **Boundary Condition** that affects `get_p_item_stack_from__inventory_by__index`
  (which performs `&p_inventory->items[index]` with no bounds check). The
  swallowed errors from `deserialize_item_stack` are **Coupled** to the
  counter being set unconditionally — the inventory may report N occupied
  stacks when fewer were actually deserialized, leaving the remaining slots
  in stale/empty state.

### 2.5 Inventory manager coupling

`release_inventory_in__inventory_manager` (inventory_manager.c, line ~70)
calls `initialize_inventory_as__empty` (1.2). The stale-counter bug means
released inventories retain a non-zero `quantity_of__item_stacks`, causing
`does_inventory_have__available_item_stacks` to return `false` for a
freshly-released inventory. The inventory manager tests
(`inventory_manager__release__cannot_retrieve_after`,
`inventory_manager__release_and_reallocate__works`) would exhibit
undefined behavior because `initialize_inventory` /
`initialize_inventory_as__empty` leave `quantity_of__item_stacks`
indeterminate on stack-allocated `Inventory` variables.

---

## 3. Resolution Assessment

### 3.1 `initialize_inventory` (1.1) and `initialize_inventory_as__empty` (1.2)

**What needs to change:** Add `p_inventory->quantity_of__item_stacks = 0;`
after the call to `remove_all_unequiped_item_stacks_from__inventory` in
both functions. This restores the **Conservation Law**: all slots emptied →
counter is 0.

**Caller updates:** None. The function signatures and post-conditions are
unchanged; only the counter is now correctly maintained.

**Test updates:** The existing tests
`inventory__initialize__has_available_stacks` and
`inventory__initialize__is_empty` will continue to pass (they don't directly
assert on the counter, but the counter being correct prevents UB in
subsequent operations). New assertions on `quantity_of__item_stacks == 0`
after initialization should be added.

### 3.2 `add_item_to__inventory` (1.3)

**What needs to change:** After successfully locating an empty slot
(`Item_Kind__None`) in the fallback path, increment
`p_inventory->quantity_of__item_stacks`. This should be done **only** when a
new slot is occupied (not when merging into an existing stack). The fix is
consistent with how `get_next_available_item_stack_in__inventory` handles the
increment. Also correct the docstring to reflect that the function calls
`debug_abort` (not "does nothing") when the inventory is full.

**Caller updates:** None — the signature is unchanged. The counter is now
maintained, which means `does_inventory_have__available_item_stacks` will
report correctly.

**Test updates:** `inventory__add_multiple__has_available_until_full` will
begin to pass correctly (counter reaches 27 after 27 additions, then
`does_inventory_have__available_item_stacks` returns `false`).
`inventory__add_when_full__returns_null` will also pass (the 28th add
triggers `debug_abort` as expected). Add a `Property Based Testing`
assertion: after N additions, `quantity_of__item_stacks == N` and
`does_inventory_have__available_item_stacks` returns `N < 27`.

### 3.3 `copy_p_item_stack_to__inventory` (1.4)

**What needs to change:** Add `#ifndef NDEBUG` null checks for both
`p_inventory` and `p_item_stack__copy_origin`, consistent with
`add_item_to__inventory` and `remove_p_item_stack_from__inventory`:
```c
#ifndef NDEBUG
    if (!p_inventory) {
        debug_abort("copy_p_item_stack_to__inventory, p_inventory is null.");
        return;
    }
    if (!p_item_stack__copy_origin) {
        debug_abort("copy_p_item_stack_to__inventory, p_item_stack__copy_origin is null.");
        return;
    }
#endif
```

**Caller updates:** None. The signature is unchanged.

**Test updates:** Add a `Fuzzing` test case that passes NULL for each
parameter in debug builds and verifies the `debug_abort` is triggered.

### 3.4 `move_p_item_stack_to__inventory` (1.5)

**What needs to change:** The root cause is that `copy_p_item_stack_to__inventory`
(1.4) is `void` with no success signal. Two resolution paths:
1. **Preferred:** Change `copy_p_item_stack_to__inventory` to return
   `Item_Stack*` (the destination pointer, or NULL on failure), then have
   `move_p_item_stack_to__inventory` check the return value before clearing
   the origin. This is a **Coupled** signature change.
2. **Alternative:** Have `move_p_item_stack_to__inventory` check
   `does_inventory_have__available_item_stacks` before attempting the copy
   and origin clear.

Path 1 is preferred because it addresses the root cause (the void return)
and provides a reusable success signal. Path 2 is a workaround that
duplicates the availability check.

**Caller updates:** `copy_p_item_stack_to__inventory`'s return type change
(affects 1.4) requires updating `move_p_item_stack_to__inventory` (1.5) to
check the return. No other callers of `copy_p_item_stack_to__inventory`
were found in production code.

**Test updates:** Add a test that fills the inventory to capacity, then
calls `move_p_item_stack_to__inventory` with a valid origin, and asserts
that the origin is **not** cleared (item preserved). Use a `Round Trip Check`:
move an item in, verify it's in the inventory, verify the origin is empty.

### 3.5 `remove_this_many_item_kinds_from__inventory` (1.6)

**What needs to change:** Replace the argument
`quantity_of__items_to__remove` with `quantity_of__items_remaining_to__remove`
in the call to `remove_quantity_of_items_from__item_stack`:
```c
quantity_of__items_remaining_to__remove =
    remove_quantity_of_items_from__item_stack(
            p_item_stack,
            quantity_of__items_remaining_to__remove);  // FIXED
```
This ensures each iteration only removes the diminishing remainder, achieving
the **Conservation Law** of total items removed.

**Caller updates:** None — the signature is unchanged.

**Test updates:** `inventory__remove_this_many__removes_correct_quantity`
and `inventory__remove_this_many__removes_all_empties_inventory` will begin
to pass. Add a `Property Based Testing` assertion: after removing K items
from a stack of N (K ≤ N), the remaining count is exactly N − K. Add a
multi-stack test: distribute removal across stacks and verify the total
removed equals the requested amount.

### 3.6 `deserialize_inventory` (1.7)

**What needs to change:**
1. **Boundary Condition fix:** After reading
   `quantity_of__serialized_item_stacks`, validate it against
   `INVENTORY_ITEM_MAXIMUM_QUANTITY_OF`:
   ```c
   if (quantity_of__serialized_item_stacks > INVENTORY_ITEM_MAXIMUM_QUANTITY_OF) {
       debug_error("deserialize_inventory, serialized count %u exceeds maximum %u.",
           quantity_of__serialized_item_stacks, INVENTORY_ITEM_MAXIMUM_QUANTITY_OF);
       return PLATFORM_Read_File_Error__Unknown;
   }
   ```
2. **Error propagation:** Change `deserialize_item_stack` (item_stack.h/c)
   to return `PLATFORM_Read_File_Error` instead of `void`, and propagate the
   error from `deserialize_inventory`. If any stack fails to deserialize,
   return the error immediately without setting the counter.
3. **Null checks:** Add `#ifndef NDEBUG` null checks for `p_inventory` and
   `p_serialization_request`, consistent with peer functions.

**Caller updates:** `deserialize_item_stack`'s signature change (void →
`PLATFORM_Read_File_Error`) is **Coupled** and affects its definition in
`item_stack.c` and its declaration in `item_stack.h`. Any other caller of
`deserialize_item_stack` must be updated to check the return value.

**Test updates:** Add a `Fuzzing` test that writes a count byte > 27 to a
file and verifies `deserialize_inventory` returns an error without
out-of-bounds access. Add an `Equivalence Check` test that round-trips
serialize → deserialize and verifies the inventory state matches.

### 3.7 `remove_all_item_stacks_from__inventory` (1.8)

**What needs to change:** Implement the function body in
`core/source/inventory/inventory.c`. Following the pattern of
`remove_all_unequiped_item_stacks_from__inventory` (which clears all slots),
the implementation should also reset `quantity_of__item_stacks` to 0:
```c
void remove_all_item_stacks_from__inventory(Inventory *p_inventory) {
#ifndef NDEBUG
    if (!p_inventory) {
        debug_abort("remove_all_item_stacks_from__inventory, p_inventory is null.");
        return;
    }
#endif
    remove_all_unequiped_item_stacks_from__inventory(p_inventory);
    p_inventory->quantity_of__item_stacks = 0;
}
```

**Caller updates:** None — the declaration already exists; only the
definition is missing.

**Test updates:** Re-enable `inventory__remove_all__becomes_empty` (remove
the `MUNIT_FAIL` and uncomment the body). Add a `Round Trip Check`: add
items → verify non-empty → remove all → verify empty and
`quantity_of__item_stacks == 0`.

### 3.8 `remove_item_stack_from__inventory_using__identifier_for__item_stack` (1.9)

**What needs to change:**
1. **Type fix:** Change the parameter from `Identifier__u16` to
   `Identifier__u32` in both the header declaration and the (new) implementation,
   matching `get_p_item_stack_from__inventory`.
2. **Implementation:** Add the function body to `inventory.c`:
   ```c
   void remove_item_stack_from__inventory_using__identifier_for__item_stack(
           Inventory *p_inventory,
           Identifier__u32 identifier_for__item_stack) {
       Item_Stack *p_item_stack =
           get_p_item_stack_from__inventory(
                   p_inventory, identifier_for__item_stack);
       remove_p_item_stack_from__inventory(
               p_inventory, p_item_stack);
   }
   ```

**Caller updates:** Any caller passing a `u16` literal will need to pass a
`u32` instead. Since no production callers were found, the blast radius is
limited to the header declaration and the test suite.

**Test updates:** Add a test that allocates an item stack, retrieves its
UUID, calls
`remove_item_stack_from__inventory_using__identifier_for__item_stack` with
the full `u32` UUID, and verifies the stack is emptied and the counter
decremented. Use a `Round Trip Check`: add item → remove by UUID → verify
empty.

---

## 4. Test Verification Checklist

| Test File | Test Function | Current Status | Impact of Fix |
|---|---|---|---|
| `test_suite_inventory_inventory.c` | `inventory__initialize_as_empty__is_empty` | Passes (checks `is_inventory__empty`, not counter) | No change needed; add counter assertion |
| `test_suite_inventory_inventory.c` | `inventory__initialize__has_available_stacks` | Passes (counter is stale/garbage but `< 27`) | Will pass correctly after 3.1; add counter == 0 assertion |
| `test_suite_inventory_inventory.c` | `inventory__initialize__is_empty` | Passes | No change; add counter assertion |
| `test_suite_inventory_inventory.c` | `inventory__add_item__returns_non_null` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__add_item__no_longer_empty` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__add_item__can_find_by_kind` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__add_item__find_nonexistent_returns_null` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__does_have_item_kind__*` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__does_have_this_many__*` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__remove_item_stack__becomes_empty` | Passes (UB risk: counter is garbage) | Will be correct after 3.1; counter properly maintained |
| `test_suite_inventory_inventory.c` | `inventory__remove_all__becomes_empty` | **Disabled** (`MUNIT_FAIL`, TODO) | Re-enable after 3.7 |
| `test_suite_inventory_inventory.c` | `inventory__remove_this_many__removes_correct_quantity` | **Fails** (over-removal bug) | Passes after 3.5 |
| `test_suite_inventory_inventory.c` | `inventory__remove_this_many__removes_all_empties_inventory` | **Fails** (over-removal bug) | Passes after 3.5 |
| `test_suite_inventory_inventory.c` | `inventory__get_by_index__returns_valid_stack` | Passes | No change |
| `test_suite_inventory_inventory.c` | `inventory__add_multiple__has_available_until_full` | **Fails** (counter never increments) | Passes after 1.1/1.2 + 1.3 |
| `test_suite_inventory_inventory.c` | `inventory__add_when_full__returns_null` | **Fails** (counter never reaches 27) | Passes after 1.1/1.2 + 1.3 |
| `test_suite_inventory_inventory.c` | `inventory__iterator__finds_all_matching_stacks` | Passes | No change |
| `test_suite_inventory_inventory_manager.c` | `inventory_manager__allocate__*` | **Fails** (broken `allocate_p_inventory_using__this_uuid_in__inventory_manager` — separate review) | Not in scope for this plan |
| `test_suite_inventory_inventory_manager.c` | `inventory_manager__release__*` | Passes (release builds) / UB (debug, stale counter) | Correct after 3.1 |

**Recommended new tests (using terminology):**
- **`Property Based Testing`** for `quantity_of__item_stacks`: after N
  additions and M removals, assert `quantity_of__item_stacks == N − M` and
  `does_inventory_have__available_item_stacks` returns
  `(N − M) < INVENTORY_ITEM_MAXIMUM_QUANTITY_OF`.
- **`Round Trip Check`** for `move_p_item_stack_to__inventory`: move an item
  in → verify it's present → verify origin is cleared; and move-when-full →
  verify origin is preserved.
- **`Round Trip Check`** for `deserialize_inventory`: serialize → deserialize
  → verify all slots and counter match.
- **`Fuzzing`** for `deserialize_inventory`: feed a count byte > 27 and
  verify no out-of-bounds access (error returned).
- **`Equivalence Check`** for `remove_this_many_item_kinds_from__inventory`:
  verify total items removed equals the requested amount across multiple
  stacks.
- **`Mutation Testing`** for the `quantity_of__items_remaining_to__remove`
  fix: confirm the test suite catches the original over-removal bug.

**Test blast radius:** Medium. Six existing tests will change from failing to
passing (or from UB to correct). One test must be re-enabled. New tests
should be added for edge cases (null inputs, full inventory, over-removal
across stacks, corrupted deserialization).

---

## 5. Blast Radius Summary

- **Files requiring changes:** 3 source/header files + 1 test file
  - `core/source/inventory/inventory.c` — fix 1.1, 1.2, 1.3, 1.4, 1.5, 1.6,
    1.7 (counter, null checks, loop variable), 1.8 (new implementation)
  - `core/include/inventory/inventory.h` — fix 1.9 (parameter type
    `Identifier__u16` → `Identifier__u32`)
  - `core/include/inventory/item_stack.h` — fix 1.7 (change
    `deserialize_item_stack` return type from `void` to
    `PLATFORM_Read_File_Error`)
  - `core/source/inventory/item_stack.c` — fix 1.7 (update
    `deserialize_item_stack` definition to return error)
  - `tests/core/source/inventory/test_suite_inventory_inventory.c` —
    re-enable `inventory__remove_all__becomes_empty`; add new test cases

- **Behavior-preserving for current callers:** No. The counter fixes (1.1,
  1.2, 1.3) change the observable state of `quantity_of__item_stacks`, which
  is read by `does_inventory_have__available_item_stacks`. Any caller
  relying on the counter being stale (e.g., always reporting available slots)
  will see corrected behavior. No production callers were found that depend
  on the stale counter, but the test suite has assertions that encode the
  broken behavior (e.g., `inventory__add_multiple__has_available_until_full`
  currently fails).

- **Phased approach:** The fixes can be grouped into three phases:
  1. **Phase 1 (counter correctness):** Fix 1.1, 1.2, 1.3 — the three
     counter bugs. This is the foundation; all other fixes depend on the
     counter being correct.
  2. **Phase 2 (validation & safety):** Fix 1.4 (null checks), 1.6 (loop
     variable), 1.7 (bounds check + error propagation).
  3. **Phase 3 (missing implementations & item loss):** Fix 1.5 (move
     semantics — depends on 1.4's return type change), 1.8 (new
     implementation), 1.9 (new implementation + type fix).

- **De facto contracts invalidated:**
  - `does_inventory_have__available_item_stacks` currently returns `true`
    after `add_item_to__inventory` (counter stays stale) — correcting 1.3
    invalidates this false positive.
  - `quantity_of__item_stacks` after `initialize_inventory` /
    `initialize_inventory_as__empty` is currently indeterminate — correcting
    1.1/1.2 invalidates the assumption that the counter is garbage.
  - `deserialize_inventory` currently accepts any count 0–255 — adding the
    bounds check invalidates the assumption that corrupted files with counts
    > 27 are silently accepted (they will now return an error).
  - `remove_item_stack_from__inventory_using__identifier_for__item_stack`
    currently accepts `Identifier__u16` — changing to `Identifier__u32`
    invalidates any caller passing a `u16` literal (none found).

- **Overall blast radius:** Medium. The changes are localized to the
  inventory module (3 files + 1 test file) with one coupled change to
  `item_stack.h`/`item_stack.c` (the `deserialize_item_stack` return type).
  No cross-module callers were found in production code, but the test suite
  has 6 tests that currently fail or exhibit UB and will be corrected.
