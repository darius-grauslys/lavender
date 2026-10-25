# Planning: chunk_pool.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/chunk_pool.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/chunk_pool.h`
- `core/source/world/chunk_pool.c`
- `tests/core/source/world/test_suite_world_chunk_pool.c`

---

## 1. Problem Identification

**Flagged function:** `get_chunk_at__index_from__chunk_pool`

**Defect:** **Translation Gap.** The spec layer expects a public API accessor that retrieves a `Chunk*` from a `Chunk_Pool` by zero-based index, with bounds-checked behavior (returning `NULL` on out-of-bounds in debug builds). No such function is declared in `core/include/world/chunk_pool.h` nor implemented as an externally-linked symbol in `core/source/world/chunk_pool.c`.

The only code performing this operation is a `static inline` helper named `get_p_chunk_by__index_from__chunk_pool` (lines 8–19 of `chunk_pool.c`). This helper:
- Has internal linkage (`static`) — invisible to other translation units.
- Is **never called** within its own translation unit — it is dead code.
- Does not match the expected public API name.

The result: the spec's public contract for index-based chunk retrieval is unfulfilled. The implementation layer has a dormant internal stub that was never wired to the public interface.

---

## 2. Impact Assessment

**Current reliance on broken/missing behavior:**
- **None.** No file in `./include` or `./source` calls `get_chunk_at__index_from__chunk_pool` (the function does not exist). No external translation unit references the static helper `get_p_chunk_by__index_from__chunk_pool` (internal linkage prevents this).
- The test file (`tests/core/source/world/test_suite_world_chunk_pool.c`) includes the `.c` file directly (`#include <world/chunk_pool.c>`), giving it access to the static helper, but **no test exercises it**.

**Assumptions invalidated by correction:**
- None. Since no caller depends on the missing function or the dead static helper, promoting the function to public API introduces zero behavioral change to existing code paths.
- The `Chunk_Pool` struct (`Chunk chunks[QUANTITY_OF__GLOBAL_SPACE]`) is embedded in `World` and accessed via `get_p_chunk_pool_from__world`. Adding a public accessor does not alter the struct layout or existing allocation/release semantics.

**Affected callers/callees:**
- `core/source/world/world.c` — includes `chunk_pool.h`; no code change needed (it only calls `initialize_chunk_pool`).
- `core/source/world/global_space_manager.c` — includes `chunk_pool.h`; only calls `release_chunk_from__chunk_pool`. No change needed.
- `tests/core/source/world/test_suite_world_chunk_pool.c` — will need new test cases for the newly exposed function.

**De facto contract:** None exists. The missing function has never been part of any working interface.

---

## 3. Resolution Assessment

### Step 1: Promote the static helper to a public API function

In `core/source/world/chunk_pool.c`:
- Rename `get_p_chunk_by__index_from__chunk_pool` → `get_chunk_at__index_from__chunk_pool`.
- Remove the `static` and `inline` qualifiers.
- Retain the existing body (bounds check under `#ifndef NDEBUG`, direct array indexing).

This satisfies **SSOT** (single implementation, single name) and avoids the code duplication that would result from creating a separate public wrapper around the static helper.

### Step 2: Declare the function in the header

In `core/include/world/chunk_pool.h`, add:

```c
Chunk *get_chunk_at__index_from__chunk_pool(
        Chunk_Pool *p_chunk_pool,
        Index__u32 index_of__chunk);
```

This makes the function's **Precondition** (non-null pool, index in `[0, QUANTITY_OF__GLOBAL_SPACE)`) and **Postcondition** (non-null pointer for valid index; `NULL` for out-of-bounds in debug builds) visible to all consumers.

### Step 3: Update test suite

In `tests/core/source/world/test_suite_world_chunk_pool.c`, add tests:

| Test | Purpose |
|------|---------|
| `chunk_pool__get_at_index__returns_valid_chunk` | Allocate a chunk, retrieve it by its known index, assert pointer equality. **Round Trip Check** for the pool's internal mapping. |
| `chunk_pool__get_at_index__out_of_bounds_returns_null` | Call with `index == QUANTITY_OF__GLOBAL_SPACE`; assert `NULL` return (debug build). **Boundary Condition** coverage. |
| `chunk_pool__get_at_index__deallocated_chunk_returns_valid_ptr` | Retrieve an index that was never allocated; assert non-null pointer (the slot exists, it's just deallocated). Verifies the **Representation Invariant** that the array is always fully populated after `initialize_chunk_pool`. |
| `chunk_pool__get_at_index__null_pool_returns_null` | Pass `NULL` as pool; assert graceful handling. **Precondition** violation test. |

Use **Property Based Testing** for a bulk invariant: for all `i ∈ [0, QUANTITY_OF__GLOBAL_SPACE)`, `get_chunk_at__index_from__chunk_pool(&pool, i)` returns a non-null pointer after initialization.

### Step 4: Documentation / spec alignment

Confirm the spec file (referenced in tests as `docs/specs/core/world/chunk_pool.h.spec.md`) lists `get_chunk_at__index_from__chunk_pool` as a required public function. If the spec uses a different name, align the implementation to the spec (spec is the **SSOT** for naming).

### Phased approach

Not needed. The change is additive (one new declaration + rename of dead code). No existing behavior changes. Single-phase deployment is safe.

---

## 4. Test Verification Checklist

- **Existing tests:** No current test references `get_chunk_at__index_from__chunk_pool` or the static helper. No existing assertions are invalidated.
- **New tests needed:** 4–5 test cases (listed in Step 3 above).
- **Terminology-based recommendations:**
  - **Round Trip Check:** allocate → get_by_index → verify same pointer.
  - **Boundary Condition:** index at `QUANTITY_OF__GLOBAL_SPACE` (one past last valid).
  - **Property Based Testing:** all indices in valid range return non-null after init.
- **Blast radius (tests):** Low. Only `test_suite_world_chunk_pool.c` needs additions. No other test file references the chunk pool's index accessor.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|-----------|
| Files changed | 2 (`chunk_pool.h`, `chunk_pool.c`) + 1 test file |
| Behavior-preserving for existing callers? | Yes — purely additive; no existing call site is affected |
| Phased approach needed? | No — single atomic change |
| De facto contracts invalidated? | None — the function never existed publicly |
| Risk level | **Low** — renaming dead code + adding a declaration cannot break working code paths |
