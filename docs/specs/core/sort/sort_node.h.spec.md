# 1. Specification: core/include/sort/sort_list/sort_node.h

## 1.1 Overview

Provides initialization and accessor functions for `Sort_Node` — the
fundamental element of the `Sort_List` cooperative sorting system. Each
`Sort_Node` holds an opaque data pointer, a heuristic value used for
ordering, and a linked-list index to the next node in the list.

Sort nodes are allocated contiguously by the `Sort_List_Manager` and
referenced by index rather than pointer, enabling compact storage and
efficient traversal on memory-constrained platforms.

## 1.2 Dependencies

- `defines.h` (for `Sort_Node`, `Signed_Quantity__i16`, `Index__u16`)

## 1.3 Types

### 1.3.1 Sort_Node (struct)

    typedef struct Sort_Node_t {
        void                    *p_node_data;
        Signed_Quantity__i16    heuristic_value;
        Index__u16              index_for__next_node    :15;
        bool                    is_allocated            :1;
    } Sort_Node;

| Field | Type | Width | Description |
|-------|------|-------|-------------|
| `p_node_data` | `void*` | pointer | Opaque pointer to the data this node represents. |
| `heuristic_value` | `Signed_Quantity__i16` | 16 bits | Value used by the sort heuristic for ordering comparisons. |
| `index_for__next_node` | `Index__u16` | 15 bits | Index of the next node in the linked list. `INDEX__UNKNOWN__SORT_NODE` if none. |
| `is_allocated` | `bool` | 1 bit | True if this node is currently in use. |

### 1.3.2 INDEX__UNKNOWN__SORT_NODE (macro)

    #define INDEX__UNKNOWN__SORT_NODE (INDEX__UNKNOWN__u16 >> 1)

Sentinel value for `index_for__next_node` indicating no next node exists.
This is the maximum value representable in 15 bits.

## 1.4 Functions

### 1.4.1 Initialization

| Function | Signature | Description |
|----------|-----------|-------------|
| `initialize_sort_node_as__allocated` | `(Sort_Node*, Signed_Quantity__i16 heuristic_value, Index__u16 index_for__next_node) -> void` | Initializes a node as allocated with the given heuristic and next-node index. Sets `is_allocated = true`. |
| `initialize_sort_node_as__empty` | `(Sort_Node*) -> void` | Initializes a node as empty/deallocated. Clears all fields. Sets `is_allocated = false`. |

### 1.4.2 Allocation Management (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_sort_node_as__allocated` | `(Sort_Node*) -> void` | `void` | Sets `is_allocated = true`. |
| `set_sort_node_as__deallocated` | `(Sort_Node*) -> void` | `void` | Sets `is_allocated = false`. |
| `is_sort_node__allocated` | `(Sort_Node*) -> bool` | `bool` | Returns `true` if the node is allocated. |

### 1.4.3 Data Access (static inline)

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `set_sort_node__p_node_data` | `(Sort_Node*, void* p_node_data) -> void` | `void` | Sets the opaque data pointer for this node. |

## 1.5 Agentic Workflow

### 1.5.1 Role in the Sort System

`Sort_Node` is the leaf-level building block of the cooperative sort system:

    Sort_List_Manager
        └── Sort_List (linked list of Sort_Nodes)
                └── Sort_Node (data + heuristic + next index)

Sort nodes are pooled in the `Sort_List_Manager` and allocated
contiguously. The `index_for__next_node` field forms an intrusive
linked list within the contiguous array, avoiding pointer overhead.

### 1.5.2 Lifecycle

    [Unallocated] --> initialize_sort_node_as__allocated --> [Allocated]
                                                                 |
                                                          (used by Sort_List)
                                                                 |
                                                   initialize_sort_node_as__empty
                                                                 |
                                                           [Unallocated]

### 1.5.3 Heuristic Value Convention

The `heuristic_value` field is a signed 16-bit integer used by
`f_Sort_Heuristic` to determine ordering. The interpretation is
defined by the sort heuristic function:

- **Min-heap**: Smaller `heuristic_value` = higher priority (root).
- **Max-heap**: Larger `heuristic_value` = higher priority (root).
- **Custom**: Any signed comparison the heuristic defines.

The heuristic value should be set at initialization time and updated
only when the sort list is re-sorted.

### 1.5.4 Index-Based Linking

Nodes reference each other by index into the contiguous `sort_nodes`
array in `Sort_List_Manager`, not by pointer. This:

- Reduces memory usage on 32-bit platforms (15-bit index vs 32-bit pointer).
- Enables safe serialization of sort state if needed.
- Requires the `Sort_List` to resolve indices via
  `get_p_sort_node_by__index_from__sort_list`.

### 1.5.5 Preconditions

- All functions require a non-null `p_sort_node`.
- `initialize_sort_node_as__allocated`: `index_for__next_node` must be
  a valid index or `INDEX__UNKNOWN__SORT_NODE`.

### 1.5.6 Postconditions

- After `initialize_sort_node_as__allocated`: `is_allocated` is true,
  `heuristic_value` and `index_for__next_node` are set.
- After `initialize_sort_node_as__empty`: all fields are zeroed/cleared,
  `is_allocated` is false.
