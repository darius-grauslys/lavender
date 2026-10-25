# Planning: item_stack.h — Incorrect Modules

**Review source:** `agents/core/review/include/inventory/item_stack.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/inventory/item_stack.h`
- `core/source/inventory/item_stack.c`
- `core/include/inventory/inventory.h`
- `core/source/inventory/inventory.c`
- `core/include/defines.h`
- `tests/core/source/inventory/test_suite_inventory_item_stack.c`

---

## 1. Problem Identification

Three functions in the `item_stack` module are flagged as **Incorrect**:

### `is_p_item_stack___full` (triple underscore) — `core/include/inventory/item_stack.h`

**Defect:** Inverted comparison operator. The implementation uses `<` (less-than) where it should use `>=` (greater-than-or-equal). The function returns `true` when the stack has *room remaining* (`quantity < max`), which is the semantic inverse of "full." A `Postcondition` violation: the name promises "is full" but the body computes "is not full."

### `is_p_item_stack__full` (double underscore) — `core/include/inventory/item_stack.h`

**Defect:** Missing empty-item guard. The function compares `quantity_of__items == max_quantity_of__items` without first excluding the empty-stack case. After `initialize_item_stack_as__empty`, both fields are `0`, so `0 == 0` yields `true`, incorrectly reporting an empty stack as full. This is a **Boundary Condition** failure at the zero-quantity edge of the domain. The sibling function `is_p_item_stack___full` correctly guards with `!is_p_item__empty(...)`, establishing the expected pattern.

### `set_item_stack` — `core/source/inventory/item_stack.c`

**Defect:** Parameter types (`Quantity__u32`) do not match struct field types (`Quantity__u8`). The assignment performs an implicit narrowing conversion, silently truncating any value above `UINT8_MAX` (e.g., 300 → 44). This is a **Non-Injective Translation** from the parameter domain to the field domain — distinct input values map to the same stored value. The sibling function `initialize_item_stack` correctly uses `Quantity__u8` for both quantity parameters, confirming the struct's **Representation Invariant**.

---

## 2. Impact Assessment

### Callers of `is_p_item_stack__full` (double underscore)

| Caller | File | Coupling |
|--------|------|----------|
| `add_item_to__inventory` | `core/source/inventory/inventory.c` | Uses `is_p_item_stack__full` in a `while` loop to advance past "full" stacks of the same item kind when searching for a slot to add items. |

**Blast radius of correction:** Fixing `is_p_item_stack__full` to exclude empty stacks (adding the `!is_p_item__empty` guard) changes the return value from `true` to `false` for empty stacks (0==0). In `add_item_to__inventory`, this means empty slots of the same item kind will no longer be skipped by the `while` loop. This is **behavior-correcting** — the current broken behavior causes valid empty slots to be skipped, potentially forcing the function into the fallback path (searching for `Item_Kind__None` slots) or failing entirely. The correction aligns with the caller's intent.

### Callers of `is_p_item_stack___full` (triple underscore)

No direct callers found in `core/source`. The function is a `static inline` in the header and may be used by downstream game code (Lavender) that includes `item_stack.h`. The inverted logic means any downstream caller relying on it as "is full" receives the opposite answer.

**Blast radius of correction:** Changing `<` to `>=` inverts the return value for all inputs. Any downstream caller that adapted to the broken behavior (i.e., treated `true` as "has room") would break. This is a **de facto contract** concern: if downstream code was written against the broken semantics, the fix invalidates those assumptions.

### Callers of `set_item_stack`

| Caller | File | Coupling |
|--------|------|----------|
| `copy_item_stack` (inline) | `core/include/inventory/item_stack.h` | Passes `Quantity__u8` field values, which are promoted to `Quantity__u32` and truncated back. No data loss in practice. |
| `add_item_to__inventory` | `core/source/inventory/inventory.c` | Passes `Quantity__u8` parameters. No data loss in practice. |

**Blast radius of correction:** Changing parameter types from `Quantity__u32` to `Quantity__u8` is **behavior-preserving** for all current callers (they already pass `Quantity__u8` values). The change removes the latent truncation hazard without altering any observable behavior for existing call sites.

### Data structures affected

- `Item_Stack` struct (`core/include/defines.h`): fields `quantity_of__items` and `max_quantity_of__items` are `Quantity__u8`. No struct change needed.
- `Inventory` struct: embeds `Item_Stack items[27]`. Indirectly affected through the query functions.

---

## 3. Resolution Assessment

### Fix 1: `is_p_item_stack___full` — correct the comparison operator

**Change:** In `core/include/inventory/item_stack.h`, replace `<` with `>=` in the return expression:

```c
// Before (broken):
return 
    !is_p_item__empty(&p_item_stack->item)
    && p_item_stack->quantity_of__items
    < p_item_stack->max_quantity_of__items;

// After (corrected):
return 
    !is_p_item__empty(&p_item_stack->item)
    && p_item_stack->quantity_of__items
    >= p_item_stack->max_quantity_of__items;
```

**Callers needing update:** None in `core/source`. Downstream (Lavender) callers must be audited — any code that inverted the result to compensate for the bug must be reverted.

**Tests:** New test cases needed (see §4).

---

### Fix 2: `is_p_item_stack__full` — add empty-item guard

**Change:** In `core/include/inventory/item_stack.h`, add the `!is_p_item__empty` guard consistent with the sibling pattern:

```c
// Before (broken):
static inline
bool is_p_item_stack__full(
        Item_Stack *p_item_stack) {
    return p_item_stack->quantity_of__items
        == p_item_stack->max_quantity_of__items;
}

// After (corrected):
static inline
bool is_p_item_stack__full(
        Item_Stack *p_item_stack) {
    return 
        !is_p_item__empty(&p_item_stack->item)
        && p_item_stack->quantity_of__items
        == p_item_stack->max_quantity_of__items;
}
```

**Callers needing update:** `add_item_to__inventory` in `core/source/inventory/inventory.c` — no code change required. The correction makes the `while` loop behave as intended (empty slots are no longer treated as full). The function's **Postcondition** is restored: "Returns true if and only if the stack holds a non-empty item at maximum capacity."

**Tests:** Existing tests (`item_stack__is_full__when_quantity_equals_max`, `item_stack__is_not_full__when_quantity_less_than_max`) remain valid — they use non-empty items. New test needed for the empty-stack boundary case (see §4).

---

### Fix 3: `set_item_stack` — correct parameter types to match struct fields

**Change:** In both the declaration (`core/include/inventory/item_stack.h`) and definition (`core/source/inventory/item_stack.c`), change `Quantity__u32` to `Quantity__u8`:

```c
// Before (broken):
void set_item_stack(
        Item_Stack *p_item_stack,
        Item item,
        Quantity__u32 quantity_of__items,
        Quantity__u32 max_quantity_of__items);

// After (corrected):
void set_item_stack(
        Item_Stack *p_item_stack,
        Item item,
        Quantity__u8 quantity_of__items,
        Quantity__u8 max_quantity_of__items);
```

**Callers needing update:** None. All existing callers (`copy_item_stack`, `add_item_to__inventory`) already pass `Quantity__u8` values. The implicit promotion from `Quantity__u8` to `Quantity__u32` at the call site is eliminated; no value change occurs.

**Tests:** Existing test (`item_stack__set_item_stack__overwrites_contents`) remains valid — it passes values within `u8` range. No new tests strictly required, but a **Boundary Condition** test confirming values at `UINT8_MAX` (255) pass through correctly is recommended.

---

## 4. Test Verification Checklist

### Existing test status

| Test | Function | Status post-fix |
|------|----------|-----------------|
| `item_stack__is_full__when_quantity_equals_max` | `is_p_item_stack__full` | **Passes** (non-empty item, qty==max → true) |
| `item_stack__is_not_full__when_quantity_less_than_max` | `is_p_item_stack__full` | **Passes** (non-empty item, qty<max → false) |
| `item_stack__set_item_stack__overwrites_contents` | `set_item_stack` | **Passes** (values within u8 range) |
| `item_stack__copy_item_stack__copies_contents` | `copy_item_stack`→`set_item_stack` | **Passes** (u8 values, no truncation) |

No existing test asserts on the broken behavior. No existing assertions are invalidated by the fixes.

### New tests required

1. **`is_p_item_stack__full` — empty stack boundary case:**
   - Initialize stack as empty (`initialize_item_stack_as__empty`).
   - Assert `is_p_item_stack__full` returns `false`.
   - **Rationale:** Directly exercises the **Boundary Condition** at (quantity=0, max=0) that the current code fails.

2. **`is_p_item_stack___full` — full stack case:**
   - Initialize stack with non-empty item, quantity == max.
   - Assert `is_p_item_stack___full` returns `true`.
   - **Rationale:** Verifies the corrected `>=` comparison at the equality boundary.

3. **`is_p_item_stack___full` — not-full case:**
   - Initialize stack with non-empty item, quantity < max.
   - Assert `is_p_item_stack___full` returns `false`.
   - **Rationale:** Confirms the inverted logic is corrected.

4. **`is_p_item_stack___full` — empty stack case:**
   - Initialize stack as empty.
   - Assert `is_p_item_stack___full` returns `false`.
   - **Rationale:** Verifies the `!is_p_item__empty` guard short-circuits correctly.

5. **`set_item_stack` — boundary value (255):**
   - Call `set_item_stack` with quantity=255, max=255.
   - Assert stored values equal 255.
   - **Rationale:** **Boundary Condition** at the `UINT8_MAX` edge of the corrected parameter type.

### Test strategy recommendations

- **Property Based Testing:** For `is_p_item_stack__full` and `is_p_item_stack___full`, generate random (item_kind, quantity, max) triples and verify the invariant: "full" is true if and only if (item is non-empty AND quantity >= max [for triple-underscore] or quantity == max [for double-underscore]).
- **Equivalence Check:** After fixing `is_p_item_stack__full`, verify that for all non-empty stacks, its result matches `is_p_item_stack___full` when quantity == max (both should agree at the full boundary for non-empty items).
- **Mutation Testing:** Run the test suite against mutated versions of each fix (e.g., revert `>=` to `>`, remove the empty guard) to confirm the new tests catch regressions.

### Test blast radius: **Low**

All fixes are behavior-correcting, not behavior-changing for valid inputs. No existing test assertions break. New tests are additive only. No phased approach needed for test updates.

---

## 5. Blast Radius Summary

| Metric | Assessment |
|--------|------------|
| Files requiring changes | **3** (`item_stack.h`, `item_stack.c`, test file) |
| Behavior-preserving for current callers? | **Yes** — all current callers pass valid u8 values; query fixes correct semantic errors without altering valid-path behavior |
| Phased approach needed? | **No** — all three fixes are independent, local, and low-risk. They can land in a single change. |
| De facto contracts invalidated? | **Yes** — `is_p_item_stack___full` (triple underscore) has inverted semantics. Any downstream code (Lavender) that compensated for the inversion by negating the result must be updated. This is the highest-risk item. |
| `set_item_stack` signature change | Source-compatible for all core callers. Downstream callers passing literal `u32` constants > 255 would now get a compile-time type mismatch (desirable — surfaces the latent bug). |

### Risk ranking (highest to lowest)

1. **`is_p_item_stack___full`** — Inverted semantics may have been absorbed as a de facto contract by downstream code. Requires downstream audit before or concurrent with the fix.
2. **`is_p_item_stack__full`** — Corrects a boundary condition bug. The `add_item_to__inventory` caller benefits immediately. Low risk.
3. **`set_item_stack`** — Type signature tightening. No behavioral change for current callers. Lowest risk.
