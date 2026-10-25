# Planning: degree.h — Incorrect Modules

**Review source:** `agents/core/review/include/degree.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/degree.h`
- `core/source/degree.c`
- `core/include/defines.h`
- `core/include/defines_weak.h`
- `core/include/raycast/ray.h`
- `tests/core/source/test_suite_degree.c`
- `tests/core/include/test_suite_degree.h`
- `agents/core/modules/math.md`

---

## 1. Problem Identification

Two functions in the angle-math subsystem were flagged **Incorrect** by review. Both are rooted in the same 9-bit degree system (`Degree__u9` = `uint16_t`, 512 units per revolution, `ANGLE__360` = 512).

### 1.1 `add_angles` — Incorrect mask constant (`core/include/degree.h:25–29`)

`add_angles` is intended to perform modular addition over a full 512-unit circle: `(angle_1 + angle_2) mod 512`. The implementation applies `ANGLE__MASK` as the modulus:

```c
return (angle_1 + angle_2) & ANGLE__MASK;
```

However, `ANGLE__MASK` is defined in `core/include/defines.h:106` as `MASK(5)` (= 31), which preserves only the lowest 5 bits. This wraps the result at 32 (45°) instead of 512 (360°), silently discarding all higher bits for any sum ≥ 32. The correct mask for the 9-bit system is `MASK(9)` (= 511).

This is a **Boundary Condition** defect: the **Postcondition** — that the return lies in `[0, 511]` and equals `(angle_1 + angle_2) mod 512` — is violated. The **Root Cause** is a misconfigured **Representation Invariant**: `ANGLE__MASK` does not match the 9-bit width of the `Degree__u9` type. The sibling `subtract_angles` (`degree.h:34–42`) correctly wraps at `ANGLE__360` (512) via conditional arithmetic and does **not** use `ANGLE__MASK`, making the inconsistency explicit.

Concrete counterexamples (per review):
- `add_angles(ANGLE__90, ANGLE__90)` = `(128+128) & 31` = `0` — should be `ANGLE__180` (256).
- `add_angles(ANGLE__45, ANGLE__45)` = `(64+64) & 31` = `0` — should be `ANGLE__90` (128).

### 1.2 `get_middle_angle` — Incorrect branch logic and missing output mask (`core/source/degree.c:583–590`)

`get_middle_angle` is intended to compute the midpoint of two angles. The implementation uses a value-ordering test (`degree__one < degree__two`) to decide whether to add `ANGLE__360` before halving, but value ordering does not indicate whether the shorter arc crosses the 0/360 boundary:

```c
Degree__u9 get_middle_angle(i32F20 degree__one, i32F20 degree__two) {
    if (degree__one < degree__two)
        return (degree__one + degree__two) >> 1;
    return ((degree__one + degree__two + ANGLE__360) >> 1);
}
```

This is a **Translation Gap** — the implementation does not faithfully translate the semantic intent of "midpoint of the shorter arc." It is also a **State Desync**: the branch condition is **Coupled** to value ordering rather than to the angular distance metric (which should compare the forward distance to `ANGLE__360 / 2` = 256). Additionally, the result is never masked to `[0, 511]`, so it can return `512` (`ANGLE__360`) — an out-of-`Degree__u9` value — for inputs like `degree__one == degree__two == 256`.

There is also a **Mode Confusion**: the parameters are typed `i32F20` (a 20-bit **Fixed-Point** type), but the function performs plain integer arithmetic (`>> 1`), ignoring any fractional component. The intent is integer degree values, not fixed-point.

Concrete counterexamples (per review):
- `degree__one == degree__two`: else-branch always fires, returning `degree__one + 256` instead of `degree__one`.
- `degree__one=200, degree__two=100`: distance is 100 (< 256, no wrap needed), but returns `(200+100+512)>>1 = 406` instead of `150`.
- `degree__one=10, degree__two=400`: distance is 390 (> 256, wrap needed), but returns `(10+400)>>1 = 205` instead of `461`.

---

## 2. Impact Assessment

### 2.1 `add_angles` / `ANGLE__MASK`

**`ANGLE__MASK` usage:** `ANGLE__MASK` is referenced in exactly one location in the entire codebase — `add_angles` (`degree.h:28`). No other file in `./include` or `./source` uses it. Changing `MASK(5)` → `MASK(9)` therefore has a **minimal blast radius** at the constant level.

**`add_angles` callers:** A search across `./core/source/` (game.c, entity/, entity_manager.c, world/, collisions/, raycast/ray.c, scene/, process/, game_action/, vectors.c, debug/, util/) and `./tests/` found **zero callers** of `add_angles`. It is a `static inline` function with no call sites currently in the codebase.

**Downstream consumers of angle values:** The functions that *would* be affected if `add_angles` were used to produce angles for them are:
- `get_2i32F4_offset_from__angle` and `get_2i32F20_offset_from__angle` (`degree.c:572–581`) — both index the 512-entry `__DEGREE_TO_2i32F10__LOOKUP_TABLE` directly with the angle. A correct `add_angles` result in `[0, 511]` is a valid table index; the current broken result in `[0, 31]` is technically in-bounds but semantically wrong. No current caller feeds `add_angles` output into these functions.
- `get_direction_from__angle` (`degree.c:523–546`) — consumes angles via range comparisons and delegates bounds checking to `is_degree_u9__out_of_bounds`. Does not use `add_angles` or `ANGLE__MASK`.
- `get_angle_between__vectors_3i32` (`degree.c:~line 549`) — uses direct addition (`angle + ANGLE__180`, etc.) rather than `add_angles`, so it is **not** coupled to the broken mask.

**De facto contract:** Since `add_angles` has no callers, no code currently relies on the broken wrapping-at-45° behavior as a de facto contract. Correcting the mask will not invalidate any existing assumption in the codebase.

### 2.2 `get_middle_angle`

**Callers:** The review confirms `get_middle_angle` has **no callers** in the codebase. It is not declared in `degree.h` or any other header — it is a non-`static` function defined in `degree.c` with no visible declaration, making it effectively unreachable from other translation units.

**Test coverage:** The degree test suite (`tests/core/source/test_suite_degree.c`) is effectively empty — it contains only a `#warning` directive asking for tests to be written. No assertions exist for either `add_angles` or `get_middle_angle`.

**De facto contract:** Since `get_middle_angle` has no callers and no tests, no code relies on its current (broken) behavior. Correcting it will not invalidate any existing assumption.

---

## 3. Resolution Assessment

### 3.1 `add_angles` — Fix `ANGLE__MASK` constant

**What needs to change:**
- In `core/include/defines.h:106`, change `#define ANGLE__MASK MASK(5)` to `#define ANGLE__MASK MASK(9)`.
- This is the **Single Source of Truth** for the angle mask and the root-cause fix. It makes `add_angles` consistent with `subtract_angles` (both wrap at 512) and with the 9-bit `Degree__u9` type.

**Why fix the constant rather than the function:**
- `ANGLE__MASK` is used only by `add_angles`, so correcting the constant is the minimal, **DRY**-compliant change.
- The `MASK(9)` value (= 511) correctly produces `(angle_1 + angle_2) & 511` ≡ `(angle_1 + angle_2) mod 512` for the 9-bit circle.
- **Static Analysis** confirms no other usage of `ANGLE__MASK` exists.

**Caller updates:** None required — no callers exist.

**Test/Documentation updates:**
- Add tests to `tests/core/source/test_suite_degree.c` for `add_angles` covering:
  - Normal sums within 512 (e.g., `add_angles(ANGLE__45, ANGLE__45)` == `ANGLE__90`).
  - Wrap-around sums (e.g., `add_angles(ANGLE__270, ANGLE__90)` == `ANGLE__0`).
  - Idempotent identity (`add_angles(0, x)` == `x`).
- Use **Property Based Testing** to verify the modular-addition invariant: `add_angles(a, b) == (a + b) & 511` for all `a, b ∈ [0, 511]`.
- Use **Boundary Condition** testing at the wrap boundary (e.g., sums of 511, 512, 513).

### 3.2 `get_middle_angle` — Rewrite branch logic and mask output

**What needs to change:**
- In `core/source/degree.c:583–590`, rewrite `get_middle_angle` to correctly compute the midpoint of the shorter arc:
  1. Compute the forward angular distance: `diff = (degree__two - degree__one) & 511` (modular difference).
  2. If `diff <= 256` (half-circle), the shorter arc does not cross 0/360: midpoint = `(degree__one + degree__two) >> 1` (no wrap offset).
  3. If `diff > 256`, the shorter arc crosses 0/360: midpoint = `((degree__one + degree__two + 512) >> 1) & 511`.
  4. Always mask the final result to `[0, 511]` to enforce the **Representation Invariant**.
- Change parameter types from `i32F20` to `Degree__u9` to resolve the **Mode Confusion** and align with the rest of the `degree.h` API (e.g., `add_angles`, `subtract_angles` both take `Degree__u9`).
- Add a forward declaration to `core/include/degree.h` so the function is part of the public API (it is currently defined in `degree.c` but undeclared anywhere).

**Caller updates:** None required — no callers exist.

**Test/Documentation updates:**
- Add tests for `get_middle_angle` covering:
  - Equal inputs (midpoint == input).
  - Inputs on the same side of 0 (no wrap).
  - Inputs straddling 0/360 (wrap needed).
  - Use **Round Trip Check**: `get_middle_angle(a, b)` should return a value `m` such that `m` lies on the shorter arc between `a` and `b`.
  - Use **Property Based Testing** to verify the midpoint invariant for all angle pairs.
  - Use **Boundary Condition** testing at the half-circle boundary (diff == 256).
  - Use **Fuzzing** to explore edge cases around the 0/360 boundary.

---

## 4. Test Verification Checklist

**Existing test coverage:**
- `tests/core/source/test_suite_degree.c` — **empty**. Contains only a `#warning` directive. No tests exist for `add_angles`, `get_middle_angle`, or any other degree function.
- `tests/core/include/test_suite_degree.h` — declares the suite but contains no test cases.

**Test impact assessment:**
- **Blast radius: Low.** No existing tests assert on either function's behavior (none exist). No existing assertions will be invalidated by the fixes.
- New tests are required for both functions. A phased approach is recommended:
  1. **Phase 1:** Fix `add_angles` by correcting `ANGLE__MASK` → `MASK(9)`. Add property-based and boundary tests.
  2. **Phase 2:** Rewrite `get_middle_angle` with correct branch logic, output masking, and type correction. Add round-trip, property-based, and fuzzing tests.

**Recommended test strategies (per `agents/terminologies/testing.md`):**
- **Property Based Testing** — verify `add_angles(a, b) == (a + b) mod 512` and `get_middle_angle(a, b)` lies on the shorter arc.
- **Round Trip Check** — verify midpoint symmetry: `get_middle_angle(a, b) == get_middle_angle(b, a)`.
- **Boundary Condition** testing — sums/diffs at 256, 511, 512; equal inputs; antipodal inputs.
- **Fuzzing** — random angle pairs to catch edge cases around the 0/360 wrap.
- **Mutation Testing** — after implementation, mutate the mask constant or branch condition to verify the test suite catches regressions.

---

## 5. Blast Radius Summary

| Aspect | `add_angles` / `ANGLE__MASK` | `get_middle_angle` |
|---|---|---|
| Files changed | 2 (`defines.h`, `test_suite_degree.c`) | 2 (`degree.c`, `test_suite_degree.c`) + 1 (`degree.h` for declaration) |
| Behavior-preserving for callers? | N/A — no callers exist | N/A — no callers exist |
| De facto contracts invalidated | None | None |
| Phased approach needed? | No — single constant fix | Yes — type change + logic rewrite |
| Test impact | Low — new tests only | Low — new tests only |

**Overall blast radius: Low.** Both functions are currently unused (zero callers) and untested. The `add_angles` fix is a single constant change (`MASK(5)` → `MASK(9)`) with no downstream ripple. The `get_middle_angle` fix requires a logic rewrite, a type correction (`i32F20` → `Degree__u9`), and a new header declaration, but since no code calls it, no existing behavior is disrupted.
