# Planning: tile_logic_table.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/tile_logic_table.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/tile_logic_table.h`
- `core/source/world/tile_logic_table.c`
- `core/source/world/tile_logic_context.c`
- `core/include/world/tile_logic_context.h`
- `tests/core/source/world/test_suite_world_tile_logic_table.c`

---

## 1. Problem Identification

### `allocate_tile_logic_table__tile_logic_entries` — State Desync

The function allocates heap memory for the records array and assigns the pointer to `pM_tile_logic_records`, but never writes back the `quantity_of__tile_logic_records__u16` or `size_of__tile_logic_records__u16` fields. The parameter is consumed only for the `malloc` size expression; the struct's bookkeeping fields remain at their initialized (zero) values. This is a **State Desync**: two representations of the same fact (the allocated capacity vs. the recorded quantity) have diverged. The `Representation Invariant` — that the pointer, quantity, and size fields are mutually consistent — is violated on every successful call.

Additionally, `#include <stdlib.h>` is absent from `tile_logic_table.c`, making the `malloc` call an implicit declaration (undefined behavior in C99+).

### `release_tile_logic_table__tile_logic_entries` — Stub-real divergence

The function is declared in the header but has no implementation in any source file. This is a **Translation Gap**: the interface layer promises a symbol that the implementation layer never provides. Any caller will encounter a linker error. The intended semantic — free the `pM_tile_logic_records` heap allocation and null the pointer — is unfulfilled.

---

## 2. Impact Assessment

### Dependents on `quantity_of__tile_logic_records__u16` (broken by State Desync)

| Caller | Location | Coupling |
|--------|----------|----------|
| `get_p_tile_logic_record_from__tile_logic_table` | `core/include/world/tile_logic_table.h` (inline) | Debug-build bounds check: `quantity_of__tile_logic_records__u16 <= index` → with quantity at 0, **all** index lookups fail in debug builds |
| `get_p_tile_logic_record_from__tile_logic_context` | `core/include/world/tile_logic_context.h` (inline) | Delegates to the above; inherits the broken bounds check |
| `poll__is_tile__unpassable` | `core/include/world/tile_logic_context.h` (inline) | Calls `get_p_tile_logic_record_from__tile_logic_context` |
| `poll__is_tile__sight_blocking` | `core/include/world/tile_logic_context.h` (inline) | Calls `get_p_tile_logic_record_from__tile_logic_context` |
| `poll__is_tile__without_ground` | `core/include/world/tile_logic_context.h` (inline) | Calls `get_p_tile_logic_record_from__tile_logic_context` |
| `poll__tile_height` | `core/include/world/tile_logic_context.h` (inline) | Calls `get_p_tile_logic_record_from__tile_logic_context` |

Correcting the State Desync **restores** the debug bounds check to its intended behavior. No caller currently relies on the broken (always-zero) quantity as a de facto contract; they rely on it being *populated*. The fix is therefore behavior-restoring, not behavior-breaking.

### Dependents on `release_tile_logic_table__tile_logic_entries` (broken by missing implementation)

| Caller | Location | Coupling |
|--------|----------|----------|
| `release_tile_logic_table_from__tile_logic_context` | `core/source/world/tile_logic_context.c` | Frees the `Tile_Logic_Table` struct via `free()` but does **not** free the internally-heap-allocated `pM_tile_logic_records` array. If `allocate_tile_logic_table__tile_logic_entries` was called, the records array **leaks**. The release path must be extended to call the entries-release before freeing the struct. |

### Blast radius of correction

- **`core/source/world/tile_logic_table.c`**: Add `#include <stdlib.h>`; add two field assignments after successful `malloc`; set pointer to 0 on `malloc` failure. Implement `release_tile_logic_table__tile_logic_entries`.
- **`core/source/world/tile_logic_context.c`**: In `release_tile_logic_table_from__tile_logic_context`, call `release_tile_logic_table__tile_logic_entries` on the table before `free`-ing the struct. This is a **Frame Condition** correction: the release function's contract must account for all heap allocations owned by the struct.
- **No other source files** currently call these two functions directly (the registrar and context functions use different allocation paths), so the blast radius is contained to these two `.c` files.

---

## 3. Resolution Assessment

### Fix 1: `allocate_tile_logic_table__tile_logic_entries` (State Desync)

**What changes in the implementation:**
1. Add `#include <stdlib.h>` at the top of `core/source/world/tile_logic_table.c`.
2. After the successful `malloc` assignment, add:
   ```c
   p_tile_logic_table->quantity_of__tile_logic_records__u16 = quantity_of__tile_logic_records__u16;
   p_tile_logic_table->size_of__tile_logic_records__u16 = quantity_of__tile_logic_records__u16;
   ```
3. On `malloc` failure (pointer is NULL), explicitly set `p_tile_logic_table->pM_tile_logic_records = 0` to maintain the **Postcondition** that on failure the pointer is unchanged (or null). This preserves the **Representation Invariant** in both success and failure paths.

**Callers needing updates:** None. The fix restores the fields to their intended values; all existing callers of `get_p_tile_logic_record_from__tile_logic_table` will now pass the debug bounds check correctly.

**Documentation:** Update the function's doc comment to explicitly state the **Postcondition** that both quantity and size fields are set on success.

### Fix 2: `release_tile_logic_table__tile_logic_entries` (Stub-real divergence)

**What changes in the implementation:**
Implement the function in `core/source/world/tile_logic_table.c`:
```c
void release_tile_logic_table__tile_logic_entries(
        Tile_Logic_Table *p_tile_logic_table) {
#ifndef NDEBUG
    if (!p_tile_logic_table) {
        debug_error("release_tile_logic_table__tile_logic_entries, p_tile_logic_table == 0.");
        return;
    }
#endif
    if (p_tile_logic_table->pM_tile_logic_records) {
        free(p_tile_logic_table->pM_tile_logic_records);
        p_tile_logic_table->pM_tile_logic_records = 0;
    }
}
```

Key properties:
- **Idempotence**: Calling with a NULL pointer (already released) is a no-op. Safe to call multiple times.
- **Frame Condition**: Only mutates `pM_tile_logic_records`. Does not touch quantity or size fields (those are managed by the allocator/initializer).

**Callers needing updates:** None directly — the function was already declared and any future caller will now link successfully.

### Fix 3: `release_tile_logic_table_from__tile_logic_context` (memory leak)

**What changes in the implementation:**
In `core/source/world/tile_logic_context.c`, before the existing `free(...)` of the table struct, insert:
```c
release_tile_logic_table__tile_logic_entries(
        p_tile_logic_context->array_of__pM_tile_logic_tables[
            the_tile_layer_to__release]);
```

This ensures the **Conservation Law** of heap memory: every allocation has a corresponding deallocation. The `Tile_Logic_Table` struct owns a sub-allocation (`pM_tile_logic_records`); releasing the struct without releasing its sub-allocation is a leak.

**Callers needing updates:** None. The function signature is unchanged; the internal behavior is corrected.

### Phased approach

Not required. The three fixes are small, orthogonal, and can be applied in a single commit:
1. Fix the allocator (State Desync + missing include).
2. Implement the releaser (Stub-real divergence).
3. Wire the releaser into the context release path (leak fix).

---

## 4. Test Verification Checklist

### Existing tests

| Test | File | Status after fix |
|------|------|-----------------|
| `tile_logic_table__initialize__zeroes_records` | `tests/core/source/world/test_suite_world_tile_logic_table.c` | **Passes** — asserts `quantity_of__records == 0` after init. (Note: field name in test is `quantity_of__records`; verify this matches the struct field or is a typo for `quantity_of__tile_logic_records__u16`.) |
| All `tile_logic_record__*` tests | same file | **Unaffected** — they test record-level predicates, not table allocation. |

No existing test asserts on the *broken* behavior (zero quantity after allocation). The fix does not invalidate any existing assertion.

### New tests required

| Test | Strategy | Rationale |
|------|----------|-----------|
| `allocate__sets_quantity_and_size` | **Property Based Testing**: for a range of quantities, assert `quantity_of__tile_logic_records__u16 == qty` and `size_of__tile_logic_records__u16 == qty` after successful allocation. | Verifies the **Representation Invariant** is restored. |
| `allocate__zero_quantity_returns_false` | Boundary Condition | Confirms the guard: quantity 0 → return false, pointer unchanged. |
| `release__frees_and_nulls_pointer` | **Round Trip Check**: allocate then release; assert pointer is NULL. Run under a memory checker (valgrind/ASan) to confirm no leak. | Verifies the **Conservation Law** for heap memory. |
| `release__idempotent_on_null` | Boundary Condition | Call release on an already-released (NULL pointer) table; assert no crash, no double-free. |
| `get_record__valid_index_after_allocate` | **Equivalence Check**: after allocating N records, `get_p_tile_logic_record_from__tile_logic_table(&table, i)` returns non-null for all `i < N` in debug builds. | Confirms the bounds check no longer rejects valid indices. |
| `context_release__no_leak` | **Round Trip Check** under ASan: allocate table via context, allocate entries, release via context; assert no leaked memory. | Verifies Fix 3 closes the leak path. |

### Blast radius (tests)

- **Low**: One existing test file (`test_suite_world_tile_logic_table.c`) needs new test functions added. No existing assertions are invalidated.
- A new test file for `tile_logic_context` release-path leak testing may be warranted if none exists.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files modified | 2 (`core/source/world/tile_logic_table.c`, `core/source/world/tile_logic_context.c`) + 1 test file |
| Behavior-preserving for current callers? | **Yes** — the fix restores intended behavior; no caller relies on the broken state as a de facto contract |
| Phased approach needed? | **No** — three small, orthogonal edits in a single commit |
| De facto contracts invalidated? | **None** — the broken behavior (zero quantity, missing release) was never a stable contract; it was a defect |
| Linker impact | Fixing `release_tile_logic_table__tile_logic_entries` resolves a potential link error for any future caller |
