heap_sort__opaque — core/source/sort/heap_sort__opaque.c

Performs an in-place heapsort on a generic array of elements, using caller-provided comparison and swap callbacks.

Pre-conditions:
1. p_array must be a non-null pointer to a writable contiguous block of memory holding the array to be sorted.
2. length_of__array must be the number of elements in the array (any non-negative value; values < 2 cause early return).
3. size_of__type must be the size in bytes of a single element of the array; must be > 0 (no explicit check, caller's responsibility).
4. f_sort_heuristic__void must be a non-null function pointer that compares two elements and returns a negative value if the first is less than the second, zero if equal, or positive if greater.
5. f_sort_swap__void must be a non-null function pointer that swaps the two elements pointed to by its arguments.
6. p_context may be NULL or a valid context pointer; it is passed through to the callback functions unchanged.

Post-conditions:
1. The array pointed to by p_array is sorted in ascending order according to f_sort_heuristic__void's comparison semantics.
2. p_array is mutated in place; no allocation or deallocation occurs.
3. If length_of__array < 2, the function returns immediately and the array is unchanged.
4. p_context is passed through to callbacks but is not modified by this function.

Correctness Verdict: Correct

Semantic Alignment:
The implementation correctly implements the heapsort algorithm. The heapify phase builds a max-heap by sifting down from the last non-leaf node (index length_of__array/2 - 1) to the root (index 0). The sort-down phase repeatedly extracts the maximum element (root) by swapping it with the last unsorted element and restoring the heap property on the reduced heap.

The loop `for (Quantity__u32 i = (length_of__array / 2); i-- > 0;)` correctly processes indices from length_of__array/2 - 1 down to 0, which is the standard starting point for bottom-up heapify on a 0-indexed array.

The heuristic comparison is used consistently: a return value of < 0 means the first argument is less than the second, and the swap is performed when the parent is less than the larger child, maintaining the max-heap property.

Implementation Correctness:
Type compatibility — p_array is cast from void * to unsigned char * for byte-level pointer arithmetic, which is standard practice. Element indexing uses size_of__type * index, which is correct. Quantity__u32 is used consistently for indices and sizes, matching the typedef in defines.h.

Undefined behavior — No null dereference (function pointers are assumed valid per caller responsibility). No out-of-bounds access: child index checks (child >= length_of__array and child >= i) prevent reading beyond array bounds. No type punning. Pointer arithmetic is performed on unsigned char *, which has well-defined semantics for byte-level access.

No validation of null function pointers or size_of__type == 0 is performed, but this is appropriate for a low-level sorting primitive where the caller is expected to provide valid callbacks and parameters.

Side Effects:
The array pointed to by p_array is mutated in place to be sorted in ascending order. No other memory is allocated or freed. p_context is not modified. The function has no side effects beyond reordering elements in the input array.
