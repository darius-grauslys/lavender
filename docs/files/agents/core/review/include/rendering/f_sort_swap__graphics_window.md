# Function Review: f_sort_swap__graphics_window

## 1. Header
- **Function name:** `f_sort_swap__graphics_window`
- **File of origin:** `core/source/rendering/graphics_window_manager.c` (defined at line 610)

## 2. Semantic
Swaps two `Graphics_Window*` entries in the graphics window manager's sorted-windows array; it is the swap callback supplied to `heap_sort__opaque` when sorting `ptr_array_of__sorted_graphic_windows`.

## 3. Pre-conditions
1. `pv_graphics_window__one` is a non-null `Graphics_Window**` — i.e. a pointer to a valid `Graphics_Window*` slot (an element of `ptr_array_of__sorted_graphic_windows`).
2. `pv_graphics_window__two` is a non-null `Graphics_Window**` pointing to a valid `Graphics_Window*` slot.
3. Both pointers denote slots within the same `ptr_array_of__sorted_graphic_windows` array (guaranteed by the caller, `heap_sort__opaque`, which derives them as `&p_byte_array[size_of__type * index]`).
4. `p_context` is unused by this function and may be any value (including `NULL`).
5. The two slots need not be distinct; a self-swap is safe (see Implementation Correctness).

## 4. Post-conditions
1. The `Graphics_Window*` value previously stored at `*pv_graphics_window__one` is now stored at `*pv_graphics_window__two`, and vice versa; the two pointer slots are exchanged.
2. No other array slots are modified.
3. The `Graphics_Window` objects themselves are not moved, copied, allocated, or freed — only the pointer slots are rearranged.
4. The function returns `void`.

## 5. Correctness Verdict
Correct

## 6. Semantic Alignment
The function's intent — by its name and by its role as the `f_sort_swap__void` callback passed to `heap_sort__opaque` (call at `graphics_window_manager.c:631`) — is to exchange two graphics-window entries. The implementation performs an exact 3-way swap of the two `Graphics_Window*` values obtained by dereferencing the supplied `Graphics_Window**` pointers. This fulfills the semantic intent with no missing/omitted struct fields (it is not a struct initializer) and no ordering drift. (Initialization ≠ RAII: not applicable — this is a swap, not an init/reset function.)

## 7. Implementation Correctness
- **Type compatibility:** `heap_sort__opaque` passes `&p_byte_array[size_of__type * index]` for each element; since `ptr_array_of__sorted_graphic_windows` is declared `Graphics_Window*[]` (`defines.h:2515`), every such address is a `Graphics_Window**`. The `void *` → `Graphics_Window **` cast in this function is exact — there is no implicit conversion, sign change, or truncation. The function's signature `(void *p_context, void *pv_graphics_window__one, void *pv_graphics_window__two)` matches the `f_Sort_Swap__Void` typedef exactly (`void (*)(void *, void *, void *)` at `defines.h:1411-1414`). ✓
- **Undefined behavior:** Within the function only the two caller-provided pointers are dereferenced; both are guaranteed valid intra-array element addresses by the heap sort. The 3-way swap is self-assignment safe: if the two pointers addressed the same slot, the temp exchange is a harmless no-op (store A → assign A → restore A). No pointer arithmetic, no type punning, no out-of-bounds, no null dereference inside the function body. ✓
- **Validation:** No null/length checks are performed. This is appropriate for the function's role — `heap_sort__opaque` owns the responsibility of supplying valid element addresses; this function is a leaf swap callback. Adding defensive checks here would be out of scope and inconsistent with the engine's "validate at the orchestrator" convention (cf. the heuristic's intrinsic check at `graphics_window_manager.c:463` living in the caller layer, not here). ✓

## 8. Side Effects
- Mutates exactly two slots of `ptr_array_of__sorted_graphic_windows`: the stored `Graphics_Window*` values are exchanged. All other slots, the `Graphics_Window` objects, the manager's other fields, and global state are untouched.
- No allocation, no I/O, no deallocation.
- `p_context` is unused (read in the ABI sense only).

## Related Finding (not a defect of this function)
`heap_sort__opaque` has a parameter-order discrepancy between its header and its definition, which affects callers of this swap rather than the swap itself:

- Header (`core/include/sort/heap_sort__opaque.h:13-14`) names positional params `(…, size_of__type, size_of__array, …)`.
- Definition (`core/source/sort/heap_sort__opaque.c:7-8`) names them `(…, length_of__array, size_of__type, …)` and uses the **3rd** positional arg as the array length and the **4th** as the element byte size.

This is consistent and harmless for the `sprite_manager.c:344` call, which passes *length* in arg 3 and *element size* in arg 4 — matching the definition's usage. But the `graphics_window_manager.c:631` call passes `sizeof(Graphics_Window*)` in arg 3 and `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` in arg 4 — i.e. in header-name order. The definition therefore interprets the array length as `sizeof(Graphics_Window*)` and the element size as the max count.

On the current 64-bit target this is **masked by numerical coincidence**: `sizeof(Graphics_Window*)` == `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` == `8` (`defines.h:2468`), so the sort reads/writes the correct locations. It is a latent bug that would surface (out-of-bounds access) if `MAX_QUANTITY_OF__GRAPHICS_WINDOWS` were ever changed away from 8 or if the target pointer size differed. This defect belongs to a `heap_sort__opaque` / call-site review, not to `f_sort_swap__graphics_window`; the swap itself operates correctly on whatever element addresses it is handed.
