# Review: f_sort_heuristic__p_graphics_window

## 1. Header
- **Function name:** `f_sort_heuristic__p_graphics_window`
- **File of origin:** `core/source/rendering/graphics_window_manager.c`

## 2. Semantic
A comparator (signaled by `Signed_Quantity__i32`) used by `heap_sort__opaque` to order
the `ptr_array_of__sorted_graphic_windows` array into render order. Windows are ordered so
that parents render before children, and siblings, roots, and disjoint (lateral) ancestors
are ordered by ascending Z (`position_of__gfx_window.z__i32`, lower values first / drawn
earliest). The heap sort is a standard ascending max-heap, so a *negative* return means
*p_one renders before/at the same priority as p_two*, and a *positive* return means
*p_two renders before p_one*.

## 3. Pre-conditions
1. `p_context` is non-null and points to a valid `Graphics_Window_Manager`.
2. `pv_graphics_window__one` and `pv_graphics_window__two` are non-null `void*` that point
   to elements of type `Graphics_Window*` (i.e., `Graphics_Window**`), as dispatched by
   `heap_sort__opaque` with `size_of__type == sizeof(Graphics_Window*)`.
3. The dereferenced `Graphics_Window*` values may be null (a deallocated/empty slot); the
   function explicitly handles this via the null checks and branches to `one_priority` /
   `two_priority`.
4. Every non-null `Graphics_Window*` referenced (and reached by `get_graphics_window__p_root_parent`)
   has a *valid* parent chain: each `graphics_window__parent__uuid` either is invalid
   (`IDENTIFIER__UNKNOWN__u32`, marking a root/orphan) or resolves to an existing `Graphics_Window`
   in the manager. (If this is violated the engine crashes inside the callee — see Implementation
   Correctness.)
5. The call only occurs within `sort_graphic_windows_in__graphic_window_manager`, operating on
   `&manager->ptr_array_of__sorted_graphic_windows` of length
   `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` (8).

## 4. Post-conditions
1. Returns a `Signed_Quantity__i32`:
   - negative → `p_one` sorts before `p_two` (p_one renders first / has higher render priority).
   - positive → `p_two` sorts before `p_one` (p_two renders first).
   - zero → equal ordering (only reachable for the identical-slot duplicate, handled under `NDEBUG`).
2. `p_context` (the manager) is not modified by this function itself (it is read-only; any
   mutation of parent uuids happens inside the *callee* `get_graphics_window__p_root_parent`
   on a broken chain, not here).
3. The compared `Graphics_Window` structs are not mutated by this function.

## 5. Correctness Verdict
**Correct**

The comparator correctly implements the intended render-order heuristic over valid input:
parent-before-child, sibling/root/disjoint-ancestor ordering by ascending Z, with nulls
gracefully demoted. See the notes in Semantic Alignment / Implementation Correctness for
edge-case and defensive issues that do not invalidate the ordering on valid input.

## 6. Semantic Alignment
The implementation fulfills the semantic intent:
- **Parent-before-child:** when `GET_UUID_P(one) == two->parent_uuid` (one is the parent),
  it goes to `two_priority` → returns `-1` → one (the parent) sorts first. The mirror case
  (`two` is the parent) goes to `one_priority` → returns `+1` → two (the parent) sorts first.
  Both are correct under the ascending heap-sort convention.
- **Siblings** (equal `graphics_window__parent__uuid`) and **roots** both goto `sort_by_z`,
  returning `one.z - two.z` (lower Z renders first / is drawn earliest). Consistent.
- **Childless orphans** (both) goto `sort_by_z`. Consistent.
- **Sole root vs. non-root:** the sole root is demoted (non-root renders first via
  `one_priority`/`two_priority`). This is a deliberate prioritization choice, internally
  consistent.
- **Disjoint ancestors:** the loop walks each window's parent chain toward the common root,
  decrementing each side's depth independently starting from its own tree-depth. Because both
  depths start at their respective tree-depths and decrement in lock-step, at iteration `k`
  both pointers reference the ancestor *k steps below the root* — i.e., ancestors at the same
  depth. The loop exits at the first depth where they differ, and those least-disjoint
  ancestors are compared by Z. This correctly identifies the pair of lateral ancestors that
  share a common parent, matching the comment's intent.

**Alignment findings (non-logic):**
- The `one_priority` label returns `+1` (which actually *demotes* one / promotes two) and
  `two_priority` returns `-1` (which actually *promotes* one / demotes two). The labels are
  inverted relative to the concrete render effect under this ascending sort. The *logic* is
  correct, but the labels are misleading and could confuse future maintainers.
- The duplicate-slot guard `if (pv_graphics_window__one == pv_graphics_window__two)` compares
  the `void*` *slot addresses* (only true when the same array index is passed twice), not the
  dereferenced window pointers. Genuine duplicate window pointers in two slots are not
  detected here, but they are harmlessly handled elsewhere: two equal windows share the same
  parent uuid → hit the sibling branch and return 0.

## 7. Implementation Correctness
- **Type compatibility:** fully compatible.
  - `position_of__gfx_window.z__i32` is `Signed_Index__i32` (`int32_t`); `one.z - two.z`
    promotes to `int` on the target platform and is returned as `Signed_Quantity__i32`
    (`int32_t`) with no truncation for realistic screen coordinates.
  - `1`/`-1` integer literals convert to `Signed_Quantity__i32` cleanly.
  - `GET_UUID_P(...)` expands to `((Serialization_Header*)p)->uuid` (`Identifier__u32` /
    `uint32_t`), compared against `graphics_window__parent__uuid` (`Identifier__u32`) —
    exact match. `Graphics_Window` begins with `Serialization_Header _serialization_header;`,
    so the cast is valid.
  - `pv_graphics_window__one/two` are dereferenced as `*(Graphics_Window**)` matching the
    `sizeof(Graphics_Window*)` stride used by `heap_sort__opaque`. Correct.
- **Undefined behavior / null dereference (latent, callee-owned):**
  The disjoint-parent result is dereferenced unconditionally at lines 596–599
  (`p_disjoint_parent_one->position_of__gfx_window.z__i32 - p_disjoint_parent_two->...`).
  This is safe *in practice* for valid parent chains (the callee
  `get_graphics_window__p_root_parent` always returns a non-null pointer for non-broken
  chains — either the root ancestor, or the window itself when it has no parent), but there
  is **no explicit null guard**. A defensive `if (!p_one || !p_two)` fallback to
  `sort_by_z` (or returning 0) would make the function robust to a callee that ever returns
  null.
  Compounding this, the callee `get_graphics_window__p_root_parent` (line 668) itself
  contains a genuine null-pointer dereference in its broken-chain handler
  (line 695: `p_graphics_window__current_parent->graphics_window__parent__uuid = ...`
  immediately after testing `if (!p_graphics_window__current_parent)`). Because the callee
  *crashes* on a broken chain rather than returning null, the f_sort_heuristic dereference at
  596–599 is currently never reached with a null; but this is fragile and the callee bug
  should be fixed (return null cleanly, then guard here).
- **Dead/ineffective code:** the "Disjoint chain try again" blocks (lines 568–575 and
  581–588) re-invoke `get_graphics_window__p_root_parent` with a depth that was already
  overwritten by the first call (and, for broken chains, the callee crashes first), so these
  retries never change the outcome. They are dead code that obscures intent.
- **Out-of-bounds access:** none. Array indexing is performed only inside the callees
  (`get_graphics_window__p_root_parent` → `get_p_graphics_window_by__index_from__manager`),
  not in this function.
- **Validation appropriateness:** validation is reasonable for a comparator. Null windows
  are handled; the only un-guarded path requires an invalid parent chain (see above).

## 8. Side Effects
- No side effects of its own. This is a pure comparator with respect to its own code:
  `p_context` is only read (cast to `Graphics_Window_Manager*` and passed by pointer to
  read-only callees), and the `Graphics_Window` structs are only read.
- Out of scope (callee behavior, not this function's own observable effects): on a broken
  parent chain, the callee `get_graphics_window__p_root_parent` *writes*
  `graphics_window__parent__uuid = IDENTIFIER__UNKNOWN__u32` to orphan the window (and
  crashes doing so — see Implementation Correctness). This is a side effect of the callee,
  not of `f_sort_heuristic__p_graphics_window` itself.
