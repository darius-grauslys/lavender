# Planning: structure_manager.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/structures/structure_manager.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/structures/structure_manager.h`
- `core/include/defines.h` (Structure_Manager, Room, Structure definitions)
- `core/include/world/structures/room.h`
- `core/include/world/structures/structure.h`

---

## 1. Problem Identification

**`allocate_room_in__structure_manager`** — **Stub-real divergence.**

The function is declared at lines 9–10 of `core/include/world/structures/structure_manager.h`:

```c
Room *allocate_room_in__structure_manager(
        Structure_Manager *p_structure_manager);
```

It has **no implementation** anywhere in the codebase. No `core/source/world/structures/structure_manager.c` file exists, and no other `.c` file provides a definition for this symbol. The declaration is a stub that satisfies the header's structural interface but violates its semantic contract: any call site will produce a linker error.

This is a **Translation Gap** — the header layer declares an allocation operation that the source layer never wires to an actual implementation.

---

## 2. Impact Assessment

### Direct coupling

- **`World` struct** (`core/include/defines.h`, line 2442): embeds `Structure_Manager structure_manager` as a member. Any code that initializes, serializes, or inspects a `World` implicitly assumes the embedded manager's functions are callable. The `Structure_Manager` pool (128 `Room` slots, 16 `Structure` slots) occupies a fixed block within every `World` instance.

- **Sibling declarations in the same header** (`initialize_structure_manager`, `allocate_structure_in__structure_manager`, `release_room_in__structure_manager`, `release_structure_in__structure_manager`): all are declared with no `.c` implementation. The entire `structure_manager.h` interface is an unfulfilled contract. If any of these are implemented independently without the others, the **Representation Invariant** of the pool (counter ↔ ptr-array ↔ flags consistency) cannot be maintained.

### Blast radius of correction

- **No existing callers**: No `.c` file in `core/source/` or `tests/` calls `allocate_room_in__structure_manager`. Correcting the defect introduces a new implementation; it does not invalidate any existing behavior-preserving assumption, because no code currently depends on the broken (absent) behavior.

- **Downstream dependency chain (latent)**: Once implemented, callers will rely on the **Postcondition** that a non-null return implies `ROOM_FLAG__IS_ALLOCATED` is set, `quantity_of__allocated_rooms` is incremented, and the pointer is recorded in `ptr_array_of__allocated_rooms`. Any future caller that assumes these invariants without calling `initialize_structure_manager` first will violate the **Precondition** (pool must be initialized with deallocated headers).

- **No de facto contract to invalidate**: Because the function is never called, no code has adapted to its absence. The fix is purely additive.

### Assumptions invalidated by correction

None currently. The correction is non-breaking for all existing code paths.

---

## 3. Resolution Assessment

### Step 1 — Create the source file

Create `core/source/world/structures/structure_manager.c` implementing **all** functions declared in `structure_manager.h`:

| Function | Implementation approach |
|----------|------------------------|
| `initialize_structure_manager` | Zero the ptr-arrays, set all `Room._serialization_header.uuid` to `IDENTIFIER__UNKNOWN__u32`, zero counters. Follow pattern from `entity_manager.c` / `inventory_manager.c`. |
| `allocate_room_in__structure_manager` | Scan `rooms[]` for first slot with `uuid == IDENTIFIER__UNKNOWN__u32`. If found: assign a UUID (via the world's or manager's randomizer), set `ROOM_FLAG__IS_ALLOCATED`, store pointer at `ptr_array_of__allocated_rooms[quantity_of__allocated_rooms]`, increment counter, return pointer. If none found: return null. |
| `allocate_structure_in__structure_manager` | Same pattern over `structures[]` using `STRUCTURE_FLAG__IS_ALLOCATED`. |
| `release_room_in__structure_manager` | Clear `ROOM_FLAG__IS_ALLOCATED`, reset UUID to `IDENTIFIER__UNKNOWN__u32`, remove pointer from ptr-array (swap-with-tail or linear scan), decrement counter. |
| `release_structure_in__structure_manager` | Same pattern for structures. |

### Step 2 — Callers

No existing callers require updating. No caller changes needed.

### Step 3 — Documentation / comments

Add a brief doc-comment block above each function in the `.c` file stating its **Precondition**, **Postcondition**, and **Frame Condition** (what it mutates: the pool slot, the ptr-array entry, the counter; what it leaves alone: all other pool slots).

### Step 4 — Build system

Ensure the new `.c` file is included in the build (Makefile / CMake / whatever build system is in use for `core/source/world/structures/`).

### Phasing

No phased approach needed. The change is isolated to a single new file plus a build-system entry. All five functions should be implemented together to preserve the **Conservation Law** of the allocation counter (allocate +1, release −1, net zero over a full lifecycle).

---

## 4. Test Verification Checklist

### Existing test coverage

No test file references `structure_manager` or any of its functions. The `tests/core/source/` directory contains no `test_suite_world_structures_*` file. **Zero existing assertions will be invalidated.**

### New tests required

Create `tests/core/source/world/test_suite_world_structure_manager.c`:

| Test | Strategy | Purpose |
|------|----------|---------|
| Allocate one room from initialized manager | Round Trip Check | Verify pointer non-null, flag set, counter == 1, ptr-array[0] correct. |
| Allocate all 128 rooms, then attempt one more | Boundary Condition / Fuzzing | Verify null return on pool exhaustion; counter stays at 128. |
| Allocate → Release → Re-allocate same slot | Round Trip Check | Verify counter returns to baseline; slot is reusable. |
| Allocate N rooms, release M, verify counter == N−M | Property Based Testing (Conservation Law) | `quantity_of__allocated_rooms` must equal the number of slots with `ROOM_FLAG__IS_ALLOCATED` set. |
| Null pointer to manager | Assertion / Precondition guard | Verify debug-mode assertion fires; no UB. |

### Blast radius (tests)

**Low.** No existing tests affected. New test file is self-contained.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files changed | 1 new `.c` file + 1 build-system entry. **2 files.** |
| Behavior-preserving for current callers? | Yes — no current callers exist. Change is purely additive. |
| Phased approach needed? | No. Single-transaction implementation of all five functions. |
| De facto contracts invalidated? | None. No code relies on the absence of this function. |
| Risk level | **Low.** Isolated module, fixed-size pool, no heap allocation, no concurrency. |
