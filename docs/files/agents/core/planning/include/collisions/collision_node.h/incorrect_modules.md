# Planning: `collision_node.h` — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/collision_node.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/collision_node.h` (function at lines 55–60)
- `core/source/collisions/collision_node.c`
- `core/source/collisions/collision_node_pool.c`
- `core/include/world/global_space.h` (sibling null-safe pattern, lines 46–53)
- `core/include/serialization/serialization_header.h` (callee + `IS_DEALLOCATED_P__u64`)
- `tests/core/source/collisions/test_suite_collisions_collision_node.c`

---

## 1. Problem Identification

### `is_collision_node__allocated` (`core/include/collisions/collision_node.h`, lines 55–60)

**Correctness Verdict: Incorrect**

The function is a `Pure`, `Referentially Transparent` query reporting whether a
`Collision_Node` is in a live (allocated) state. Its **Precondition** states that
`p_collision_node` is a non-null pointer to a valid `Collision_Node`.

**Core defect — missing null guard (null pointer dereference / UB):**
The implementation dereferences `p_collision_node` unconditionally via
`&p_collision_node->_serialization_header` before any null check is possible:

```c
static inline
bool is_collision_node__allocated(
        Collision_Node *p_collision_node) {
    return !is_serialized_struct__deallocated__uuid_64(
            &p_collision_node->_serialization_header);
}
```

If `p_collision_node == NULL`, the address-of-member expression
`&p_collision_node->_serialization_header` dereferences a null pointer, invoking
**undefined behavior**. A `Conservative` `Static Analysis` pass should flag this as a
`Boundary Condition` violation of the stated `Precondition`.

**Inconsistency with established pattern:**
The sibling `is_global_space__allocated` (`core/include/world/global_space.h`,
lines 46–53) guards with `p_global_space &&` before dereferencing. The codebase
also offers a null-safe `Single Source of Truth (SSOT)` idiom via the
`IS_DEALLOCATED_P__u64` macro (`serialization_header.h`, lines 37–39), which
short-circuits on `!serialized_header`. `is_collision_node__allocated` follows
neither, so it is `Coupled` only to a non-null assumption it does not enforce.

**Dead callee guard:**
The delegate `is_serialized_struct__deallocated__uuid_64`
(`serialization_header.h`, lines 173–179) contains `!p_serialization_header ||`,
but the argument passed is `&p_collision_node->_serialization_header` — the
address-of a struct member, always non-null when `p_collision_node` is non-null.
That callee guard is therefore **dead code** in this call path; the only protection
against a null `p_collision_node` must reside in `is_collision_node__allocated`.

**Type compatibility — correct.** `&p_collision_node->_serialization_header`
yields `Serialization_Header__UUID_64 *`, matching the callee parameter exactly.
No other UB (no pointer arithmetic, type punning, or out-of-bounds access).

## 2. Impact Assessment

### Direct callers in `./include` and `./source`

A survey of every translation unit that includes `collision_node.h`
(`collision_node.c`, `collision_node_pool.c`, `world.c`) shows that
**`is_collision_node__allocated` has no direct production callers**. The de facto
allocation check in this module is the null-safe `IS_DEALLOCATED_P__u64` macro,
used at `collision_node_pool.c` line 83:

```c
if (!IS_DEALLOCATED_P__u64(p_collision_node)) {
    debug_error("allocate_collision_node_from__collision_node_pool, uuid already in use.");
    return 0;
}
```

That macro already short-circuits on `!serialized_header`, so the live allocation
path is **not** affected by the bug in `is_collision_node__allocated`.

### Test callers

`tests/core/source/collisions/test_suite_collisions_collision_node.c` references
the function at lines 37 and 54. Both call sites pass a **valid, non-null** pointer
(`&node`). No test currently exercises the null-input path, so the defect is
uncovered by the suite.

### Assumptions coupled to the broken behavior

- No production code relies on the broken behavior; the null-deref UB is latent.
- The function is a `static inline` in a public header, forming part of the inline
  API **contract**. Any future caller passing a potentially-null
  `Collision_Node *` (the natural defensive posture given
  `is_global_space__allocated` sets the precedent) would be exposed to the UB.
- The function's **Postcondition** (true for valid UUIDs, false for the
  `IDENTIFIER__UNKNOWN__u64` sentinel) is already semantically correct; only the
  null-input case is mishandled. Adding the guard therefore **does not invalidate**
  any existing assumption — it strengthens the `Representation Invariant` of the
  query while leaving the truth table for non-null inputs unchanged.

## 3. Resolution Assessment

### Plan

Add a null guard `p_collision_node &&` before the dereference, mirroring the
`is_global_space__allocated` pattern. This enforces the stated `Precondition` and
makes the function `Conservative` under `Static Analysis`.

**Corrected implementation** (`core/include/collisions/collision_node.h`, lines 55–60):

```c
static inline
bool is_collision_node__allocated(
        Collision_Node *p_collision_node) {
    return p_collision_node
        && !is_serialized_struct__deallocated__uuid_64(
                &p_collision_node->_serialization_header);
}
```

### Per-issue resolution steps

| Item | Implementation change | Callers | Tests / Docs |
|------|-----------------------|---------|--------------|
| `is_collision_node__allocated` | Add `p_collision_node &&` guard before dereference | None (no production callers); no caller updates required | Add a null-input test; existing non-null assertions remain valid (see §4) |

### Notes

- **No phased approach required.** The change is a single-line guard with minimal
  blast radius and no behavioral change for non-null inputs, preserving
  `Referential Transparency` and the existing `Postcondition`.
- Optional follow-up `Refactoring` (out of scope): migrate `collision_node_pool.c`
  line 83 to use `!is_collision_node__allocated(p_collision_node)` instead of the
  raw `IS_DEALLOCATED_P__u64` macro, so allocation-status logic per struct type has
  a single `Single Source of Truth (SSOT)`, consistent with
  `is_global_space__allocated`.

## 4. Test Verification Checklist

Surveyed `tests/core/source/collisions/test_suite_collisions_collision_node.c`:

- **Existing assertions are behavior-preserving.** All current call sites
  (`collision_node__initialize__sets_uuid` line 37,
  `collision_node__is_allocated__false_when_deallocated` line 54) pass valid,
  non-null pointers and assert on the correct truth table. The added guard is a no-op
  for non-null inputs, so **no existing assertion is invalidated** — this is a clean
  `Equivalence Check` for the non-null path.
- **New test required (null input).** Add a case asserting
  `is_collision_node__allocated(NULL)` returns `false` and does not crash/UB. This
  converts the previously-uncovered `Boundary Condition` into an asserted invariant.
- **Recommended strategies** (from `agents/terminologies/testing.md`):
  - `Property Based Testing`: for all UUID values,
    `is_collision_node__allocated(node) == (uuid != IDENTIFIER__UNKNOWN__u64)`.
  - `Fuzzing`: feed random/edge UUIDs and a null pointer to confirm the guard
    holds across the full input space.
- **Blast radius of test changes: Low.** Add one null-input case; no existing tests
  need modification. No phased approach needed.

## 5. Blast Radius Summary

- **Files changed:** 1 (`core/include/collisions/collision_node.h`) + 1 test file
  (`tests/core/source/collisions/test_suite_collisions_collision_node.c`).
- **Behavior-preserving for current callers:** Yes — no production callers exist, and
  the guard is a no-op for all non-null inputs.
- **Phased approach:** Not needed; single-line fix.
- **De facto contracts invalidated:** None. The null-safe `IS_DEALLOCATED_P__u64`
  macro and `is_global_space__allocated` remain the established contracts; this fix
  only aligns `is_collision_node__allocated` with them, reducing `Spaghettification`
  of the allocation-check idiom.
