get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager

## 1. Header

- **Function name:** `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager`
- **File of origin:** `core/include/collisions/core/aabb/hitbox_aabb_manager.h`

## 2. Semantic

A pure inline accessor that retrieves the `Hitbox_AABB *` stored at a given index in the
manager's `pM_ptr_array_of__hitbox_records` array. It is a read-only record lookup by
positional index (not by identity/UUID), intended for blind iteration over all pooled
hitboxes.

## 3. Pre-conditions

1. `p_hitbox_aabb_manager` is non-null. The function dereferences it unconditionally
   (`->quantity_of__hitboxes`, `->pM_ptr_array_of__hitbox_records`); **no null check is
   performed, even in debug builds** (see Implementation Correctness notes).
2. `p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records` has been allocated with at
   least `p_hitbox_aabb_manager->quantity_of__hitboxes` entries. This invariant is
   established by `f_hitbox_manager__allocator_AABB` / `initialize_hitbox_aabb_manager`
   (`core/source/collisions/core/aabb/hitbox_aabb_manager.c:53-54, 179-180`), which
   allocates the records array as `sizeof(Hitbox_AABB*) * quantity_of__hitboxes_to__pool`
   and sets the manager's `quantity_of__hitboxes` to the same value.
3. `index_of__hitbox` is in the range `[0, quantity_of__hitboxes - 1]`.

## 4. Post-conditions

1. In a debug build, if `index_of__hitbox >= quantity_of__hitboxes`, an error is logged
   via `debug_error` and the function returns `0` (NULL) without performing the array
   access.
2. Otherwise, returns `p_hitbox_aabb_manager->pM_ptr_array_of__hitbox_records[index_of__hitbox]`,
   which is the `Hitbox_AABB *record` at that index.
3. The manager and the hitbox are **not modified**. (Note: records are `memset` to `0`
   at initialization, so an unoccupied slot yields a NULL record pointer, which is
   semantically distinct from an out-of-bounds index.)
4. In a release build (`NDEBUG` defined), the bounds check is compiled out entirely; an
   out-of-bounds `index_of__hitbox` results in an out-of-bounds read on
   `pM_ptr_array_of__hitbox_records` (undefined behavior). The caller is responsible for
   passing a valid index.

## 5. Correctness Verdict

**Correct.**

## 6. Semantic Alignment

The implementation fulfills its semantic intent exactly: it looks up a hitbox record by
positional index against the manager's records array. The chosen guard (`>=` against
`quantity_of__hitboxes`) is the correct half-open bound for `[0, N)`, and the invariant
that the records array length equals `quantity_of__hitboxes` holds (verified against the
allocator and initializer at `hitbox_aabb_manager.c:53-54, 179-180`). There is no struct
initialization to audit here; the function is a getter, and no computation is performed.

## 7. Implementation Correctness

- **Type compatibility:** `Index__u32` is `uint32_t` (`defines.h:129`); it indexes
  `Hitbox_AABB **pM_ptr_array_of__hitbox_records` and is compared against
  `Quantity__u32` (`uint32_t`, `defines.h:140`). No implicit conversions, no truncation.
- **Undefined behavior:** Debug guard prevents out-of-bounds indexing and avoids null
  dereference of the records array for a valid manager. However, the guard does NOT cover
  a null `p_hitbox_aabb_manager` — passing NULL causes a null dereference on the very first
  field access (`->quantity_of__hitboxes`) in both debug and release.
- **Validation appropriateness:** Bounds validation is debug-only via `#ifndef NDEBUG`,
  matching the codebase convention for hot inline accessors (e.g.
  `get_p_entity_by__index_from__entity_manager`, `get_p_local_space_by__index_from__local_space_manager`).
  This is a reasonable performance trade-off for an inline getter.
- **Null-check gap (finding):** Sibling index getters
  (`get_p_entity_by__index_from__entity_manager` at `entity/entity_manager.h:111-114`,
  `get_p_local_space_by__index_from__local_space_manager` at `world/local_space_manager.h`)
  all null-check their manager pointer inside the debug block and return `0` on failure.
  This function omits that check, making it inconsistent with the established pattern and
  leaving a null-manager dereference unguarded even in debug builds.
- **Return convention:** `return 0;` for the NULL pointer is valid in C but stylistically
  inconsistent — `debug_error` is variadic (`debug.h:43`) and the codebase elsewhere
  documents the `0`/`NULL` sentinel via `"... == 0."` messages; using `NULL` (or `0`)
  consistently with a descriptive message would improve clarity.

## 8. Side Effects

No side effects on the game state, manager, or hitbox records. The function performs
only a read of the records array and returns a pointer value. (The sole observable
effect is the `debug_error` log emitted on the out-of-bounds error path in debug builds,
which is an intended diagnostic side effect rather than a state mutation.)

## Lavender-Specific Semantics

This function is a pure accessor (name contains "get", not "init"/"initialize"/"reset"),
so the Lavender "initialization ≠ RAII" distinction does not apply — no resource
acquisition or pool-return-to-free semantics are involved. It reads from an already
initialized, pooled array.
