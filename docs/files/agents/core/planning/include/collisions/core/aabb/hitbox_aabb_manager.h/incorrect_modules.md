# Planning: hitbox_aabb_manager — Incorrect Modules

**Review source:** `agents/core/review/include/collisions/core/aabb/hitbox_aabb_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/collisions/core/aabb/hitbox_aabb_manager.h`
- `core/source/collisions/core/aabb/hitbox_aabb_manager.c`
- `tests/core/source/collisions/core/aabb/test_suite_collisions_core_aabb_hitbox_aabb_manager.c`

---

## 1. Problem Identification

### `get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager`

**Defect: Boundary Condition violation — guard checks against compile-time ceiling, not runtime allocation.**

The debug-mode bounds check compares `index_of__hitbox` against `MAX_QUANTITY_OF__HITBOX_AABB` (a compile-time constant of 256) instead of `p_hitbox_aabb_manager->quantity_of__hitboxes` (the runtime field reflecting actual pool allocation). This creates a **State Desync** between the guard's assumed domain and the pool's true allocated size. When the manager is initialized with fewer than 256 hitboxes, indices in `[quantity_of__hitboxes, MAX_QUANTITY_OF__HITBOX_AABB)` pass the guard but index past the end of the heap-allocated array — a **Precondition** violation that manifests as out-of-bounds memory access (undefined behavior).

The sibling function `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` (header, lines 58–70) already implements the correct pattern: it guards against `p_hitbox_aabb_manager->quantity_of__hitboxes`. The pool-access variant simply failed to mirror this.

**Minor defects:**
- Error message on the second `debug_error` call names the wrong function (`get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` instead of `get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager`) — a **Surface-form leakage** from copy-paste.
- Format specifier `%d` used for `Index__u32` (`uint32_t`); should be `%u`.

---

## 2. Impact Assessment

### Callers of the broken function

The function is `static inline` in `hitbox_aabb_manager.c`, limiting visibility to that translation unit. Its sole caller is:

| Caller | File | Coupling to broken behavior |
|--------|------|-----------------------------|
| `allocate_hitbox_aabb_from__hitbox_aabb_manager` | `core/source/collisions/core/aabb/hitbox_abb_manager.c` | Receives `index_of__hitbox` from `poll_for__uuid_collision`, which is already bounded by `quantity_of__hitboxes`. In practice, the caller never passes an out-of-range index, so the broken guard is **not currently triggering** a visible fault. However, the function's **Postcondition** ("returns a valid pointer into the pool") is unsound for indices in the gap. |

### Assumptions invalidated by correcting the guard

- **None of the existing callers will break.** The sole caller already constrains indices to `< quantity_of__hitboxes` via `poll_for__uuid_collision`. Tightening the guard to match this invariant is behavior-preserving for all current call sites.
- **No de facto contract is invalidated.** No external code relies on the ability to index into `[quantity_of__hitboxes, MAX_QUANTITY_OF__HITBOX_AABB)` — that range is never produced by any internal allocator or hash function.
- **Release builds are unaffected** by this specific fix (no guard exists under `NDEBUG`), but the correction makes the debug contract **Conservative** and **Faithful** to the allocation, which is a prerequisite for any future static analysis or assertion tooling.

### Files requiring changes

| File | Change |
|------|--------|
| `core/source/collisions/core/aabb/hitbox_aabb_manager.c` | Fix bounds check, error message string, format specifier (3 edits in one function) |

No header changes required. No other `.c` or `.h` files reference this `static` function.

---

## 3. Resolution Assessment

### Step 1 — Correct the bounds check (Primary fix)

In `get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager`, replace:

```c
if (index_of__hitbox >= MAX_QUANTITY_OF__HITBOX_AABB) {
```

with:

```c
if (index_of__hitbox >= p_hitbox_aabb_manager->quantity_of__hitboxes) {
```

This aligns the **Precondition** with the **Representation Invariant** (pool size == `quantity_of__hitboxes`) and mirrors the sibling function's guard, restoring **Single Source of Truth** for the valid-index domain.

### Step 2 — Fix error message function name

Change the second `debug_error` call's string from:
```
"get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager, index out of bounds, %d/%d"
```
to:
```
"get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager, index out of bounds, %u/%u"
```

### Step 3 — Fix format specifier

Replace `%d/%d` with `%u/%u` (or cast explicitly to `unsigned int`). This ensures correct diagnostic output for the unsigned index type.

### Caller updates

None required. The sole caller (`allocate_hitbox_aabb_from__hitbox_aabb_manager`) already guarantees `index_of__hitbox < quantity_of__hitboxes`.

### Documentation

No public API contract changes. The function remains `static inline` in the `.c` file. No header modification needed.

---

## 4. Test Verification Checklist

### Existing tests

The test file `tests/core/source/collisions/core/aabb/test_suite_collisions_core_aabb_hitbox_aabb_manager.c` is an empty placeholder (contains only a `#warning` directive and an empty suite). No existing assertions to invalidate.

### Required new tests

| Test | Strategy | Description |
|------|----------|-------------|
| In-bounds index returns valid pool pointer | **Equivalence Check** | Allocate manager with N < 256 hitboxes; for each index in `[0, N)`, assert the returned pointer equals `&pool[index]`. |
| Out-of-bounds index (between N and 256) returns null in debug | **Boundary Condition** test | Allocate manager with N = 128; call with index 128. Assert return is `0` (null). This directly exercises the corrected guard. |
| Null manager pointer returns null in debug | **Boundary Condition** test | Call with `NULL` manager. Assert return is `0`. |
| Full pool (N == MAX_QUANTITY) still works | **Equivalence Check** | Verify behavior when the pool is at maximum capacity — the old and new guards coincide, confirming no regression. |

### Blast radius of test changes

- **Low.** Only the empty placeholder test file needs content added. No other test suites reference this `static` function.
- A phased approach is not needed; all four test cases can be added in a single pass.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files modified (source) | 1 (`hitbox_aabb_manager.c`) |
| Files modified (tests) | 1 (empty placeholder → populated) |
| Behavior-preserving for current callers? | **Yes.** Sole caller already constrains index to valid range. |
| De facto contracts invalidated? | **None.** No code depends on the oversized guard. |
| Phased approach needed? | **No.** Single-function, single-file fix with a straightforward test addition. |
| Risk level | **Low.** The change tightens a debug-only assertion to match the actual allocation; it cannot introduce new runtime behavior in release builds. |
