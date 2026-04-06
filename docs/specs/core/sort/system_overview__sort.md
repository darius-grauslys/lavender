# 1. System Overview: Cooperative Sort System

## 1.1 Purpose

The cooperative sort system provides a pool-managed, incremental sorting
framework designed for single-core, memory-constrained hardware. Instead of
blocking for the full duration of an O(N log N) sort, the system spreads
sorting work across multiple frames by performing one algorithmic step per
invocation. This integrates with the engine's `Process_Manager` to prevent
frame drops during large sorts.

A secondary, blocking opaque sort function is also provided for cases where
sorting must complete within a single call.

## 1.2 Architecture

### 1.2.1 Data Hierarchy

    Game
    └── Sort_List_Manager
        ├── sort_lists[0..SORT_LIST__MAXIMUM_QUANTITY_OF-1]   (Sort_List pool)
        │   ├── Sort_Data                (algorithm-specific state, e.g. heap indices)
        │   ├── f_Sort_Heuristic         (pluggable comparison function)
        │   ├── m_Sort                   (pluggable sort stepper function)
        │   ├── p_sort_list__next        (extension chain to another Sort_List)
        │   └── p_node_list ─────────────► contiguous range in sort_nodes[]
        │
        └── sort_nodes[0..SORT_NODE__MAXIMUM_QUANTITY_OF-1]   (Sort_Node pool)
            ├── p_node_data              (opaque pointer to user data)
            ├── heuristic_value          (signed 16-bit ordering value)
            └── index_for__next_node     (15-bit index-based linked list link)

### 1.2.2 Key Types

| Type | Role |
|------|------|
| `Sort_List_Manager` | Top-level resource owner. Lives in `Game`. Holds fixed-size pools of both `Sort_List` and `Sort_Node` instances. All sort resources are allocated and released through this manager. |
| `Sort_List` | A logical sorted collection. Owns a contiguous range of `Sort_Node` elements from the manager's node pool. Holds a pluggable heuristic and sort stepper. Supports extension chaining via `p_sort_list__next`. |
| `Sort_Node` | The leaf-level element. Holds an opaque data pointer, a heuristic value for ordering, and an index-based link to the next node. Allocated contiguously and referenced by index rather than pointer. |
| `Sort_Data` | A union embedded in `Sort_List` that holds algorithm-specific auxiliary state. Currently contains heap sort indices (`index_of__heapification`, `index_of__heap_sort`). |
| `f_Sort_Heuristic` | Function pointer type for comparing two `Sort_Node` elements. Returns a signed integer indicating relative ordering. |
| `m_Sort` | Function pointer type for the sort stepper. Each invocation performs one incremental step. Returns `true` when the sort is complete. |

### 1.2.3 Standalone Opaque Sort

| Type | Role |
|------|------|
| `f_Sort_Heuristic__i32` | Function pointer for comparing two opaque elements with a context pointer. Used by the blocking opaque sort. |
| `f_Sort_Swap__Void` | Function pointer for swapping two opaque elements. Used by the blocking opaque sort. |
| `heap_sort__opaque` | Blocking heap sort function that operates on arbitrary contiguous arrays. Does not use `Sort_List` or `Sort_Node`. |

### 1.2.4 Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `SORT_LIST__MAXIMUM_QUANTITY_OF` | 64 | Maximum number of sort lists in the pool. |
| `SORT_NODE__MAXIMUM_QUANTITY_OF` | 512 | Maximum number of sort nodes in the pool. |
| `INDEX__UNKNOWN__SORT_NODE` | `INDEX__UNKNOWN__u16 >> 1` | Sentinel value for "no next node" in the 15-bit index field. |

## 1.3 Cooperative Sorting Model

### 1.3.1 Why Cooperative?

On single-core hardware (e.g. Nintendo DS), a blocking O(N log N) sort on a
large dataset can cause visible frame drops. The cooperative model avoids this
by splitting the sort into many small steps:

- Each call to `m_sort` (via `run_sort__once`) performs **one step** of the
  sort algorithm.
- A `Process` handler calls `run_sort__once` or
  `run_sort_with__this_many_steps` each poll cycle, budgeting a fixed number
  of steps per frame.
- The total O(N log N) work is spread across many frames, keeping each
  frame's sort cost constant.

### 1.3.2 Pluggable Algorithms

The sort stepper (`m_Sort`) is a function pointer, allowing different sort
algorithms to be plugged in. The engine currently provides:

| Algorithm | Stepper Function | Initialization | Use Case |
|-----------|-----------------|----------------|----------|
| Heapify only | `m_sort__heapify__sort_list` | `initialize_sort_list_as__heap` | Build a max-heap; extract only the root (priority queue). |
| Full heap sort | `m_sort__heap_sort__sort_list` | `initialize_sort_list_as__heap_sort` | Sort the entire list in ascending order. |

Additional algorithms can be added by implementing the `m_Sort` signature and
using the `Sort_Data` union for algorithm-specific state.

### 1.3.3 Blocking vs Cooperative

| Function | Behavior | Use Case |
|----------|----------|----------|
| `run_sort` | Blocking (runs to completion) | Initialization, non-time-critical paths. |
| `run_sort__once` | One step | Process handler per-frame invocation. |
| `run_sort_with__this_many_steps` | Up to N steps | Budgeted per-frame sorting. |
| `run_sort_with__this_heurisitic_and__this_many_steps` | Up to N steps with temporary heuristic override | Re-sorting with a different comparison. |
| `heap_sort__opaque` | Blocking (runs to completion) | Sorting plain arrays outside the `Sort_List` system. |

## 1.4 Lifecycle

### 1.4.1 Manager Initialization

    initialize_sort_list_manager(&game.sort_list_manager);
        -> All Sort_List slots: cleared, is_allocated = false.
        -> All Sort_Node slots: cleared, is_allocated = false.
        -> Allocation counters: set to zero.

### 1.4.2 Sort List Allocation

When a subsystem needs a sorted collection:

    Sort_List *p_sort_list =
        allocate_sort_list_in__sort_list_manager(
            &game.sort_list_manager,
            quantity_of__nodes);

        -> Finds an unallocated Sort_List slot.
        -> Finds a contiguous range of unallocated Sort_Nodes
           of the requested size.
        -> Calls initialize_sort_list_as__allocated with the
           node range, heuristic, and size.
        -> Returns the allocated Sort_List, or NULL on failure.

**Contiguous allocation requirement**: The node pool can fragment over time.
If insufficient contiguous nodes are available, allocation fails even if the
total number of free nodes is sufficient. Callers should release sort lists
promptly and allocate large lists early.

### 1.4.3 Algorithm Configuration

After allocation, configure the sort algorithm:

    // For heap sort:
    initialize_sort_list_as__heap_sort(p_sort_list);
    set_sort_list__sort_heuristic(p_sort_list, my_heuristic);

    // For heapify only:
    initialize_sort_list_as__heap(p_sort_list);
    set_sort_list__sort_heuristic(p_sort_list, my_heuristic);

### 1.4.4 Data Population

Populate the sort nodes with data:

    // Option A: Point nodes to a contiguous data range
    point_sort_list__sort_nodes_to__this_range(
        p_sort_list,
        p_data_array,
        sizeof(Element));
        -> Each Sort_Node's p_node_data is set to sequential
           elements in the array, stepping by stride bytes.

    // Option B: Insert elements individually
    append_into__sort_list(p_sort_list, p_data);   // O(lg N)
    insert_into__sort_list(p_sort_list, p_data, index);  // O(1)

### 1.4.5 Sorting (Cooperative)

Request sorting and drive it from a process handler:

    // Trigger a sort pass
    request_resorting_of__heap_sort(p_sort_list);

    // In a Process handler, called each frame:
    void m_my_sort_process(Process *p_proc, Game *p_game) {
        Sort_List *p_sl = p_proc->p_process_data;
        if (run_sort_with__this_many_steps(p_sl, 4)) {
            // Sort complete
            complete_process(p_proc);
        }
    }

### 1.4.6 Sorted Data Access

After sorting completes, traverse the sorted order:

    Sort_Node *p_node =
        get_p_sort_node_by__index_from__sort_list(p_sort_list, 0);
    while (p_node) {
        void *p_data = p_node->p_node_data;
        // ... use sorted data ...
        p_node = get_next_p_sort_node_from__sort_list(
            p_sort_list, p_node);
    }

### 1.4.7 Re-sorting After Mutation

If the underlying data changes (e.g. heuristic values updated):

    // For heapify only:
    request_resorting_of__heap(p_sort_list);

    // For full heap sort:
    request_resorting_of__heap_sort(p_sort_list);

    // Continue calling m_sort steps until complete.

### 1.4.8 Sort List Release

When the sorted collection is no longer needed:

    release_sort_list_in__sort_list_manager(
        &game.sort_list_manager,
        p_sort_list);

        -> The Sort_List and its Sort_Nodes are marked deallocated.
        -> Allocation counters are decremented.
        -> The slots are returned to the pool for reuse.

## 1.5 Full Lifecycle Diagram

    [Manager Initialized]
            |
    allocate_sort_list_in__sort_list_manager(quantity_of__nodes)
            |
    [Sort_List Allocated, Sort_Nodes Allocated]
            |
    initialize_sort_list_as__heap_sort / initialize_sort_list_as__heap
    set_sort_list__sort_heuristic
            |
    [Algorithm Configured]
            |
    point_sort_list__sort_nodes_to__this_range
      or append_into__sort_list / insert_into__sort_list
            |
    [Nodes Populated]
            |
    request_resorting_of__heap_sort / request_resorting_of__heap
            |
    [Sorting] <-- run_sort__once / run_sort_with__this_many_steps (per frame)
            |
    (m_sort returns true)
            |
    [Sorted] -- (data mutated) --> request_resorting_of__heap_sort --> [Sorting]
            |
    release_sort_list_in__sort_list_manager
            |
    [Sort_List and Sort_Nodes Returned to Pool]

## 1.6 Index-Based Linking

Sort nodes reference each other by **index** into the contiguous `sort_nodes`
array in `Sort_List_Manager`, not by pointer. This design:

- Reduces memory usage on 32-bit platforms (15-bit index vs 32-bit pointer).
- Enables safe serialization of sort state if needed.
- Requires the `Sort_List` to resolve indices via
  `get_p_sort_node_by__index_from__sort_list`.

The sentinel value `INDEX__UNKNOWN__SORT_NODE` indicates "no next node" and
terminates the linked list.

## 1.7 Extension Chaining

Sort lists can be chained via `p_sort_list__next` to represent logical lists
larger than a single contiguous allocation:

    Sort_List A
      p_sort_list__next --> Sort_List B
                              p_sort_list__next --> Sort_List C
                                                      p_sort_list__next --> NULL

Use `is_sort_list__extexted` and `get_extension_of__sort_list` to traverse
the chain. The `Sort_List_Manager` can detect chaining via
`is_sort_node_a__sort_list`, which checks whether a `Sort_Node`'s
`p_node_data` points to a `Sort_List` within the manager's pool.

## 1.8 Heap Sort Algorithm Details

### 1.8.1 Heapify Phase

Transforms the node list into a valid max-heap. Each invocation of
`m_sort__heapify__sort_list` sifts one element into its correct heap
position. Progress is tracked by `Sort_Data.index_of__heapification`.
When `index_of__heapification == INDEX__UNKNOWN__SORT_NODE`, heapification
is complete.

- Total work: O(N), spread across O(N) cooperative steps.

### 1.8.2 Heap Sort Extraction Phase

After heapification, repeatedly extracts the maximum element:

1. `rotate_heap`: Swaps the root (max) with the last unsorted leaf.
2. Decrements `Sort_Data.index_of__heap_sort` (shrinks the unsorted region).
3. Re-heapifies the reduced heap.

When `index_of__heap_sort <= 1`, the list is fully sorted in ascending order.

- Total work: O(N log N), spread across O(N log N) cooperative steps.
- Space: O(1) auxiliary (in-place, using `Sort_Data` for state).

### 1.8.3 Priority Queue Usage

For priority queue behavior (repeated max extraction without full sorting):

1. `initialize_sort_list_as__heap` (heapify only).
2. Run `m_sort` steps until `is_heap__heapifed` returns true.
3. The root node contains the maximum element.
4. Call `rotate_heap` to extract the max.
5. Call `request_resorting_of__heap` to restore the heap property.
6. Repeat from step 2.

## 1.9 Opaque Heap Sort

The `heap_sort__opaque` function provides a separate, blocking heap sort for
plain contiguous arrays that are not managed by the `Sort_List` system:

    heap_sort__opaque(
        p_context,              // opaque context for callbacks
        p_array,                // pointer to contiguous array
        sizeof(Element),        // element size in bytes
        quantity_of__elements,  // element count
        f_compare,              // f_Sort_Heuristic__i32 comparator
        f_swap);                // f_Sort_Swap__Void swapper

This function:

- Runs to completion in a single call (blocking).
- Does not use `Sort_List`, `Sort_Node`, or `Sort_List_Manager`.
- Performs an in-place heap sort with O(N log N) time and O(1) space.
- Is suitable for initialization-time sorts or small arrays where frame
  budget is not a concern.

## 1.10 Capacity Constraints

- The `Sort_List_Manager` is the **sole owner** of all `Sort_List` and
  `Sort_Node` memory. No other system should allocate or free sort
  resources outside of this manager.
- Sort node allocation is **contiguous**: a sort list's nodes must occupy
  a contiguous range in the node pool. Fragmentation can cause allocation
  failures even when the total number of free nodes is sufficient.
- The maximum number of sort lists (64) and sort nodes (512) are
  compile-time constants.

## 1.11 Relationship to Process_Manager

The cooperative sort system is designed to be driven by the engine's
`Process_Manager`:

| Concern | Managed By |
|---------|------------|
| Sort list and node allocation | `Sort_List_Manager` |
| Algorithm configuration | `heap_sort.h` initialization functions |
| Per-frame sort stepping | `Process_Manager` -> process handler -> `run_sort__once` / `run_sort_with__this_many_steps` |
| Sort completion detection | `m_sort` return value (`true` = complete) |
| Resource release | `Sort_List_Manager` |

The `Process` handler is responsible for calling the sort stepper each frame
and releasing the sort list when sorting is complete or no longer needed.

## 1.12 Known Issues

- `get_quantity_of__available_sort_lists_in__sort_list_manager` subtracts
  `quantity_of__allocated_sort_nodes` from `SORT_LIST__MAXIMUM_QUANTITY_OF`,
  and `get_quantity_of__available_sort_nodes_in__sort_list_manager` subtracts
  `quantity_of__allocated_sort_lists` from `SORT_NODE__MAXIMUM_QUANTITY_OF`.
  These appear to have swapped subtrahends and may return incorrect values.

## 1.13 Error Handling

- `allocate_sort_list_in__sort_list_manager` returns NULL on failure (no free
  list slot, or insufficient contiguous nodes).
- All `static inline` accessor functions call `debug_abort` on null pointers
  in debug builds.
- `run_sort__once` calls `debug_abort` if `m_sort` is null in debug builds.
- `heap_sort__opaque` has no explicit error handling; null function pointers
  or invalid arrays result in undefined behavior.
