# Specification: core/include/sort/sort_list/sort_list.h

## Overview

Provides initialization, manipulation, and cooperative sorting for
`Sort_List` — a linked list of `Sort_Node` elements that supports
incremental (one-step-per-invocation) sorting via pluggable sort
algorithms.

`Sort_List` is the primary data structure for the engine's cooperative
sorting system, designed to spread sorting work across multiple frames
on single-core hardware. Each `Sort_List` holds a contiguous array of
`Sort_Node` elements linked by index, a pluggable heuristic function,
and a pluggable sort stepper function.

## Dependencies

- `defines.h` (for `Sort_List`, `Sort_Node`, `Sort_Data`,
  `f_Sort_Heuristic`, `m_Sort`, `Quantity__u32`, `Index__u16`,
  `INDEX__UNKNOWN__SORT_NODE`)
- `defines_weak.h` (forward declarations)
- `sort/sort_list/sort_node.h` (for `Sort_Node` accessors)
- `debug/debug.h` (for `debug_abort` in debug builds)

## Types

### Sort_List (struct)

    typedef struct Sort_List_t {
        Sort_Node *p_node_list;
        f_Sort_Heuristic f_sort_heuristic;
        m_Sort m_sort;
        struct Sort_List_t *p_sort_list__next;
        Quantity__u32 size_of__p_node_list  :31;
        bool is_allocated                   :1;
        Sort_Data sort_data;
    } Sort_List;

| Field | Type | Width | Description |
|-------|------|-------|-------------|
| `p_node_list` | `Sort_Node*` | pointer | Pointer to the contiguous array of sort nodes owned by this list. |
| `f_sort_heuristic` | `f_Sort_Heuristic` | pointer | Comparison function used to determine node ordering. |
| `m_sort` | `m_Sort` | pointer | Pluggable sort stepper. Invoked once per cooperative step. |
| `p_sort_list__next` | `Sort_List*` | pointer | Extension pointer for chaining multiple sort lists. |
| `size_of__p_node_list` | `Quantity__u32` | 31 bits | Number of nodes in `p_node_list`. |
| `is_allocated` | `bool` | 1 bit | True if this sort list is currently allocated. |
| `sort_data` | `Sort_Data` | union | Algorithm-specific auxiliary data (e.g. heap indices). |

### Sort_Data (union)

    typedef union Sort_Data_t {
        struct { // Heapsort
            Index__u16 index_of__heapification;
            Index__u16 index_of__heap_sort;
        };
    } Sort_Data;

| Field | Type | Description |
|-------|------|-------------|
| `index_of__heapification` | `Index__u16` | Current index for the heapify pass. `INDEX__UNKNOWN__SORT_NODE` when heapification is complete. |
| `index_of__heap_sort` | `Index__u16` | Current index for the heap sort extraction pass. |

### f_Sort_Heuristic (function pointer)

    typedef Signed_Quantity__i32 (*f_Sort_Heuristic)(
            Sort_Node *p_node__one,
            Sort_Node *p_node__two);

Comparison function for `Sort_Node`-based sorting. Returns a signed
integer indicating relative ordering.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_node__one` | `Sort_Node*` | First node to compare. |
| `p_node__two` | `Sort_Node*` | Second node to compare. |

**Return value**: Negative if `p_node__one` should precede `p_node__two`,
positive if `p_node__two` should precede `p_node__one`, zero if equal.

### m_Sort (function pointer)

    typedef bool (*m_Sort)(
            Sort_List *p_this_sort_list);

Pluggable sort stepper. Each invocation performs one incremental step
of the sort algorithm.

| Parameter | Type | Description |
|-----------|------|-------------|
| `p_this_sort_list` | `Sort_List*` | The sort list being sorted. |

**Return value**: `true` if the sort is fully complete, `false` if more
steps are needed.

### Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `SORT_LIST__MAXIMUM_QUANTITY_OF` | 64 | Maximum number of sort lists in the pool. |
| `SORT_NODE__MAXIMUM_QUANTITY_OF` | 512 | Maximum number of sort nodes in the pool. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_sort_list_as__allocated` | `(Sort_List*, Sort_Node* p_node_list, f_Sort_Heuristic, Quantity__u32 size) -> void` | Full initialization. Sets the node list, heuristic, and size. Marks as allocated. |
| `initialize_sort_list_as__empty` | `(Sort_List*) -> void` | Clears all fields. Marks as deallocated. |

### Data Population

| Function | Signature | Description |
|----------|-----------|-------------|
| `point_sort_list__sort_nodes_to__this_range` | `(Sort_List*, void* p_range, Quantity__u32 stride) -> void` | Points each sort node's `p_node_data` to sequential elements in a contiguous range, stepping by `stride` bytes. Ignores `index_for__next_node` ordering. |

### Insertion and Removal

| Function | Signature | Time | Description |
|----------|-----------|------|-------------|
| `append_into__sort_list` | `(Sort_List*, void* p_data) -> void` | O(lg N) | Appends `p_data` at the back of the list. |
| `insert_into__sort_list` | `(Sort_List*, void* p_data, Index__u16 index) -> void` | O(1) | Inserts `p_data` at the given node index. |
| `remove_from__sort_list` | `(Sort_List*, void* p_data) -> void` | O(N) | Linearly searches for and removes the first node matching `p_data`. |

### Sorting

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `run_sort` | `(Sort_List*) -> void` | `void` | Runs the sort algorithm to completion (blocking). |
| `run_sort__once` | `(Sort_List*) -> bool` | `bool` | Runs one step of the sort. Returns `true` if complete. (static inline) |
| `run_sort_with__this_many_steps` | `(Sort_List*, Quantity__u32 steps) -> bool` | `bool` | Runs up to `steps` sort steps. Returns `true` if complete before exhausting steps. |
| `run_sort_with__this_heurisitic_and__this_many_steps` | `(Sort_List*, f_Sort_Heuristic, Quantity__u32 steps) -> bool` | `bool` | Temporarily overrides the heuristic and runs up to `steps` sort steps. Returns `true` if complete. |

### Node Access

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_index_of__sort_node_in__sort_list` | `(Sort_List*, Sort_Node*) -> Index__u16` | `Index__u16` | Returns the index of the given node within the list's node array. |
| `get_p_sort_node_by__index_from__sort_list` | `(Sort_List*, Index__u16) -> Sort_Node*` | `Sort_Node*` | Returns a pointer to the node at the given index. |
| `get_next_p_sort_node_from__sort_list` | `(Sort_List*, Sort_Node*) -> Sort_Node*` | `Sort_Node*` | Returns the next node in the linked list, or null if none. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_length_of__sort_list` | `(Sort_List*) -> Quantity__u32` | `Quantity__u32` | Returns `size_of__p_node_list`. |
| `is_sort_list__allocated` | `(Sort_List*) -> bool` | `bool` | Returns `true` if the list is allocated. |
| `is_sort_list__extexted` | `(Sort_List*) -> bool` | `bool` | Returns `true` if `p_sort_list__next` is non-null (list is extended/chained). |
| `get_extension_of__sort_list` | `(Sort_List*) -> Sort_List*` | `Sort_List*` | Returns `p_sort_list__next`. |
| `get_p_node_list_from__sort_list` | `(Sort_List*) -> Sort_Node*` | `Sort_Node*` | Returns `p_node_list`. |

### Allocation Management (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_sort_list_as__allocated` | `(Sort_List*) -> void` | Sets `is_allocated = true`. |
| `set_sort_list_as__deallocated` | `(Sort_List*) -> void` | Sets `is_allocated = false`. |

### Configuration (static inline)

| Function | Signature | Description |
|----------|-----------|-------------|
| `set_sort_list__sort_heuristic` | `(Sort_List*, f_Sort_Heuristic) -> void` | Sets the comparison heuristic function. |

## Agentic Workflow

### Cooperative Sorting Model

The `Sort_List` system is designed for **cooperative, non-preemptive**
sorting that integrates with the engine's `Process_Manager`:

- Each call to `m_sort` (via `run_sort__once`) performs **one step** of
  the sort algorithm.
- A process handler calls `run_sort__once` or
  `run_sort_with__this_many_steps` each poll cycle, spreading the O(N log N)
  work across multiple frames.
- This prevents frame drops on single-core hardware (e.g. Nintendo DS).

### Sort List Lifecycle

    [Unallocated]
         |
    allocate_sort_list_in__sort_list_manager
         |
    initialize_sort_list_as__allocated
         |
    [Allocated, Unsorted]
         |
    (populate nodes via point_sort_list__sort_nodes_to__this_range
     or append_into__sort_list / insert_into__sort_list)
         |
    [Allocated, Populated]
         |
    (set m_sort via initialize_sort_list_as__heap, etc.)
         |
    request_resorting_of__heap (or equivalent)
         |
    [Sorting]  <-- run_sort__once each frame
         |
    (m_sort returns true)
         |
    [Sorted]
         |
    release_sort_list_in__sort_list_manager
         |
    initialize_sort_list_as__empty
         |
    [Unallocated]

### Extension Chaining

Sort lists can be chained via `p_sort_list__next` to represent logical
lists larger than a single contiguous allocation. Use
`is_sort_list__extexted` and `get_extension_of__sort_list` to traverse
the chain.

### Blocking vs Cooperative

| Function | Behavior | Use Case |
|----------|----------|----------|
| `run_sort` | Blocking (runs to completion) | Initialization, non-time-critical paths |
| `run_sort__once` | One step | Process handler per-frame invocation |
| `run_sort_with__this_many_steps` | Up to N steps | Budgeted per-frame sorting |

### Preconditions

- All functions require a non-null `p_sort_list`. Debug builds call
  `debug_abort` on null.
- `run_sort__once`: `m_sort` must be non-null. Debug builds call
  `debug_abort` if null.
- `point_sort_list__sort_nodes_to__this_range`: the range must contain
  at least `size_of__p_node_list` elements of `stride` bytes each.
- `append_into__sort_list`, `insert_into__sort_list`: the list must have
  available (unallocated) nodes.

### Postconditions

- After `run_sort` or `run_sort__once` returning `true`: the node list
  is fully sorted according to `f_sort_heuristic`.
- After `initialize_sort_list_as__empty`: all fields are cleared,
  `is_allocated` is false.

### Error Handling

- All `static inline` functions call `debug_abort` on null in debug builds.
- `run_sort__once` calls `debug_abort` if `m_sort` is null in debug builds.
