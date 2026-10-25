# Planning: room.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/structures/room.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/structures/room.h` — the module under review
- `core/include/defines.h` — `Room` struct definition (lines 1880–1888), `Structure_Manager` (lines 1964–1974), `_serialization_header` first-member layout
- `core/include/vectors.h` — `VECTOR__3i32F4__OUT_OF_BOUNDS` sentinel, `get_distance_hamming_of__vectors_3i32F4`, `is_vectors_3i32F4__out_of_bounds`, `is_vectors_3i32F4__equal`
- `core/include/serialization/serialization_header.h` — `initialize_serialization_header_for__deallocated_struct`, `DEALLOCATE_P`, `initialize_serialization_header__contiguous_array`, `get_next_available_p_serialization_header`
- `core/source/collisions/core/aabb/hitbox_aabb.c` — reference `initialize_*` pattern (`memset` + deallocated header)
- `core/Makefile.include` / `core/Makefile.build` — build source collection
- `core/source/world/structures/room.c` — **does not exist** (to be created)
- `tests/core/source/world/structures/*` — **does not exist** (no tests; to be created)

---

## 1. Problem Identification

Three functions in `core/include/world/structures/room.h` are flagged **Incorrect**.
Two are declared but have no definition (**Stub-real divergence** / **Translation Gap**);
one is a `static inline` setter whose declared return type it never honors
(**Type Invariant** violation → **undefined behavior**).

The `Room` struct (`defines.h`, lines 1880–1888) is:
`Serialization_Header _serialization_header` (first member),
`Hitbox_AABB bounding_box_of__room`,
`Vector__3i32F4 entrances__3i32F4[ROOM_ENTRANCE_MAX_QUANTITY_OF]`,
`Room_Type__u16 the_type_of__room`,
`Quantity__u8 quantity_of__room_entrances`,
`Room_Flags__u8 room_flags`.

No `core/source/world/structures/` directory exists, so **none** of the module's
non-inline declarations have a definition. Only `set_the_type_of__room` has an
inline body (in the header), and that body is defective.

### 1.1 `set_the_type_of__room` — non-void setter with no return (UB)

**Location:** `room.h`, lines 46–52 (`static inline`).

**Core defect:** Declared to return `Room_Type__u16`, but the body
(`p_room->the_type_of__room = the_type_of__room;`) has no `return`. Falling
off the end of a non-void function is **undefined behavior** in C. The
assignment itself is correct, but the signature promises a value the body never
produces — a **Type Invariant** / **Postcondition** violation (a
**Surface-form leakage**: the value-returning surface form leaks a contract the
implementation does not honor).

Its siblings `set_room_as__allocated` / `set_room_as__deallocated` (lines 54–74)
are both `void`; `set_the_type_of__room` is the sole outlier. The companion
getter `get_the_type_of__room` (lines 40–44) is **Correct** and is the
**Single Source of Truth (SSOT)** for reading the field.

### 1.2 `get_closest_entrance_to__room` — declared, no definition

**Location:** `room.h`, lines 15–20 (doc comment + declaration; not inline).

**Core defect:** No definition exists anywhere (no `room.c`). This is a
**Stub-real divergence**: the declaration satisfies the compiler, but any call
site produces a **linker error**.

**Semantic intent** (from name + doc): over
`p_room->entrances__3i32F4[0..quantity_of__room_entrances-1]`, compute Hamming
distance to `position__3i32F4` (via `get_distance_hamming_of__vectors_3i32F4`)
and return the closest entrance's position; return the
`VECTOR__3i32F4__OUT_OF_BOUNDS` **Sentinel** when `quantity_of__room_entrances == 0`.
**Frame Condition:** read-only — the `Room` struct is not mutated.

### 1.3 `initialize_room` — declared, no definition

**Location:** `room.h`, lines 8–9 (not inline).

**Core defect:** No definition exists (no `room.c`). **Stub-real divergence**;
any call site produces a **linker error**.

**Semantic intent** (Lavender convention): "initialize" means **reset a struct
to its deallocated state for pool reuse** (not RAII allocation). It must
re-establish the **Representation Invariant** (deallocated serialization header)
so a room can be returned to / reused from the `Structure_Manager` pool.

---

## 2. Impact Assessment

### 2.1 `set_the_type_of__room`

- **Live callers:** none found in `core/include/` or `core/source/` (the module
  is unconsumed; see 2.4). Because it is `static inline`, any TU that includes
  `room.h` and calls it compiles the UB body today — a **latent** landmine, not
  an active failure.
- **Correcting it:** changing the return type `Room_Type__u16` → `void` is a
  **Type Invariant** fix that aligns with the sibling setters. No correct caller
  can depend on the (undefined) return value, so **no de facto contract is
  invalidated**. Any future reader of the field must use
  `get_the_type_of__room` (SSOT).

### 2.2 `get_closest_entrance_to__room`

- **Live callers:** none; the missing definition blocks all usage.
- **Dependencies the fix introduces:**
  - `vectors.h` — `VECTOR__3i32F4__OUT_OF_BOUNDS`, `get_distance_hamming_of__vectors_3i32F4`,
    `is_vectors_3i32F4__out_of_bounds`.
  - `Room.entrances__3i32F4` / `Room.quantity_of__room_entrances` (`defines.h`).
- **Coupled gap (out of scope here):** `add_entrance_to__room` (room.h, lines
  11–13) is *also* declared-but-undefined and is **not** in this review's flagged
  set. It is the function that populates `entrances__3i32F4`, so
  `get_closest_entrance_to__room` is only meaningful once that sibling is
  implemented. This plan implements the query per its documented contract; the
  population gap is tracked under its own review.

### 2.3 `initialize_room`

- **Live callers:** none; the missing definition blocks all usage.
- **Upstream consumer (Coupled):** `Structure_Manager` (`defines.h`, lines
  1964–1974) owns `Room rooms[ROOM_MAX_QUANTITY_OF]` and
  `ptr_array_of__allocated_rooms`. Its header (`structure_manager.h`) declares
  `initialize_structure_manager`, `allocate_room_in__structure_manager`, and
  `release_room_in__structure_manager`. The **release** path needs to reset a
  room to deallocated state — `initialize_room` is the natural per-element
  primitive for that (or the `DEALLOCATE_P` macro). The pool's **Conservation
  Law** (allocated count == number of non-deallocated headers, found via
  `get_next_available_p_serialization_header`) depends on `initialize_room`
  zeroing all fields and marking the header deallocated.
- **Implementation nuance:** `Room` embeds `Hitbox_AABB bounding_box_of__room`,
  which carries its *own* `_serialization_header`. A whole-struct `memset` zeros
  that nested header too (uuid = 0, size = 0), while only the top-level header is
  set to `IDENTIFIER__UNKNOWN__u32`. This matches the established
  `initialize_hitbox_aabb` precedent and the review's expected implementation;
  it is **Conservative** to leave the nested header as zeroed (the bounding box
  is re-initialized on allocation). Flagged here so the implementer does not
  "fix" it into a divergence from precedent.

### 2.4 Module-level state (why impact is currently latent)

- `core/source/world/structures/` **does not exist** — no `room.c`,
  `structure.c`, `site.c`, or `structure_manager.c`. The whole module is
  declaration-only.
- `core/source/world/world.c` (which embeds a `Structure_Manager`) has **zero**
  references to rooms/structures/sites, so the module is not wired into any
  compiled path today.
- **Build fact:** `core/Makefile.include` computes `CFILES_CORE` via
  `find $(SOURCE_CORE) -name *.c`, so a new `core/source/world/structures/room.c`
  is **auto-compiled and linked** — no Makefile edit required. Creating it
  therefore *activates* the two missing symbols rather than leaving them dead.

**Net:** all three defects are **latent** (no active consumer, no live UB, no
current linker break). Correcting them invalidates **no** existing de facto
contract; they only remove landmines and make the module functional for future
wiring.

---

## 3. Resolution Assessment

### 3.1 `set_the_type_of__room` — change return type to `void` (header-only)

- **Change:** in `room.h`, change the return type from `Room_Type__u16` to
  `void`. The body is already correct; only the phantom return contract is
  removed. This is **Idempotence**-safe and behavior-preserving for any caller
  that ignores the return value.
- **Callers:** none to update. Future readers use `get_the_type_of__room`.
- **Guard:** add a **Lint Gate** / **Static Analysis** rule flagging any function
  that falls off the end of a non-void function (prevents recurrence).

### 3.2 Create `core/source/world/structures/room.c`

Both `initialize_room` and `get_closest_entrance_to__room` are non-inline
declarations; they are defined in a new `room.c` (creating the
`core/source/world/structures/` directory), mirroring the codebase convention
(`hitbox_aabb.c` for `hitbox_aabb.h`). The file includes `room.h` and
`vectors.h`.

**`initialize_room`** — mirror `initialize_hitbox_aabb`:

```c
void initialize_room(Room *p_room) {
#ifndef NDEBUG
    if (!p_room) { debug_error("initialize_room, p_room == 0."); return; }
#endif
    memset(p_room, 0, sizeof(Room));
    initialize_serialization_header_for__deallocated_struct(
        &p_room->_serialization_header, sizeof(Room));
}
```

Establishes the deallocated **Representation Invariant** / **Canonical Form** for
pool reuse.

**`get_closest_entrance_to__room`** — **Pure**, **Deterministic**, read-only:

```c
Vector__3i32F4 get_closest_entrance_to__room(
        Room *p_room, Vector__3i32F4 position__3i32F4) {
#ifndef NDEBUG
    if (!p_room) { return VECTOR__3i32F4__OUT_OF_BOUNDS; }
#endif
    if (p_room->quantity_of__room_entrances == 0) {
        return VECTOR__3i32F4__OUT_OF_BOUNDS;
    }
    Vector__3i32F4 closest = p_room->entrances__3i32F4[0];
    i32F4 min_dist = get_distance_hamming_of__vectors_3i32F4(
        position__3i32F4, closest);
    for (Quantity__u8 i = 1; i < p_room->quantity_of__room_entrances; ++i) {
        Vector__3i32F4 cand = p_room->entrances__3i32F4[i];
        i32F4 d = get_distance_hamming_of__vectors_3i32F4(position__3i32F4, cand);
        if (d < min_dist) { min_dist = d; closest = cand; }
    }
    return closest;
}
```

- **`Precondition`:** non-null, valid `Room`. **`Postcondition`:** returns the
  nearest entrance position, or the out-of-bounds **Sentinel** when there are no
  entrances. **Frame Condition:** the `Room` is not mutated.
- Ties break to the lowest index (first minimum) — a stable, deterministic choice.

### 3.3 Phased approach (respects Acyclic Dependencies)

1. **Phase 1 — room module:** fix `set_the_type_of__room` in `room.h`; create
   `room.c` implementing `initialize_room` + `get_closest_entrance_to__room`.
2. **Phase 2 — structure_manager (separate plan):** implement
   `initialize_structure_manager` / `allocate_*` / `release_*`, using
   `initialize_room` for the per-room reset.
3. **Phase 3 — wiring:** connect `initialize_structure_manager` into world init.

The room module is a lower-level **Stable Dependency** of the manager; this
ordering keeps the dependency **Acyclic**.

---

## 4. Test Verification Checklist

**Existing tests surveyed:** `tests/core/source/world/structures/` does **not**
exist — there are **no** tests for this module (confirmed against
`tests/core/source/**` and the `*room*` / `*structure*` patterns). The only
analog is the stubbed `test_suite_collisions_core_aabb_hitbox_aabb.c`
(`DEFINE_SUITE(...)` + `#include <.../hitbox_aabb.c>` + a `#warning`). Because
no tests assert on the current (broken) behavior, **no existing assertions are
invalidated** — all test work below is **new**.

**New test file:** `tests/core/source/world/structures/test_suite_world_structures_room.c`
(+ matching `.h`), following the suite convention (`DEFINE_SUITE(room, ...)`;
`#include <world/structures/room.c>` directly). See `./tests/README`.

Per-function coverage:

- **`initialize_room`**
  - **Round Trip Check:** after init, `uuid == IDENTIFIER__UNKNOWN__u32`,
    `size_of__struct == sizeof(Room)`, all other fields zero,
    `is_room__allocated() == false`; `IS_DEALLOCATED_P` true.
  - **Property Based Testing:** repeated init is **Idempotence**-safe (second
    call leaves the same deallocated state).
- **`set_the_type_of__room`**
  - **Round Trip / Equivalence Check:** set then `get_the_type_of__room` returns
    the same value.
  - **Boundary Condition:** full `uint16_t` range (0, 1, 0x7FFF, 0xFFFF).
- **`get_closest_entrance_to__room`**
  - **Boundary Condition:** `quantity_of__room_entrances == 0` →
    `VECTOR__3i32F4__OUT_OF_BOUNDS`.
  - Single entrance → returns that entrance; multiple entrances → returns the
    nearest (index 0 wins ties).
  - **Equivalence Check** against a brute-force reference for random inputs.
  - **Frame Condition:** snapshot the `Room` before/after and assert it is
    unchanged (**Referentially Transparent**).
  - **Fuzzing:** out-of-bounds query positions, max `ROOM_ENTRANCE_MAX_QUANTITY_OF`
    entrances, near-overflow coordinates.
- **Suite quality:** consider a **Mutation Testing** pass to confirm the new
  assertions actually catch regressions (e.g., a flipped `<`/`<=`, or a dropped
  zero-entrances guard).

**Test blast radius: Low.** No existing tests touched; all additions are new and
isolated to the new room suite. No phased test rollout needed.

---

## 5. Blast Radius Summary

- **Files changed/created:**
  - `core/include/world/structures/room.h` — 1-line return-type change
    (`set_the_type_of__room`: `Room_Type__u16` → `void`). Header-only, low risk.
  - `core/source/world/structures/room.c` — **new** (defines
    `initialize_room`, `get_closest_entrance_to__room`). Auto-compiled via the
    `find`-based `CFILES_CORE` glob; no Makefile edit.
  - `tests/core/source/world/structures/test_suite_world_structures_room.{c,h}`
    — **new**.
  - **Total: 1 header edited, 2 source/test files created.**
- **Behavior-preserving for current callers:** **Yes.** No current compiled
  consumers exist; the fixes only add missing definitions and correct a UB
  signature. Nothing that links today changes behavior.
- **De facto contracts invalidated:** **None.** The broken behavior is
  non-functional (no definition / UB return), so no code can depend on it. The
  only "contract" removed is the phantom return type of
  `set_the_type_of__room`, which no correct caller can rely upon.
- **Phased approach:** Recommended but not strictly required — Phase 1 (the safe
  header fix + new `room.c`) is self-contained and low-coupling; Phases 2–3
  (structure_manager, wiring) are tracked separately and are not prerequisites
  for this plan's correctness.
- **Residual / out-of-scope note:** `add_entrance_to__room` remains
  declared-but-undefined (not in this review's flagged set). It does not block
  the three fixes here, but it must be closed before the room module is fully
  functional end-to-end.
