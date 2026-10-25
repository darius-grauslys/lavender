# Planning: camera.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/camera.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/camera.h` (holds the flagged `static inline` function)
- `core/source/world/camera.c` (initialization / active-query context)
- `core/include/defines_weak.h` (`Quantity__u32`, `Vector__3i32` type definitions)
- `tests/core/source/world/test_suite_world_camera.c` (existing coverage)

**Flagged function:**
- `is_position_within__camera_fulcrum(Camera *p_camera, Vector__3i32 position)` — **Incorrect**

---

## 1. Problem Identification

`is_position_within__camera_fulcrum` is a `static inline` predicate declared in
`core/include/world/camera.h`. Its name and documented **Postcondition** state it
should return `true` when `position` lies **within** the camera's fulcrum area
(half the fulcrum width/height, expanded by a 16-unit margin). The implementation
is semantically inverted relative to that intent — a `Mode Confusion` between the
"within" and "outside" modes, and a `Non-Injective Translation` of the intended
predicate into code:

```c
return (abs(position.x__i32 - camera_position__3i32.x__i32)
        > p_camera->width_of__fulcrum / 2 + 16
    || abs(position.y__i32 - camera_position__3i32.y__i32)
        > p_camera->height_of__fulcrum / 2 + 16);
```

- **Inverted relational operators + wrong boolean connective.** `>` combined with
  `||` yields `true` when the position is **outside** the fulcrum in *either* axis.
  The correct "within" predicate requires `<` combined with `&&` (inside in *both*
  axes). As written, the predicate is the logical complement of its name — a clear
  `Surface-form leakage`: the identifier promises "within" while the body computes
  "outside".

Secondary defects observed in the same function:

- **Signed/unsigned `Mode Confusion` (type mismatch).** `abs()` returns `int`
  (signed); `p_camera->width_of__fulcrum / 2 + 16` is `Quantity__u32`
  (`uint32_t`). The comparison promotes the signed operand to unsigned. Harmless in
  practice (absolute values are non-negative) but it defeats `Static Analysis` and
  emits compiler warnings.
- **Missing `Precondition` guard.** The function dereferences `p_camera` and reads
  the fulcrum fields with no null check and no out-of-bounds check. In particular,
  `initialize_camera_as__inactive()` stores the sentinel `QUANTITY__UNKNOWN__u32` in
  the fulcrum fields; feeding an inactive camera into this predicate computes against
  a garbage sentinel rather than failing safely.
- **Magic number.** The margin literal `16` is unnamed (acknowledged by the
  `//TODO: magic number the 16` comment) — a `DRY` / Single Source of Truth (SSOT)
  violation.
- **Signed overflow risk.** `position.x__i32 - camera_position__3i32.x__i32` can
  overflow for large opposite-sign `int32_t` operands before `abs()` is applied.

---

## 2. Impact Assessment

**Current coupling is minimal — the broken behavior is not yet a de facto contract.**

- **No production callers.** The predicate is `static inline`, so it is only visible
  to translation units that `#include <world/camera.h>`. A survey of the likely
  consumers found no call sites:
  - `core/source/rendering/graphics_window.c` — no reference.
  - `sdl/source/rendering/sdl_render_world.c`, `sdl/source/rendering/opengl/gl_render_world.c` — no reference.
  - `nds/source/rendering/nds_rendering__world.c` — no reference.
  - The in-source comment `//TODO: use this in render_entity.c in NDS` confirms the
    function was authored for a **future** NDS entity-culling path that does not yet
    exist (`render_entity.c` is absent; only its review stub is present).
- **No test coupling.** `tests/core/source/world/test_suite_world_camera.c` covers
  `initialize_camera_as__inactive`, `initialize_camera`, `is_camera__active`,
  `set_camera_to__follow`, and `get_position_3i32F4_of__camera` — but **not**
  `is_position_within__camera_fulcrum`. No existing assertion depends on the broken
  behavior.

**How correction invalidates coupled assumptions:**

- Because no caller or test consumes the value today, flipping the predicate from
  "outside" to "within" invalidates **nothing** currently compiled or asserted.
  Blast radius is confined to a single file (`camera.h`).
- **The risk is forward-looking, not present.** The intended consumer (NDS
  `render_entity.c`) will use this predicate to *cull* entities — i.e., render only
  those reported "within" the fulcrum. If the inverted logic shipped, the culler
  would keep exactly the off-screen entities and drop the on-screen ones: a
  `Cascade Failure` across the render pass (blank/incorrect world). The fix must land
  **before** that consumer is wired in.
- **Sentinel coupling.** Correcting the predicate should also enforce the
  `Precondition` that the camera be active and its fulcrum fields in-bounds, so it
  aligns with `is_camera__active()` (which already rejects `QUANTITY__UNKNOWN__u32`).
  This removes a latent `Representation Invariant` mismatch: two functions currently
  disagree about what a valid fulcrum is.

---

## 3. Resolution Assessment

All changes are local to `core/include/world/camera.h`. No caller updates are needed
(none exist). A single, non-phased change is sufficient.

### 3.1 Fix the predicate (primary)
Rewrite the return expression so it is `Faithful` to the "within" intent:

```c
return (abs(position.x__i32 - camera_position__3i32.x__i32)
        < p_camera->width_of__fulcrum / 2 + CAMERA__FULCRUM__MARGIN
    && abs(position.y__i32 - camera_position__3i32.y__i32)
        < p_camera->height_of__fulcrum / 2 + CAMERA__FULCRUM__MARGIN);
```

- Switch `>` → `<` and `||` → `&&` so the result is the exact complement of the
  current (inverted) behavior.

### 3.2 Enforce the Precondition (Conservative guard)
Guard the `Boundary Condition` / invalid-state cases before computing:

```c
if (!p_camera || !is_camera__active(p_camera)) {
    return false;   // Conservative: out-of-bounds sentinel or null ⇒ "not within"
}
```

This makes the predicate safe against `initialize_camera_as__inactive()` sentinels and
null inputs, and keeps it consistent with `is_camera__active()`.

### 3.3 Remove the magic number (SSOT / DRY)
Define a named constant, e.g. `#define CAMERA__FULCRUM__MARGIN 16` (or a `static const`),
and reference it in both axes. Delete the `//TODO: magic number the 16` comment.

### 3.4 Resolve the type mismatch
Compute both sides of each comparison in a common, well-defined signed type (e.g., cast
the fulcrum expression to `int32_t`/`int64_t`) so no signed→unsigned promotion occurs and
`Static Analysis`/lint stays clean.

### 3.5 Guard signed overflow
Compute the axis delta in a wider integer (e.g., `int64_t`) before `abs()`, or bound the
comparison, so opposite-sign extremes cannot overflow `int32_t`.

### 3.6 Tests (see checklist below)
Add coverage to `tests/core/source/world/test_suite_world_camera.c`, which currently has
none for this function.

---

## 4. Test Verification Checklist

**Existing suite:** `test_suite_world_camera.c` contains **no** test for
`is_position_within__camera_fulcrum`. Therefore no existing assertion is invalidated by
the fix, and the fix is currently unverified in both directions. New tests are required.

**Recommended new tests (terminology-guided):**

- **Equivalence Check** — the corrected `within` result must be the exact logical
  complement of the current (pre-fix) expression for a grid of positions; guarantees the
  inversion is a clean flip, not a partial change.
- **Property Based Testing** — for random `position` and fulcrum sizes, assert the
  `Boundary Condition` invariant: `within` ⇔ both axis deltas are strictly `<`
  half-dimension + margin. Confirms the `<`/`&&` shape holds generally.
- **Boundary cases** — positions at exactly `half + margin - 1`, `half + margin`, and
  `half + margin + 1` along each axis, plus a corner where only one axis exceeds (must be
  `false`) and a fully interior point (must be `true`).
- **Precondition / sentinel** — pass a null camera and an
  `initialize_camera_as__inactive()` camera (sentinel fulcrum); assert `false` (Conservative).
- **Overflow** — feed large opposite-sign `int32_t` coordinates; assert no UB and a sane
  `false`.
- **Fuzzing** (optional, later) — random `(position, width, height)` triples to stress the
  margin/overflow edges.

**Blast radius of tests:** Low. One test file gains new cases; nothing existing changes.

---

## 5. Blast Radius Summary

- **Files changed:** 1 (`core/include/world/camera.h`) + 1 test file
  (`tests/core/source/world/test_suite_world_camera.c`).
- **Behavior-preserving for current callers:** N/A — there are no current callers and no
  existing tests; the change is safe to land immediately.
- **Phased approach needed:** No. Single-function, single-file edit plus additive tests.
- **De facto contracts invalidated:** None today. The only real constraint is sequencing:
  the corrected (non-inverted) predicate must be in place **before** the planned NDS
  `render_entity.c` culling consumer is introduced, so it never inherits the inverted
  "outside" semantics.
