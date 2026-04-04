# Specification: core/include/sort/heap_sort__opaque.h

## Overview

Provides a blocking, opaque heap sort function that operates on arbitrary
contiguous arrays of any element type. Unlike the cooperative `Sort_List`
system, this function runs to completion in a single call and does not
integrate with the process scheduler.

This is intended for use cases where the sort must complete within a single
frame or initialization step, and where the data is not stored in
`Sort_Node` structures.

## Dependencies

- `defines.h` (for `Quantity__u32`, `f_Sort_Heuristic__i32`,
  `f_Sort_Swap__Void`)
- `defines_weak.h` (forward declarations)

## Types

### f_Sort_Heuristic__i32 (function pointer)

    typedef Signed_Quantity__i32 (*f_Sort_Heuristic__i32)(
            void *p_context,
            void *p_one,
            void *p_two);

Comparison function for opaque sorting. Returns a signed integer indicating
the relative ordering of two elements. `p_context` is an opaque pointer
(e.g. `Game*`, a manager, etc.) passed through from the caller.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_context` | `void*` | Opaque context pointer forwarded from the caller. |
| `p_one` | `void*` | Pointer to the first element to compare. |
| `p_two` | `void*` | Pointer to the second element to compare. |

**Return value**: Negative if `p_one` should precede `p_two`, positive if
`p_two` should precede `p_one`, zero if equal.

### f_Sort_Swap__Void (function pointer)

    typedef void (*f_Sort_Swap__Void)(
            void *p_context,
            void *p_one,
            void *p_two);

Swap function for opaque sorting. Swaps the contents of two elements.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_context` | `void*` | Opaque context pointer forwarded from the caller. |
| `p_one` | `void*` | Pointer to the first element to swap. |
| `p_two` | `void*` | Pointer to the second element to swap. |

## Functions

### heap_sort__opaque

    void heap_sort__opaque(
            void *p_context,
            void *p_ptr_array,
            Quantity__u32 size_of__type,
            Quantity__u32 size_of__array,
            f_Sort_Heuristic__i32 f_sort_heuristic__void,
            f_Sort_Swap__Void f_sort_swap__void);

Performs a complete heap sort on a contiguous array of opaque elements.
This function blocks until the sort is finished.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_context` | `void*` | Opaque context pointer passed to heuristic and swap functions. |
| `p_ptr_array` | `void*` | Pointer to the start of the contiguous array to sort. |
| `size_of__type` | `Quantity__u32` | Size in bytes of each element in the array. |
| `size_of__array` | `Quantity__u32` | Number of elements in the array. |
| `f_sort_heuristic__void` | `f_Sort_Heuristic__i32` | Comparison function for element ordering. |
| `f_sort_swap__void` | `f_Sort_Swap__Void` | Swap function for exchanging two elements. |

## Agentic Workflow

### When to Use

Use `heap_sort__opaque` when:

- The sort **must** complete within a single invocation (no cooperative
  scheduling).
- The data is stored in a plain contiguous array, not in `Sort_Node`
  structures.
- The caller can tolerate blocking for the duration of the sort.

Do **not** use `heap_sort__opaque` when:

- The sort can be spread across multiple frames. Use the `Sort_List` +
  `Process_Manager` cooperative system instead.
- The data is already managed by `Sort_Node` / `Sort_List` structures.

### Usage Pattern

    // Example: sort an array of Sprite_Render_Record by depth
    heap_sort__opaque(
            p_game,                         // context
            p_sprite_render_records,        // array
            sizeof(Sprite_Render_Record),   // element size
            quantity_of__records,            // element count
            f_compare_sprite_depth,         // heuristic
            f_swap_sprite_records);         // swap

### Preconditions

- `p_ptr_array` must point to a valid contiguous array of at least
  `size_of__array` elements, each of `size_of__type` bytes.
- `f_sort_heuristic__void` must not be null.
- `f_sort_swap__void` must not be null.
- `size_of__array` of 0 or 1 is a no-op.

### Postconditions

- The array pointed to by `p_ptr_array` is sorted according to the
  ordering defined by `f_sort_heuristic__void`.
- No allocations are performed. The sort is in-place.

### Performance

- Time complexity: O(N log N) worst case.
- Space complexity: O(1) auxiliary (in-place).
- **Blocking**: This function does not yield. On constrained hardware
  (e.g. Nintendo DS), large arrays may cause frame drops.

### Error Handling

- Null function pointers or invalid array pointers result in undefined
  behavior. Debug builds should validate arguments before calling.
