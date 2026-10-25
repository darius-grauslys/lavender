# Header
- **Function name**: `reset_children_of__graphics_window_from__graphics_window_manager`
- **File of origin**: `core/source/rendering/graphics_window_manager.c`

# Semantic
Iterates over every graphics window held by the manager and, for each window that is allocated and a child of `p_graphics_window`, either releases it (removing it from the pool) or resets it in place, recursing through the child subtree. Used by `reset_graphics_window` (graphics_window.c:379) as the recursive descent into a window's children.

# Pre-conditions
1. `p_game` must be a valid, initialized `Game *` (used to derive `Gfx_Context` and sub-managers).
2. `p_graphics_window_manager` must be a valid, initialized `Graphics_Window_Manager *` containing the backing `graphics_windows` contiguous array.
3. `p_graphics_window` must be a valid (non-null) `Graphics_Window *` that belongs to `p_graphics_window_manager` (its UUID is used as the parent-match key). It need not itself be allocated.
4. `is_releasing_unprovided_children` is a plain boolean controlling whether non-platform-provided children are released (removed from the pool) or merely reset.

# Post-conditions
1. Returns `void`.
2. IntENDED for every allocated child of `p_graphics_window` (traversed in fixed index order over `graphics_windows[0..MAX_QUANTITY_OF__GRAPHICS_WINDOWS)`):
   - If `is_releasing_unprovided_children` is true and the child is not platform-provided, the child is fully released: its sub-managers are torn down, it is returned to the free pool (`initialize_graphics_window` clears it), it is unlinked from the sorted-pointer array, and the manager is re-sorted.
   - Otherwise `reset_graphics_window` is invoked on the child, recursively resetting the child's own children and releasing the child's UI/sprite/hitbox managers while keeping the child allocated.
3. The iteration order is fixed; the sorted-pointer array is re-sorted after any release.

NOTE: The intended post-conditions above do NOT actually hold for the current implementation — see Correctness Verdict / Implementation Correctness.

# Correctness Verdict
Incorrect

# Semantic Alignment
The semantic intent is to traverse the subtree of children rooted at `p_graphics_window` and, per child, choose release-vs-reset based on `is_releasing_unprovided_children` and the CHILD's platform-provided status. The `else` branch (`reset_graphics_window(... p_graphics_window__child ...)`) correctly matches this intent; the `if` branch does not.

In the `if` condition `!is_graphics_window__platform_provided(p_graphics_window)` and in the call `release_graphics_window_from__graphics_window_manager(p_game, p_graphics_window)`, the code uses `p_graphics_window` (the PARENT / subtree root) instead of `p_graphics_window__child` (the child discovered in the loop body). As a result:
- The release-vs-reset decision is based on the parent's flag, not the child's.
- When the branch is taken, the PARENT is released instead of the child.

This is clear semantic drift: children that should be released are left untouched, while the parent (the very window whose children are being reset) is the one actually released. Compare the sibling `release_children_of__graphics_window_from__graphics_window_manager` (graphics_window_manager.c:356-379), which correctly passes `p_graphics_window__child` to `release_graphics_window_from__graphics_window_manager`. The intended implementation is:

```c
if (is_releasing_unprovided_children
        && !is_graphics_window__platform_provided(p_graphics_window__child)) {
    release_graphics_window_from__graphics_window_manager(
            p_game,
            p_graphics_window__child);
} else {
    reset_graphics_window(
            p_game,
            p_graphics_window__child,
            is_releasing_unprovided_children);
}
```

# Implementation Correctness
- Type compatibility: `release_graphics_window_from__graphics_window_manager` takes `(Game *, Graphics_Window *)`; both candidates are `Graphics_Window *`, so types are compatible. No conversion/truncation issue.
- Undefined behavior / wrong variable: the two uses of `p_graphics_window` in the `if` branch are the primary defect. Because the branch releases the parent on every matching iteration, if more than one child satisfies the guard, `release_graphics_window_from__graphics_window_manager` is invoked on `p_graphics_window` repeatedly:
  - The first call clears the parent's slot in `ptr_array_of__sorted_graphic_windows` (sets it to 0) and re-sorts.
  - On the next matching iteration, `get_sorted_slot_of__graphics_window_from__sorted_list` fails to find the parent's slot and returns `0` (null), after which `*p_ptr_sorted_graphics_window_slot = 0;` dereferences a null pointer — undefined behavior / crash (graphics_window_manager.c:402-408).
  - Additionally, repeated `DEALLOCATE_P` + `initialize_graphics_window` on the parent risks a double-release of the parent's backing `PLATFORM_graphics_window`.
- Validation: the function performs no validation that `p_graphics_window` belongs to `p_graphics_window_manager` (unlike `set_graphics_window_as__parent_to__this_graphics_window`, graphics_window_manager.c:220-232, which checks `is_graphics_window_NOT_from__this_graphics_window_manager`). This pre-existing gap is not the introduced bug, but it amplifies the fault. The null check on `p_graphics_window__child` via the bounds-checked helper `get_p_graphics_window_by__index_from__manager` (graphics_window_manager.c:27-40) is present and correct.
- Bounds / off-by-one: the loop bound `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` is correct and matches the helper-based indexing; no out-of-bounds access.

# Side Effects
This function is recursive: the `else` branch calls `reset_graphics_window` (graphics_window.c:379), which calls back into this function, recursing down the child subtree; the `if` branch calls `release_graphics_window_from__graphics_window_manager` (graphics_window_manager.c:381), which itself calls `reset_graphics_window` on its target. For each matching entry it:
- Release branch (as written, erroneously targeting the parent `p_graphics_window`): resets the window, deallocates its `PLATFORM_graphics_window`, re-initializes (clears) the `Graphics_Window` struct to its free-pool default, removes it from the sorted-pointer array, and re-sorts `ptr_array_of__sorted_graphic_windows`. By the current code it is the PARENT — not the child — that is released, corrupting the subtree root whose children are being processed.
- Reset branch (correct): recursively resets the child's subtree, releases the child's UI tile map (if valid), UI manager, sprite manager (if owned), and hitbox manager — while keeping the child allocated.

When the guard is corrected to target `p_graphics_window__child`, the intended side effect is: each non-platform-provided child is released (deallocated + unlinked + re-sorted) and each other child is recursively reset in place.

# Lavender-Specific Semantics — Initialization vs RAII
The "initialization" terminology in this area is Lavender-style (pool cleanup), not RAII. The release branch ultimately calls `initialize_graphics_window` (via `release_graphics_window_from__graphics_window_manager` -> graphics_window.c:400) to clear the struct back to its free-pool default — i.e., the window is being returned to the pool, not "constructed" with resource acquisition. The reset branch likewise tears down sub-managers to return them to their pools. The bug causes this pool-cleanup to happen to the WRONG window (the parent), corrupting the very subtree root whose children are being processed and, on repeated matches, crashing via a null dereference when the parent's (already-cleared) sorted slot cannot be found.
