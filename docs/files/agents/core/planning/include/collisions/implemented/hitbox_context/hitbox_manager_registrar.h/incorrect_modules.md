# Planning: `hitbox_manager_registrar.h` — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/implemented/hitbox_context/hitbox_manager_registrar.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/implemented/hitbox_context/hitbox_manager_registrar.h`
- `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c`
- `core/include/collisions/hitbox_context.h`
- `core/source/collisions/hitbox_context.c`
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/include/vectors.h`
- `core/include/numerics.h`
- `core/include/collisions/core/aabb/hitbox_aabb_manager.h`
- `core/source/collisions/core/aabb/hitbox_aabb_manager.c`
- `core/include/collisions/core/aabb/hitbox_aabb.h`
- `core/include/game_action/core/hitbox/game_action__hitbox.h`
- `core/source/game_action/core/hitbox/game_action__hitbox.c`
- `core/include/game_action/core/hitbox/game_action__hitbox__aabb.h`
- `tests/core/source/collisions/implemented/hitbox_context/test_suite_collisions_implemented_hitbox_context_hitbox_manager_registrar.c`
- `tests/core/source/collisions/test_suite_collisions_hitbox_context.c`

---

## 1. Problem Identification

### Incorrect Module: `register_hitbox_managers`

**File of origin:** `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c`, lines 7–32

**Correctness Verdict:** Incorrect

**Core defect — `Translation Gap` between the fixed-point type and its declared metadata:**

The function registers the `Hitbox_AABB_Manager` by delegating to
`register_hitbox_manager`, supplying component metadata that describes the
AABB hitbox's fixed-point data layout. The `fractional_percision_of__acceleration`
parameter is passed as `FRACTIONAL_PERCISION_16__BIT_SIZE` (value 16), but the
actual type backing acceleration components is `i16F8`.

Per the codebase naming convention, the `F8` suffix denotes 8 fractional bits
(e.g., `i32F4` = `int32_t` with 4 fractional bits). This is confirmed by the type
definitions:

- `i16F8` is `typedef int16_t i16F8;` — **8 fractional bits**
  (`core/include/defines_weak.h:40`)
- `Vector__3i16F8` is a struct of three `i16F8` components
  (`core/include/defines_weak.h:95–97`)
- `Hitbox_AABB.acceleration__3i16F8` is of type `Vector__3i16F8`
  (`core/include/defines.h:454`)

The correct macro `FRACTIONAL_PERCISION_8__BIT_SIZE` (value 8) is defined at
`core/include/defines.h:49` and is available at the call site, but the wrong
macro (`FRACTIONAL_PERCISION_16__BIT_SIZE`, value 16, defined at
`core/include/defines.h:51`) is used instead.

This is a **Representation Invariant** violation: the registration record stores
metadata that does not match the actual in-memory representation of the
acceleration component. The `Postcondition` that
`fractional_percision_of__acceleration` equals the true fractional bit-width of
`i16F8` is not met.

---

## 2. Impact Assessment

### Data flow

1. `register_hitbox_managers` (`hitbox_manager_registrar.c:11`) calls
   `register_hitbox_manager` (`hitbox_context.c:19`).
2. `register_hitbox_manager` writes the `fractional_percision_of__acceleration`
   argument into `Hitbox_Manager_Registration_Record.fractional_percision_of__acceleration`
   (`hitbox_context.c:70–71`).
3. The record is stored in
   `Hitbox_Context.hitbox_manager_registration_records[Hitbox_Manager_Type__AABB]`
   (`defines.h:446–447`).

### Current consumers of the broken field

A search of `./include` and `./source` confirms that
`fractional_percision_of__acceleration` is **write-only** at present — no code path
reads it from the registration record. The actual data-access path bypasses the
registration record entirely:

- `opaque_access_to__hitbox` (`hitbox_context.c`) dispatches through the
  `hitbox_manager_instance__invocation_table` (function pointers), not the
  registration record.
- `f_hitbox_manager__opaque_property_access_of__hitbox_AABB`
  (`hitbox_aabb_manager.c`) operates on the concrete `Vector__3i16F8` type
  directly, using hardcoded shift constants (`FRACTIONAL_PERCISION_4__BIT_SIZE`
  in `vectors.h` conversion helpers) rather than reading the registration record.
- `m_process__game_action__hitbox` (`game_action__hitbox.c`) and
  `m_process__game_action__hitbox__aabb` (`game_action__hitbox__aabb.h`) consume
  acceleration via the concrete `Vector__3i16F8` type and the `Vector__3i16F8`
  conversion helpers in `vectors.h`, which use `FRACTIONAL_PERCISION_4__BIT_SIZE`
  for cross-type conversion (a separate, pre-existing concern not in scope here).

### How correcting the value invalidates coupled assumptions

Because the field is currently write-only, **no existing caller relies on the
broken value (16) as a de facto contract**. Correcting it to 8 does not alter any
current runtime behavior. However, the fix **invalidates the latent assumption**
that the registration record is a faithful description of component layout. Any
future consumer that reads `fractional_percision_of__acceleration` to derive
fixed-point shift amounts (e.g., a generic serializer, a generic property
accessor, or a `Static Analysis`-driven code generator) would currently compute
incorrect scaling factors (shifting by 2^16 instead of 2^8). Correcting the value
restores the **Representation Invariant** so that such future consumers behave
correctly.

### Affected portions of `./include` and `./source`

| File | Role | Reliance on broken behavior |
|------|------|-----------------------------|
| `core/include/defines.h` | Defines `Hitbox_Manager_Registration_Record`, `Hitbox_Context`, `FRACTIONAL_PERCISION_*__BIT_SIZE` macros, `Hitbox_AABB` (with `acceleration__3i16F8`) | The `Representation Invariant` of the record is violated. The struct layout and macro definitions are correct; only the *value written* is wrong. |
| `core/include/defines_weak.h` | Defines `i16F8` (= `int16_t`, 8 fractional bits) and `Vector__3i16F8` | Source of truth for the correct fractional precision (8). No change needed. |
| `core/include/collisions/hitbox_context.h` | Declares `register_hitbox_manager` signature | The function signature accepts `u8 fractional_percision_of__acceleration`; no validation of the value. No change needed. |
| `core/source/collisions/hitbox_context.c` | Implements `register_hitbox_manager` (writes the record) and `initialize_hitbox_context` (calls `register_hitbox_managers`) | Writes the incorrect value verbatim into the record. No change needed in this file — the fix is at the call site. |
| `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c` | Defines `register_hitbox_managers` (the call site) | **The bug lives here.** The fix is a single macro substitution. |
| `core/include/collisions/core/aabb/hitbox_aabb_manager.h` | Declares AABB manager functions | No reliance on the registration record's fractional precision. |
| `core/source/collisions/core/aabb/hitbox_aabb_manager.c` | Implements `f_hitbox_manager__opaque_property_access_of__hitbox_AABB` | Uses concrete `Vector__3i16F8` type directly; does not read the registration record. |
| `core/include/vectors.h` | Defines `Vector__3i16F8` conversion helpers | Uses hardcoded `FRACTIONAL_PERCISION_4__BIT_SIZE` for `i16F8`↔`i32F4` conversion (pre-existing, out of scope). |
| `core/include/numerics.h` | Defines fixed-point conversion functions | No reliance on the registration record. |
| `core/include/game_action/core/hitbox/game_action__hitbox.h` | Declares `m_process__game_action__hitbox` | No reliance on the registration record. |
| `core/source/game_action/core/hitbox/game_action__hitbox.c` | Implements hitbox game-action dispatch | Uses concrete `Vector__3i16F8` type; does not read the registration record. |
| `core/include/game_action/core/hitbox/game_action__hitbox__aabb.h` | Implements AABB hitbox game-action processing | Uses concrete `Vector__3i16F8` type; does not read the registration record. |
| `tests/core/source/collisions/implemented/hitbox_context/test_suite_collisions_implemented_hitbox_context_hitbox_manager_registrar.c` | Test suite for the registrar | Currently empty (only a `#warning` and `DEFINE_SUITE` with `END_TESTS`). No assertions on the broken behavior. |
| `tests/core/source/collisions/test_suite_collisions_hitbox_context.c` | Test suite for `hitbox_context` | Contains a stub test `register_hitbox_manager__populates_invocation_table_and_record` (`END_TEST` — no assertions). No reliance on the broken value. |

### Assumptions coupled to the broken behavior

No code relies on the value 16 as a de facto contract. The field is currently
write-only. The fix is therefore **behavior-preserving** for all existing callers
and removes a latent correctness hazard for future consumers.

---

## 3. Resolution Assessment

### Plan

**Step 1 — Correct the fractional precision macro (primary fix)**

In `core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c`,
line 30, replace `FRACTIONAL_PERCISION_16__BIT_SIZE` with
`FRACTIONAL_PERCISION_8__BIT_SIZE`:

```c
// Before (incorrect):
FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(
    acceleration,
    FRACTIONAL_PERCISION_16__BIT_SIZE)

// After (correct):
FRACTIONAL_PERCISION_OF__HITBOX_COMPONENTS(
    acceleration,
    FRACTIONAL_PERCISION_8__BIT_SIZE)
```

This restores the **Representation Invariant**: the registration record's
`fractional_percision_of__acceleration` field will correctly reflect the 8
fractional bits of the `i16F8` type, matching the pattern already established
for the other two components (`FRACTIONAL_PERCISION_0__BIT_SIZE` for `i32`
dimensions, `FRACTIONAL_PERCISION_4__BIT_SIZE` for `i32F4` pos/vel).

### Caller impact

- **No callers need updating.** `register_hitbox_managers` is the sole producer of
  this field value, and no code currently consumes it. The fix is a
  **Conservative**, single-line, behavior-preserving change for all existing call
  paths.
- `register_hitbox_manager` (`hitbox_context.c`) stores the argument verbatim; it
  requires no change.
- `initialize_hitbox_context` (`hitbox_context.c:14`) calls
  `register_hitbox_managers` and is unaffected.

### Test impact

- The existing test suite for the registrar
  (`test_suite_collisions_implemented_hitbox_context_hitbox_manager_registrar.c`)
  is empty — it contains only a `#warning` and a `DEFINE_SUITE` with `END_TESTS`.
- The `hitbox_context` test suite
  (`test_suite_collisions_hitbox_context.c`) has a stub test
  `register_hitbox_manager__populates_invocation_table_and_record` with no
  assertions (`END_TEST`).
- **No existing assertions need updating** — none assert on the broken value.

**Recommended new tests** (using terminology from `agents/terminologies/testing.md`):

1. **`Property Based Testing`** — Add a test that calls
   `register_hitbox_managers` on a zero-initialized `Hitbox_Context` and asserts
   that
   `p_hitbox_context->hitbox_manager_registration_records[Hitbox_Manager_Type__AABB]
   .fractional_percision_of__acceleration == 8`. This verifies the
   **Representation Invariant** directly.
2. **`Equivalence Check`** — Assert that the registered
   `fractional_percision_of__acceleration` matches the fractional bit-width implied
   by the type name (`i16F8` → 8), the registered
   `size_of__components__acceleration` matches `sizeof(i16F8)` (2), and the
   registered `quantity_of__components__pos_vel_acc` matches the component count
   of `Vector__3i16F8` (3). This cross-checks metadata against the concrete types.
3. **`Round Trip Check`** — Verify that registering and then reading back all
   eight metadata fields of the `Hitbox_Manager_Registration_Record` yields the
   expected values, ensuring no **State Desync** between the call site and the
   stored record.

### Documentation impact

- No documentation changes required. The function's documented `Postcondition`
  (see `register_hitbox_managers.md` review) already states the intended value;
  the fix brings the implementation into alignment.

### Blast radius

- **1 file changed** (`hitbox_manager_registrar.c`), **1 line**.
- **Behavior-preserving** for all existing callers (the field is currently
  write-only).
- **No de facto contracts invalidated** — no code reads the field today.
- **No phased approach needed.**

---

## 4. Test Verification Checklist

### Survey of existing tests

| Test file | References to `register_hitbox_managers` / fractional precision? | Assertions on broken value? |
|-----------|------------------------------------------------------------------|-----------------------------|
| `test_suite_collisions_implemented_hitbox_context_hitbox_manager_registrar.c` | No (empty stub) | No |
| `test_suite_collisions_hitbox_context.c` | Yes — stub `register_hitbox_manager__populates_invocation_table_and_record` | No (empty `END_TEST`) |
| `test_suite_collisions_core_aabb_hitbox_aabb_manager.c` | No | No |

### New tests needed

- **`Property Based Testing`**: Assert
  `fractional_percision_of__acceleration == FRACTIONAL_PERCISION_8__BIT_SIZE`
  after registration. This is the direct verification of the **Invariant**.
- **`Equivalence Check`**: Cross-check all three fractional precision fields
  against their corresponding type suffix (`i32` → 0, `i32F4` → 4, `i16F8` → 8)
  and size fields against `sizeof()`.
- **`Round Trip Check`**: Register, then read back all fields from the
  registration record to confirm no **State Desync**.

### Test blast radius

- **Low.** No existing tests assert on the broken value. The fix is
  behavior-preserving. New tests can be added incrementally without a phased
  approach.

---

## 5. Blast Radius Summary

- **Files needing changes:** 1 (`core/source/collisions/implemented/hitbox_context/hitbox_manager_registrar.c`)
- **Behavior-preserving for current callers?** Yes — the `fractional_percision_of__acceleration` field is currently write-only; no code reads it.
- **Phased approach needed?** No — single-line, surgical macro substitution.
- **De facto contracts invalidated?** None — no consumer relies on the value 16.
