# Planning: structure.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/structures/structure.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/structures/structure.h`
- `core/include/world/structures/structure_manager.h`
- `core/include/world/structures/room.h`
- `core/include/world/structures/site.h`
- `core/include/defines.h` (Structure, Room, Site, Structure_Manager definitions)
- `core/include/defines_weak.h`
- `core/include/serialization/serialization_header.h`
- `core/source/world/world.c`
- `core/source/entity/entity_manager.c` (pattern reference)
- `core/source/world/chunk_pool.c` (pattern reference)

---

## 1. Problem Identification

All three flagged functions are **Stub-real divergence**: the header declarations establish an interface contract (preconditions, postconditions, semantic intent) but no implementation exists to fulfill it. No `structure.c` file exists anywhere in the source tree. The declarations are forward-only — calling any of these functions would produce a linker error (unresolved symbol).

| Function | Defect |
|----------|--------|
| `initialize_structure` | Declared at `structure.h:7–8`. No definition in any `.c` file. The documented Postcondition (zero all fields, set serialization header to deallocated state) is unfulfillable. |
| `add_p_room_to__structure` | Declared at `structure.h:10–12`. No definition in any `.c` file. The documented Precondition (bounds check against `ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF`) and Postcondition (increment count, store pointer) are unfulfillable. |
| `get_rooms_in__structure` | Declared at `structure.h:24`. No definition in any `.c` file. The documented Postcondition (copy room pointers into caller array, NULL-terminate after last room) is unfulfillable. Additionally, the header comment states "Returns quantity of rooms" but the return type is `void` — a **Surface-form leakage** where stale documentation contradicts the actual signature. |

The root cause is a **Translation Gap**: the interface layer (`structure.h`) was authored but never wired to an implementation translation unit. The sibling modules in the same directory (`room.h`, `site.h`, `structure_manager.h`) share the same gap — none have corresponding `.c` files — but only `structure.h` functions were flagged in this review.

---

## 2. Impact Assessment

**Current callers:** None. No file in `./core/source` or `./tests` calls any of the three functions. The `initialize_world()` function in `world.c` initializes `chunk_pool`, `entity_manager`, `global_space_manager`, `inventory_manager`, `item_manager`, and `tile_logic_context` — but does NOT initialize the embedded `Structure_Manager`. The Makefile does not reference any structure `.c` file.

**De-facto contract status:** No de-facto contract exists. Since no caller ever invokes these functions, there is no behavioral assumption to invalidate. The `World` struct embeds a `Structure_Manager` (containing `Room rooms[128]` and `Structure structures[16]`), but this memory is currently uninitialized (zeroed only if the containing struct is statically allocated or memset by the caller).

**Coupled assumptions that would be affected by correction:**

- **`defines_weak.h` completeness:** The codebase convention (stated in `defines.h` header comment) requires forward declarations of every struct/typedef in `defines_weak.h`. The `Structure`, `Room`, `Site`, and `Structure_Manager` types are absent from `defines_weak.h`. Any new `.c` file that includes only `defines_weak.h` (for lightweight forward references) would fail to compile without these additions.
- **Build system:** The Makefile must be updated to include the new `structure.c` translation unit. Without this, the implementation is dead code.
- **`initialize_world()`:** If a future caller (e.g., `initialize_structure_manager`) needs to call `initialize_structure` on each pooled `Structure`, the `World` initialization sequence must account for it. Currently this is absent — adding the implementation does not force this change, but it becomes available.
- **`is_structure__allocated()` inline:** This inline reads `structure_flags & STRUCTURE_FLAG__IS_ALLOCATED`. It is only meaningful if `initialize_structure` has been called (to establish the deallocated state) or `set_structure_as__allocated` has been called. No current caller of this inline exists, so no assumption is invalidated.

**Blast radius:** **Low.** The fix introduces a new file and adds forward declarations. No existing behavior changes. No existing caller is broken.

---

## 3. Resolution Assessment

### Step 1: Create `core/source/world/structures/structure.c`

Implement all three functions following the established codebase initialization pattern (evidenced by `initialize_entity_manager`, `initialize_chunk_pool`, `f_entity_initializer__default`):

**`initialize_structure(Structure *p_structure)`:**
```
1. #ifndef NDEBUG: null-check p_structure, debug_error + return on failure.
2. memset(p_structure, 0, sizeof(Structure))  — zeroes all 6 fields.
3. Call initialize_serialization_header(
       &p_structure->_serialization_header,
       IDENTIFIER__UNKNOWN__u32,
       sizeof(Structure))
   This sets the header to deallocated state (uuid = 0xFFFFFFFF).
```

Rationale: `Structure` uses `Serialization_Header` (u32 uuid), not `Serialization_Header__UUID_64`. The correct helper is `initialize_serialization_header` (not the `_uuid_64` variant). The `DEALLOCATE_P` macro in `serialization_header.h` confirms this pattern.

**`add_p_room_to__structure(Structure *p_structure, Room *p_room)`:**
```
1. #ifndef NDEBUG: null-check p_structure and p_room; debug_error + return.
2. #ifndef NDEBUG: if (p_structure->quantity_of__rooms_in__structure
       >= ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF) { debug_error; return; }
   — Boundary Condition guard preventing out-of-bounds write.
3. p_structure->ptr_array_of__rooms[
       p_structure->quantity_of__rooms_in__structure] = p_room;
4. p_structure->quantity_of__rooms_in__structure++;
```

Postcondition invariant: `quantity_of__rooms_in__structure <= ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF` (Representation Invariant).

**`get_rooms_in__structure(Structure *p_structure, Structure_Ptr_Array_Of__Rooms ptr_array_of__rooms)`:**
```
1. #ifndef NDEBUG: null-check p_structure; debug_error + return.
2. #ifndef NDEBUG: null-check ptr_array_of__rooms; debug_error + return.
3. for (i = 0; i < p_structure->quantity_of__rooms_in__structure; i++)
       ptr_array_of__rooms[i] = p_structure->ptr_array_of__rooms[i];
4. if (p_structure->quantity_of__rooms_in__structure < ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF)
       ptr_array_of__rooms[p_structure->quantity_of__rooms_in__structure] = NULL;
```

Postcondition: indices `[0, quantity-1]` hold valid `Room*`; index `quantity` is NULL (Sentinel); indices beyond that are undefined (documented).

**Includes needed in `structure.c`:**
```c
#include "world/structures/structure.h"
#include "defines.h"
#include "serialization/serialization_header.h"
#ifndef NDEBUG
#include "debug/debug.h"
#endif
```

### Step 2: Add forward declarations to `core/include/defines_weak.h`

Under `SECTION_world`, add:
```c
typedef struct Room_t Room;
typedef struct Structure_t Structure;
typedef struct Site_t Site;
typedef struct Structure_Manager_t Structure_Manager;
```

This satisfies the codebase's stated convention and allows any translation unit to include only `defines_weak.h` for lightweight forward references without pulling in the full `defines.h`.

### Step 3: Update build system

Add `core/source/world/structures/structure.c` to the Makefile's source list (alongside other `world/*.c` files).

### Step 4: Fix stale documentation in `structure.h`

The comment block above `get_rooms_in__structure` states "Returns quantity of rooms in the structure" but the function returns `void`. Correct the comment to accurately describe the actual contract:
```
/// Copies the structure's room pointer array into the
/// caller-provided output array. The element at index
/// quantity_of__rooms_in__structure is set to NULL (sentinel).
/// Indices beyond that are undefined.
/// Use get_quantity_of__rooms_in__structure() for the count.
```

### Step 5 (Optional, separate concern): Wire into `initialize_world`

If the project intends for `World` initialization to cover the embedded `Structure_Manager`, a future step would add:
- An `initialize_structure_manager` implementation (in a new `structure_manager.c`) that memsets the manager and calls `initialize_serialization_header__contiguous_array` for both its `rooms[]` and `structures[]` arrays.
- A call to it from `initialize_world()`.

This is **out of scope** for the current fix (the review flagged only `structure.h` functions) but is noted as a follow-up dependency.

---

## 4. Test Verification Checklist

**Existing tests:** No test files reference any of the three functions. No structure-related tests exist in `tests/`. The fix does not invalidate any existing assertions.

**New tests needed (in `tests/no_gui/` or equivalent):**

| Test | Strategy | What it verifies |
|------|----------|-----------------|
| `initialize_structure` zeroes all fields | **Property Based Testing** — generate random `Structure` with garbage, call init, assert all fields are in canonical deallocated state. | Representation Invariant: post-init, `is_structure__allocated()` returns false; all room pointers are NULL; quantity is 0. |
| `add_p_room_to__structure` appends correctly | **Round Trip Check** — init a structure, add N rooms, call `get_rooms_in__structure`, verify the output array matches what was added. | Conservation Law: quantity in == quantity out; pointer identity preserved. |
| `add_p_room_to__structure` respects boundary | **Fuzzing** — attempt to add 9+ rooms to a single structure. Assert the 9th is rejected (debug build) and `quantity_of__rooms_in__structure` never exceeds 8. | Boundary Condition: no out-of-bounds write into `ptr_array_of__rooms`. |
| `get_rooms_in__structure` NULL-terminates | **Equivalence Check** — for a structure with K < 8 rooms, verify output[K] == NULL and output[0..K-1] match the internal array. | Sentinel invariant: exactly one NULL terminator at the correct index. |
| `initialize_structure` is idempotent | **Property Based Testing** — call init twice on same struct; assert second call produces identical state. | Idempotence: f(f(x)) == f(x). |

**Blast radius for tests:** Low. All new tests are additive. No existing test is invalidated.

---

## 5. Blast Radius Summary

| Dimension | Assessment |
|-----------|------------|
| Files changed | 3 (`structure.c` new, `defines_weak.h` edited, Makefile edited) + optional `structure.h` comment fix |
| Behavior-preserving for current callers? | Yes — no current callers exist. Purely additive. |
| Phased approach needed? | No. Single-phase: create `.c`, add forward decls, update build. |
| De-facto contracts invalidated? | None. The functions were never callable (linker error). |
| Risk of regression to existing modules? | None. The new `.c` file introduces new symbols; it does not modify existing behavior. |
