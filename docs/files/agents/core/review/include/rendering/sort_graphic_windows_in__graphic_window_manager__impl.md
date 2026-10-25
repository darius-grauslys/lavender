1: # Function Review: sort_graphic_windows_in__graphic_window_manager

## 1. Header
- **Function name**: `sort_graphic_windows_in__graphic_window_manager`
- **File of origin**: `core/source/rendering/graphics_window_manager.c` (lines 629-638)

## 2. Semantic
Sorts the `ptr_array_of__sorted_graphic_windows` pointer array in-place within the
given `Graphics_Window_Manager`, ordering graphic window pointers by parent/child
hierarchy and Z-depth according to the heuristic `f_sort_heuristic__p_graphics_window`.

## 3. Pre-conditions
1. `p_graphics_window_manager` must be non-null and valid.
2. `p_graphics_window_manager->ptr_array_of__sorted_graphic_windows` must be
   populated with valid `Graphics_Window*` pointers (or NULL for unused slots).
3. Unused slots in the array must be NULL (0) so the heuristic's null checks
   function correctly.

## 4. Post-conditions
1. The pointers within
   `p_graphics_window_manager->ptr_array_of__sorted_graphic_windows` are reordered
   in-place into sorted order (ascending Z for siblings/orphans; parents before
   children in the hierarchy).
2. No `Graphics_Window` objects are modified — only the pointer array is rearranged.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The function's semantic intent (sort the pointer array via heap sort using the
provided heuristic and swap callbacks) is correct in conception. The delegation to
`heap_sort__opaque` with the right context, array, heuristic, and swap function is
appropriate. However, the third and fourth arguments are passed in the wrong order
(see Implementation Correctness), which breaks the actual execution.

## 7. Implementation Correctness

**CRITICAL BUG — Swapped arguments to `heap_sort__opaque`:**

The `heap_sort__opaque` signature is:
```c
void heap_sort__opaque(
        void *p_context,
        void *p_array,
        Quantity__u32 length_of__array,   // 3rd: count of elements
        Quantity__u32 size_of__type,      // 4th: byte size of each element
        f_Sort_Heuristic__i32 f_sort_heuristic__void,
        f_Sort_Swap__Void f_sort_swap__void);
```

The call at line 631-637 passes:
```c
heap_sort__opaque(
        p_graphics_window_manager,
        &p_graphics_window_manager->ptr_array_of__sorted_graphic_windows, 
        sizeof(Graphics_Window*),            // PASSED as 3rd (length_of__array) — WRONG
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS,  // PASSED as 4th (size_of__type) — WRONG
        f_sort_heuristic__p_graphics_window, 
        f_sort_swap__graphics_window);
```

The correct call should be:
```c
heap_sort__opaque(
        ...,
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS, // 3rd: length_of__array (count = 8)
        sizeof(Graphics_Window*),           // 4th: size_of__type (stride = 8)
        ...);
```

**Impact:**
- `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` is defined as `8`.
- On 64-bit: `sizeof(Graphics_Window*)` is also `8`, so both values are identical.
  The bug is **coincidentally masked** on 64-bit platforms — sorting happens to work
  because 8 elements with an 8-byte stride matches an 8-element pointer array.
- On 32-bit: `sizeof(Graphics_Window*)` is `4`. The heap sort would treat
  `length_of__array = 4` (only sorting half the array) and `size_of__type = 8`
  (double the correct stride), causing **out-of-bounds memory access** and
  incomplete sorting.
- If `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` is ever changed to any value other than 8,
  the function will break on all platforms.

The sibling caller in `sprite_manager.c:344-349` confirms the correct argument
order (count first, then `sizeof`), proving the graphics window manager call is
inverted.

**Type compatibility:** The `&p_graphics_window_manager->ptr_array_of__sorted_graphic_windows`
expression correctly yields a byte-addressable pointer for the opaque byte-array
traversal inside `heap_sort__opaque`; casting to `void*` is fine. No type
truncation issues on the pointer parameters.

**Undefined behavior:** Outside the swapped-argument bug (which causes OOB on
32-bit), there is no inherent UB in the function body. The heuristic and swap
callbacks handle null pointers defensively.

**Validation:** No null check on `p_graphics_window_manager` is performed. This is
acceptable — all call sites (lines 187, 276, 410) pass valid manager pointers,
making this the caller's responsibility rather than the function's.

## 8. Side Effects
Mutates `p_graphics_window_manager->ptr_array_of__sorted_graphic_windows` in-place:
reorders the `Graphics_Window*` pointers within the array. No `Graphics_Window`
structs are modified. No heap allocations or deallocations occur. No callee-side
effects beyond the array reordering (callee invocation of `heap_sort__opaque` is
the mechanism, not an additional side effect).
