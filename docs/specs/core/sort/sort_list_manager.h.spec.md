# Specification: core/include/sort/sort_list/sort_list_manager.h

## Overview

Provides pool-based allocation and management for `Sort_List` and
`Sort_Node` resources. The `Sort_List_Manager` owns fixed-size pools of
both sort lists and sort nodes, and handles contiguous allocation of node
ranges for new sort lists.

This is the top-level resource manager for the cooperative sorting system.
All sort lists and sort nodes used by the engine are allocated through
this manager.

## Dependencies

- `defines.h` (for `Sort_List_Manager`, `Sort_List`, `Sort_Node`,
  `Quantity__u32`, `Index__u8`, `Index__u16`,
  `SORT_LIST__MAXIMUM_QUANTITY_OF`, `SORT_NODE__MAXIMUM_QUANTITY_OF`)
- `defines_weak.h` (forward declarations)

## Types

### Sort_List_Manager (struct)

    typedef struct Sort_List_Manager_t {
        Quantity__u32 quantity_of__allocated_sort_lists;
        Quantity__u32 quantity_of__allocated_sort_nodes;
        Sort_List sort_lists[SORT_LIST__MAXIMUM_QUANTITY_OF];
        Sort_Node sort_nodes[SORT_NODE__MAXIMUM_QUANTITY_OF];
    } Sort_List_Manager;

| Field | Type | Description |
|-------|------|-------------|
| `quantity_of__allocated_sort_lists` | `Quantity__u32` | Number of currently allocated sort lists. |
| `quantity_of__allocated_sort_nodes` | `Quantity__u32` | Number of currently allocated sort nodes. |
| `sort_lists` | `Sort_List[64]` | Fixed pool of sort list slots. |
| `sort_nodes` | `Sort_Node[512]` | Fixed pool of sort node slots. |

### Pool Limits

| Macro | Default | Description |
|-------|---------|-------------|
| `SORT_LIST__MAXIMUM_QUANTITY_OF` | 64 | Maximum number of sort lists in the pool. |
| `SORT_NODE__MAXIMUM_QUANTITY_OF` | 512 | Maximum number of sort nodes in the pool. |

## Functions

### Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_sort_list_manager` | `(Sort_List_Manager*) -> void` | Initializes all sort lists and sort nodes as empty/deallocated. Resets allocation counters to zero. |

### Allocation

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `allocate_sort_list_in__sort_list_manager` | `(Sort_List_Manager*, Quantity__u32 quantity_of__nodes) -> Sort_List*` | `Sort_List*` | Allocates a sort list backed by a **contiguous** range of `quantity_of__nodes` sort nodes. Returns null if allocation fails (insufficient contiguous nodes or no free sort list slot). |

### Deallocation

| Function | Signature | Description |
|----------|-----------|-------------|
| `release_sort_list_in__sort_list_manager` | `(Sort_List_Manager*, Sort_List*) -> void` | Releases the sort list and its associated sort nodes back to the pool. |

### Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_quantity_of__allocated_sort_lists_in__sort_list_manager` | `(Sort_List_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns the number of currently allocated sort lists. |
| `get_quantity_of__allocated_sort_nodes_in__sort_list_manager` | `(Sort_List_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns the number of currently allocated sort nodes. |
| `get_quantity_of__available_sort_lists_in__sort_list_manager` | `(Sort_List_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns `SORT_LIST__MAXIMUM_QUANTITY_OF` minus allocated sort nodes. **Note**: current implementation subtracts node count from list max, which may be a bug — see Error Handling. |
| `get_quantity_of__available_sort_nodes_in__sort_list_manager` | `(Sort_List_Manager*) -> Quantity__u32` | `Quantity__u32` | Returns `SORT_NODE__MAXIMUM_QUANTITY_OF` minus allocated sort lists. **Note**: current implementation subtracts list count from node max, which may be a bug — see Error Handling. |

### Direct Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `get_p_sort_list_by__index_in__sort_list_manager` | `(Sort_List_Manager*, Index__u8) -> Sort_List*` | `Sort_List*` | Returns a pointer to the sort list at the given index. No bounds checking. |
| `get_p_sort_node_by__index_in__sort_list_manager` | `(Sort_List_Manager*, Index__u16) -> Sort_Node*` | `Sort_Node*` | Returns a pointer to the sort node at the given index. No bounds checking. |

### Type Queries (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `is_sort_node_a__sort_list` | `(Sort_List_Manager*, Sort_Node*) -> bool` | `bool` | Returns `true` if the sort node's `p_node_data` points to a `Sort_List` within the manager's `sort_lists` array. Used to detect sort list chaining. |

## Agentic Workflow

### Resource Ownership

The `Sort_List_Manager` is the **sole owner** of all `Sort_List` and
`Sort_Node` memory in the engine. It is embedded in the `Game` struct:

    Game
    └── sort_list_manager : Sort_List_Manager
            ├── sort_lists[64]  : Sort_List
            └── sort_nodes[512] : Sort_Node

No other system should allocate or free sort lists/nodes outside of
this manager.

### Allocation Lifecycle

    [Manager Initialized]
            |
    allocate_sort_list_in__sort_list_manager(quantity_of__nodes)
            |
        (finds free Sort_List slot)
        (finds contiguous range of free Sort_Nodes)
            |
    [Sort_List allocated, Sort_Nodes allocated]
            |
        (configure sort algorithm, populate nodes)
        (run cooperative sort via Process_Manager)
            |
    release_sort_list_in__sort_list_manager
            |
    [Sort_List and Sort_Nodes returned to pool]

### Contiguous Allocation Requirement

`allocate_sort_list_in__sort_list_manager` requires a **contiguous** block
of sort nodes. This means:

- Fragmentation of the node pool can cause allocation failures even when
  the total number of free nodes is sufficient.
- Callers should release sort lists promptly to minimize fragmentation.
- For large sort lists, allocate early when the pool is less fragmented.

### Integration with Process_Manager

Typical usage pattern for cooperative sorting:

    // 1. Allocate
    Sort_List *p_sort_list =
        allocate_sort_list_in__sort_list_manager(
            &p_game->sort_list_manager, quantity);

    // 2. Configure (e.g. heap sort)
    initialize_sort_list_as__heap(p_sort_list);
    point_sort_list__sort_nodes_to__this_range(
        p_sort_list, p_data, sizeof(Element));

    // 3. In a process handler, sort cooperatively:
    void m_my_sort_process(Process *p_proc, Game *p_game) {
        Sort_List *p_sl = p_proc->p_process_data;
        if (run_sort_with__this_many_steps(p_sl, 4)) {
            complete_process(p_proc);
        }
    }

    // 4. Release when done
    release_sort_list_in__sort_list_manager(
        &p_game->sort_list_manager, p_sort_list);

### Preconditions

- `initialize_sort_list_manager`: `p_sort_list_manager` must be non-null.
- `allocate_sort_list_in__sort_list_manager`: `quantity_of__nodes` must be
  greater than 0 and not exceed `SORT_NODE__MAXIMUM_QUANTITY_OF`.
- `release_sort_list_in__sort_list_manager`: `p_sort_list` must have been
  previously allocated by this manager.
- Direct access functions perform no bounds checking; the caller is
  responsible for valid indices.

### Postconditions

- After `initialize_sort_list_manager`: all lists and nodes are
  deallocated, counters are zero.
- After successful `allocate_sort_list_in__sort_list_manager`: the
  returned sort list is marked allocated, its node array is contiguous
  and allocated.
- After `release_sort_list_in__sort_list_manager`: the sort list and
  its nodes are marked deallocated, counters are decremented.

### Error Handling

- `allocate_sort_list_in__sort_list_manager` returns null on failure
  (no free list slot, or insufficient contiguous nodes).
- **Known issue**: `get_quantity_of__available_sort_lists_in__sort_list_manager`
  subtracts `quantity_of__allocated_sort_nodes` from
  `SORT_LIST__MAXIMUM_QUANTITY_OF`, and
  `get_quantity_of__available_sort_nodes_in__sort_list_manager` subtracts
  `quantity_of__allocated_sort_lists` from `SORT_NODE__MAXIMUM_QUANTITY_OF`.
  These appear to have swapped subtrahends. Callers should be aware that
  these functions may return incorrect values.
