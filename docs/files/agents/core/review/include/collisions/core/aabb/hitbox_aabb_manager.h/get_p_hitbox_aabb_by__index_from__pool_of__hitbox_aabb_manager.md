get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager — core/source/collisions/core/aabb/hitbox_aabb_manager.c, lines 19-34

### Function Under Review

```c
static inline
Hitbox_AABB *get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager(
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        Index__u32 index_of__hitbox) {
#ifndef NDEBUG
    if (!p_hitbox_aabb_manager) {
        debug_error("get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager, p_hitbox_aabb_manager == 0.");
        return 0;
    }
    if (index_of__hitbox >= MAX_QUANTITY_OF__HITBOX_AABB) {
        debug_error("get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager, index out of bounds, %d/%d", index_of__hitbox, MAX_QUANTITY_OF__HITBOX_AABB);
        return 0;
    }
#endif
    return &p_hitbox_aabb_manager->pM_pool_of__hitboxes[index_of__hitbox];
}
```

---

## 2. Semantic

Returns a pointer to the `Hitbox_AABB` element at `index_of__hitbox` within the manager's contiguous hitbox pool (`pM_pool_of__hitboxes`). This is a direct-index pool lookup, not a lookup through the pointer-array record (`pM_ptr_array_of__hitbox_records`), which is handled by the sibling function `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` in the header.

## 3. Pre-conditions

1. `p_hitbox_aabb_manager` must be non-null (checked only in debug builds).
2. `index_of__hitbox` must be less than `p_hitbox_aabb_manager->quantity_of__hitboxes` — i.e., within the bounds of the actual allocated pool. However, the function only checks against `MAX_QUANTITY_OF__HITBOX_AABB` (see Implementation Correctness below), so indices between `quantity_of__hitboxes` and `MAX_QUANTITY_OF__HITBOX_AABB` are permitted by the debug guard but are out of bounds on the allocated pool.
3. The function is `static inline` and defined in the `.c` file, so it is only callable within `hitbox_aabb_manager.c`. It is currently called from `allocate_hitbox_aabb_from__hitbox_aabb_manager`.

## 4. Post-conditions

- Returns a pointer to `&p_hitbox_aabb_manager->pM_pool_of__hitboxes[index_of__hitbox]`.
- In debug builds, if `p_hitbox_aabb_manager` is null or `index_of__hitbox >= MAX_QUANTITY_OF__HITBOX_AABB`, returns `0` (null).
- No state is mutated. The returned pointer is non-owning; the caller must not free it.

## 5. Correctness Verdict

**Incorrect**

## 6. Semantic Alignment

The function's intent is to return a pointer to a pool element at a valid index. The implementation does access `pM_pool_of__hitboxes[index_of__hitbox]` and returns its address, which aligns with the semantic intent. However, the bounds check does not match the actual pool size (`quantity_of__hitboxes`), creating a semantic gap: the function can return a pointer to memory outside the allocated pool while believing the index is valid. This is a correctness defect that undermines the semantic contract.

The sibling function `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` (header, lines 58-70) correctly checks against `p_hitbox_aabb_manager->quantity_of__hitboxes`, confirming the intended pattern.

## 7. Implementation Correctness

### Bug: Bounds check uses `MAX_QUANTITY_OF__HITBOX_AABB` instead of `quantity_of__hitboxes`

This is the primary defect. The pool of hitboxes is allocated with exactly `quantity_of__hitboxes` elements (see `f_hitbox_manager__allocator_AABB`, line 46: `malloc(sizeof(Hitbox_AABB) * quantity_of__hitboxes_to__pool)`). However, the debug bounds check compares against the compile-time constant `MAX_QUANTITY_OF__HITBOX_AABB` (256), not the runtime `quantity_of__hitboxes` field.

**Consequence**: If the manager is initialized with fewer than 256 hitboxes (e.g., 128), an index in the range `[128, 256)` passes the debug guard but accesses memory beyond the allocated pool, causing undefined behavior (out-of-bounds read/write to the returned pointer). In release builds (`NDEBUG` defined), there is no bounds check at all.

**Fix**: Change the guard to:
```c
if (index_of__hitbox >= p_hitbox_aabb_manager->quantity_of__hitboxes) {
```

### Minor: Debug error message uses wrong function name

The second `debug_error` call (line 29) reports the function name as `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` (missing the `_pool_of_` suffix). This is a copy-paste error that will mislead debugging. It should read `get_p_hitbox_aabb_by__index_from__pool_of__hitbox_aabb_manager`.

### Minor: Format specifier mismatch

`index_of__hitbox` is `Index__u32` (i.e., `uint32_t`), but the format string uses `%d` (signed `int`). While `MAX_QUANTITY_OF__HITBOX_AABB` is an `int` literal (`256`), `index_of__hitbox` being printed as `%d` could produce misleading output for very large values (though in practice the value is bounded by `MAX_QUANTITY_OF__HITBOX_AABB`). Using `%u` with an explicit cast would be more correct.

### No bounds check in release builds

All validation is inside `#ifndef NDEBUG`. This is consistent with the rest of the codebase's convention (every function follows this pattern), so it is not a deviation. However, note that out-of-bounds access in release mode is entirely unchecked.

### `static inline` in `.c` file

The function is declared `static inline` in the `.c` file rather than the header. This limits its visibility to the translation unit. While valid, it is inconsistent with the sibling function `get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager` which is `static inline` in the header. If the pool-access variant is needed by other translation units, it should be moved to the header. This is a design observation, not a bug.

## 8. Side Effects

No side effects. The function is pure: it reads `p_hitbox_aabb_manager->pM_pool_of__hitboxes` and returns the address of an element. It does not modify the manager, the pool, or any global state. It does invoke `debug_error` in debug builds when validation fails, which is an observable side effect (logging) but is standard for the codebase's debug pattern.

---

### Summary

The function has one critical bug: the debug-mode bounds check compares against `MAX_QUANTITY_OF__HITBOX_AABB` (256) instead of `p_hitbox_aabb_manager->quantity_of__hitboxes`, allowing out-of-bounds pool access whenever the manager is initialized with fewer than 256 hitboxes. This mirrors the correct pattern already used in the sibling function. Two minor issues (incorrect function name in error message, format specifier mismatch) should also be addressed.
