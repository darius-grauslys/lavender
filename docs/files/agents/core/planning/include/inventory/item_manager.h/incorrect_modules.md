# Planning: register_core_items_into__item_manager — Incorrect Modules

**Review source:** `agents/core/review/include/inventory/item_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/inventory/item_manager.h`
- `core/source/inventory/item_manager.c`
- `core/include/inventory/implemented/item_registrar.h`
- `core/source/inventory/implemented/item_registrar.c`
- `core/include/inventory/item.h`
- `core/source/inventory/item.c`
- `core/include/types/implemented/inventory/item_kind.h`
- `core/include/defines_weak.h`
- `core/include/defines.h`
- `core/include/game.h`
- `core/include/world/world.h`
- `core/source/world/world.c`
- `tests/core/source/inventory/test_suite_inventory_item_manager.c`
- `tests/core/include/inventory/test_suite_inventory_item_manager.h`

---

## 1. Problem Identification

### `register_core_items_into__item_manager` — Stub-real divergence

The function `register_core_items_into__item_manager` in `core/source/inventory/item_manager.c`
is a **Stub-real divergence**: its body consists solely of a
`debug_warning("register_core_items_into__item_manager, impl")` call and performs no
registration of core item templates into the `Item_Manager.item_templates` array.

The declared semantic intent — populating `item_templates` with predefined core
items after initialization — is unfulfilled. The function diverges from its real
behavior: it is a no-op that leaves the `Item_Manager` in the same state as
immediately after `initialize_item_manager` (all slots set to `get_item__empty()`).

A companion stub, `register_items` in `core/source/inventory/implemented/item_registrar.c`,
exhibits the same **Stub-real divergence** pattern and is not wired into
`register_core_items_into__item_manager`. Neither function performs any actual
item registration, creating a **Translation Gap** between the declared
registration semantics and the implementation.

**Terminology:** `Stub-real divergence`, `State Desync`, `Translation Gap`
(translation-and-semantics).

---

## 2. Impact Assessment

### Caller: `initialize_world` in `core/source/world/world.c`

`initialize_world()` calls `register_core_items_into__item_manager(get_p_item_manager_from__game(p_game))`
immediately after `initialize_item_manager(...)`. The caller assumes that core
item templates will be present in the `Item_Manager` after this call returns.
Because the function is a no-op:

- The `item_templates` array remains entirely populated with empty/default `Item`
  values (`_item_void`), identical to the post-`initialize_item_manager` state.
- Any downstream code that relies on core item templates being registered
  (e.g., item lookup, crafting, spawning) will find only empty items at every
  `Item_Kind` index.
- The `Item_Kind` enum currently defines only `Item_Kind__None` and
  `Item_Kind__Unknown`, so there are no additional core item kinds to register.
  This means the **Translation Gap** is currently latent — the no-op behavior
  produces no immediately observable failure because no core items exist to
  register. However, this masks the divergence: once core items are added to the
  `Item_Kind` enum, the stub will silently fail to register them, producing a
  **State Desync** between the expected populated state and the actual empty state.

### Data structure: `Item_Manager.item_templates`

The `item_templates` array (`Item item_templates[(u16)Item_Kind__Unknown]`) is the
**Single Source of Truth (SSOT)** for item templates. The
**Representation Invariant** that "all slots contain valid, registered items after
`register_core_items_into__item_manager` completes" is currently unenforced
because the function does nothing.

### Coupling concerns

- `register_item_in__item_manager` (inline in `item_manager.h`) is the correct
  mechanism for writing to `item_templates` and is **Correct** per its review.
  It is currently unused by `register_core_items_into__item_manager`, creating
  **Surface-form leakage** where the registration API exists but the core
  registration path bypasses it.
- The `register_items` function in `item_registrar.c` is intended to be the
  implementation detail behind core item registration, but it is not called,
  creating a **Translation Gap** between the declared dependency (item_registrar)
  and the actual call graph.

**Terminology:** `Single Source of Truth (SSOT)`, `Representation Invariant`,
`Surface-form leakage`, `Translation Gap`, `State Desync`
(translation-and-semantics, design-principles, invariants-and-correctness).

---

## 3. Resolution Assessment

### Step 1: Implement `register_core_items_into__item_manager`

Replace the stub body with actual registration logic. The function should
register a corresponding `Item` template into `item_templates` for each defined
core `Item_Kind`.

- Use `register_item_in__item_manager` (the existing inline registration helper)
  to write each core item template, preserving the **Boundary Condition**
  validation already present in that helper.
- Alternatively, delegate to `register_items(p_item_manager)` from
  `core/source/inventory/implemented/item_registrar.c`, which is the intended
  SSOT for core item definitions.

### Step 2: Implement `register_items` in `item_registrar.c`

The companion stub `register_items` must be implemented to define the actual
core item templates. Currently it also emits only a `debug_warning`. This
function should:

- Construct `Item` instances for each core item kind (via `initialize_item` or
  direct struct initialization).
- Register each into `p_item_manager->item_templates` using
  `register_item_in__item_manager`.

### Step 3: Wire `register_items` into `register_core_items_into__item_manager`

Include `inventory/implemented/item_registrar.h` in `item_manager.c` (or ensure
the include chain reaches it) and call `register_items(p_item_manager)` from
within `register_core_items_into__item_manager`.

### Step 4: Address the `Item_Kind` enum

Currently `Item_Kind` contains only `Item_Kind__None` and `Item_Kind__Unknown`.
The core items to be registered must be defined. Either:

- Extend the `Item_Kind` enum in `core/include/types/implemented/inventory/item_kind.h`
  with additional core item kinds, or
- Register the `Item_Kind__None` item as the sole core item (trivial, since
  `initialize_item_manager` already sets it to empty).

### Step 5: Validate the precondition

Add a `Precondition` check (debug-only, consistent with sibling functions) that
`p_item_manager` is non-null, matching the pattern in
`register_item_in__item_manager` and `get_item_from__item_manager`.

### Caller impact

- `initialize_world` in `world.c` requires no changes — it already calls the
  function correctly. The fix is behavior-preserving for this caller (the call
  site remains valid).
- No other callers of `register_core_items_into__item_manager` exist in the
  codebase.

**Terminology:** `Precondition`, `Boundary Condition`, `Single Source of Truth
(SSOT)`, `Stub-real divergence`, `Surface-form leakage`
(translation-and-semantics, invariants-and-correctness, design-principles).

---

## 4. Test Verification Checklist

### Existing tests

The test suite at `tests/core/source/inventory/test_suite_inventory_item_manager.c`
includes `item_manager.c` directly and tests:

- `item_manager__initialize__all_templates_empty` — asserts all slots are empty
  after `initialize_item_manager`.
- `item_manager__register_and_get__returns_registered_item` — round-trip via
  `register_item_in__item_manager` and `get_item_from__item_manager`.
- `item_manager__get_unregistered__returns_empty` — asserts unregistered slots
  return empty.
- `item_manager__register_overwrites__previous_value` — asserts overwrite
  semantics.

**No existing tests reference `register_core_items_into__item_manager`.** The fix
will not invalidate any existing assertions.

### New tests needed

- **Property Based Testing**: After `register_core_items_into__item_manager`,
  every `Item_Kind` slot in `item_templates` should contain a registered item
  (not the default empty item), verifying the **Representation Invariant**.
- **Round Trip Check**: Register a core item, retrieve it via
  `get_item_from__item_manager`, and verify the retrieved item matches the
  registered template.
- **Equivalence Check**: The post-registration state of `item_templates` should
  differ from the post-`initialize_item_manager` state (i.e., at least one slot
  should have been overwritten with a core item).
- **Boundary Condition**: Verify that
  `register_core_items_into__item_manager` does not write out-of-bounds (i.e.,
  all writes are within `[0, (u16)Item_Kind__Unknown)`).
- **Mutation Testing**: Verify that a mutation which removes a core item
  registration is detected by the test suite.

### Test blast radius

**Low.** No existing tests assert on the behavior of
`register_core_items_into__item_manager` (it is currently untested). New tests
can be added without modifying existing test cases.

**Terminology:** `Property Based Testing`, `Round Trip Check`, `Equivalence
Check`, `Boundary Condition`, `Representation Invariant`, `Mutation Testing`
(testing.md, invariants-and-correctness.md).

---

## 5. Blast Radius Summary

- **Files requiring changes:**
  - `core/source/inventory/item_manager.c` — implement
    `register_core_items_into__item_manager` (replace stub).
  - `core/source/inventory/implemented/item_registrar.c` — implement
    `register_items` (replace stub).
  - `core/include/types/implemented/inventory/item_kind.h` — potentially extend
    `Item_Kind` enum with core item kinds (if not already defined elsewhere).
  - `core/include/inventory/implemented/item_registrar.h` — may need to expose
    additional declarations if `register_items` signature changes.
  - `tests/core/source/inventory/test_suite_inventory_item_manager.c` — add
    tests for `register_core_items_into__item_manager`.

- **Behavior preservation for current callers:** Yes. The sole caller,
  `initialize_world` in `world.c`, invokes the function unconditionally after
  `initialize_item_manager`. Implementing the function adds registration behavior
  without changing the call signature or call site.

- **De facto contracts invalidated:** None. The current no-op behavior is not
  relied upon as a contract — no code depends on `item_templates` remaining empty
  after `register_core_items_into__item_manager`. However, the **State Desync**
  between the declared semantic (core items registered) and actual state (all
  empty) is a latent bug that will manifest once core items are defined.

- **Phased approach:** Not strictly required. The fix is localized to the
  inventory subsystem. However, if extending the `Item_Kind` enum, a phased
  approach (define kinds → implement registrar → wire into item_manager) is
  recommended to avoid intermediate states where the array size changes without
  corresponding registration logic.

**Terminology:** `State Desync`, `Stub-real divergence`, `Single Source of Truth
(SSOT)`, `Representation Invariant` (translation-and-semantics,
design-principles, invariants-and-correctness).
