# Specification: core/include/sort/sort_list/heap_sort.h

## Overview

Provides heap-based cooperative sorting algorithms for `Sort_List`. This
module implements two related algorithms:

1. **Heapify** (`m_sort__heapify__sort_list`): Transforms an unsorted
   `Sort_List` into a valid max-heap, one step at a time.
2. **Heap Sort** (`m_sort__heap_sort__sort_list`): Performs a full heap
   sort (heapify + repeated extraction), one step at a time.

Both algorithms are designed to be driven cooperatively by the
`Process_Manager`, performing a single step per invocation to avoid
blocking on single-core hardware.

## Dependencies

- `defines.h` (for `Sort_List`, `Sort_Data`, `Sort_Node`,
  `Index__u16`, `INDEX__UNKNOWN__SORT_NODE`)
- `sort/sort_list/sort_list.h` (for `Sort_List` accessors)

## Types

This module does not define new types. It operates on `Sort_List` and
uses the `Sort_Data` union's heap-specific fields:

### Sort_Data — Heap Fields

    typedef union Sort_Data_t {
        struct {
            Index__u16 index_of__heapification;
            Index__u16 index_of__heap_sort;
        };
    } Sort_Data;

| Field | Type | Description |
|-------|------|-------------|
| `index_of__heapification` | `Index__u16` | Tracks the current position in the heapify pass. Set to `INDEX__UNKNOWN__SORT_NODE` when heapification is complete. |
| `index_of__heap_sort` | `Index__u16` | Tracks the current unsorted boundary in the heap sort extraction pass. Decremented each extraction step. Sort is complete when `<= 1`. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_sort_list_as__heap` | `(Sort_List*) -> void` | Configures the sort list for heapify-only operation. Sets `m_sort` to `m_sort__heapify__sort_list`. |
| `initialize_sort_list_as__heap_sort` | `(Sort_List*) -> void` | Configures the sort list for full heap sort operation. Sets `m_sort` to `m_sort__heap_sort__sort_list`. |

### Heap Operations

| Function | Signature | Description |
|----------|-----------|-------------|
| `rotate_heap` | `(Sort_List*) -> void` | Swaps the root node with the last leaf node. Must be followed by `request_resorting_of__heap` to restore the heap property. Used for extracting the max element. |
| `request_resorting_of__heap` | `(Sort_List*) -> void` | Resets `index_of__heapification` to trigger a full re-heapify on the next sort step. |
| `request_resorting_of__heap_sort` | `(Sort_List*) -> void` | Resets both `index_of__heapification` and `index_of__heap_sort` to trigger a full heap sort from scratch on the next sort step. |

### Sort Steppers (m_Sort implementations)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `m_sort__heapify__sort_list` | `(Sort_List*) -> bool` | `bool` | Performs one step of the heapify algorithm. Returns `true` when the heap property is fully established. |
| `m_sort__heap_sort__sort_list` | `(Sort_List*) -> bool` | `bool` | Performs one step of the heap sort algorithm (heapify + extraction). Returns `true` when the list is fully sorted. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sort_data__heapifed` | `(Sort_Data*) -> bool` | `bool` | Returns `true` if `index_of__heapification == INDEX__UNKNOWN__SORT_NODE`, meaning heapification is complete. |
| `is_heap__heapifed` | `(Sort_List*) -> bool` | `bool` | Convenience wrapper: returns `is_sort_data__heapifed(&p_sort_list->sort_data)`. |
| `get_index_of__heap_sort_from__sort_data` | `(Sort_Data*) -> Index__u16` | `Index__u16` | Returns `index_of__heap_sort`. |
| `get_index_of__heap_sort_from__sort_list` | `(Sort_List*) -> Index__u16` | `Index__u16` | Convenience wrapper: returns `get_index_of__heap_sort_from__sort_data(&p_sort_list->sort_data)`. |
| `is_heap_sort__sorted` | `(Sort_List*) -> bool` | `bool` | Returns `true` if `index_of__heap_sort <= 1`, meaning the heap sort is complete. |

## Agentic Workflow

### Algorithm Overview

#### Heapify Only (`m_sort__heapify__sort_list`)

Transforms the node list into a max-heap. Each invocation sifts one
element into its correct heap position. After completion, the root
contains the maximum element according to `f_sort_heuristic`.

    [Unsorted List]
         |
    initialize_sort_list_as__heap
         |
    request_resorting_of__heap
         |
    [Heapifying] <-- m_sort__heapify__sort_list (one step per call)
         |
    (is_heap__heapifed returns true)
         |
    [Valid Max-Heap]

#### Full Heap Sort (`m_sort__heap_sort__sort_list`)

Performs a complete heap sort: first heapifies, then repeatedly extracts
the maximum element. Each invocation performs one step of either the
heapify or extraction phase.

    [Unsorted List]
         |
    initialize_sort_list_as__heap_sort
         |
    request_resorting_of__heap_sort
         |
    [Heapifying] <-- m_sort__heap_sort__sort_list (one step per call)
         |
    (is_heap__heapifed returns true)
         |
    [Extracting] <-- m_sort__heap_sort__sort_list (one step per call)
         |              rotate_heap (swap root with last unsorted)
         |              decrement index_of__heap_sort
         |              re-heapify reduced heap
         |
    (is_heap_sort__sorted returns true)
         |
    [Fully Sorted]

### Cooperative Scheduling Integration

Both sort steppers conform to the `m_Sort` signature and are designed
to be called from a `Process` handler:

    void m_my_sort_process(Process *p_proc, Game *p_game) {
        Sort_List *p_sl = p_proc->p_process_data;
        if (run_sort_with__this_many_steps(p_sl, 4)) {
            // Sort complete
            complete_process(p_proc);
        }
    }

Each call to `run_sort_with__this_many_steps` invokes `m_sort` up to
the specified number of times, allowing fine-grained control over how
much sorting work is done per frame.

### Heapify vs Heap Sort

| Use Case | Algorithm | Function |
|----------|-----------|----------|
| Need only the max (or min) element | Heapify only | `initialize_sort_list_as__heap` |
| Need the full list sorted | Heap sort | `initialize_sort_list_as__heap_sort` |
| Priority queue (repeated max extraction) | Heapify + manual `rotate_heap` | `initialize_sort_list_as__heap` + `rotate_heap` + `request_resorting_of__heap` |

### Re-sorting After Mutation

If the data changes after sorting (e.g. heuristic values updated):

1. Call `request_resorting_of__heap` (heapify only) or
   `request_resorting_of__heap_sort` (full sort).
2. Continue calling `m_sort` steps until complete.

### Preconditions

- `initialize_sort_list_as__heap` / `initialize_sort_list_as__heap_sort`:
  `p_sort_list` must be allocated and have a valid `p_node_list`.
- `rotate_heap`: the list must be a valid heap (heapification complete).
  Must be followed by `request_resorting_of__heap`.
- `request_resorting_of__heap` / `request_resorting_of__heap_sort`:
  `p_sort_list` must be allocated.
- All query functions require non-null arguments.

### Postconditions

- After `m_sort__heapify__sort_list` returns `true`: the node list
  satisfies the max-heap property according to `f_sort_heuristic`.
- After `m_sort__heap_sort__sort_list` returns `true`: the node list
  is fully sorted in ascending order according to `f_sort_heuristic`.
- After `rotate_heap`: the former root is at the last leaf position;
  the heap property is **violated** until re-heapified.

### Performance

- Heapify: O(N) total work, spread across O(N) cooperative steps.
- Heap sort: O(N log N) total work, spread across O(N log N) cooperative
  steps.
- Space: O(1) auxiliary (in-place, using `Sort_Data` for state).

### Error Handling

- No explicit error handling in the current implementation. Null
  pointers or uninitialized sort lists result in undefined behavior.
- Debug builds should validate arguments before calling these functions.
