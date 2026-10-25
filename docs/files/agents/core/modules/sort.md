# sort — Heuristic sort lists and opaque heap sort

**Sources:** `core/source/sort/sort_list/sort_list_manager.c` + `core/source/sort/sort_list/sort_list.c` + `core/source/sort/sort_list/sort_node.c` + `core/source/sort/sort_list/heap_sort.c` + `core/source/sort/heap_sort__opaque.c`

## Surface Concerns

The `sort/` module provides two sorting approaches used by the engine's presentation layer (sprite priority, rendering order) and by game logic. Both use the same heuristic convention: return < 0 if first < second (ascending), > 0 if first > second, == 0 if equal.

In-core consumers today: `core/source/rendering/sprite_manager.c` and `core/source/rendering/graphics_window_manager.c`, both via `heap_sort__opaque` only. `core/source/game.c` merely calls `initialize_sort_list_manager()` on its `Game` member. The task-schedulable `Sort_List`/manager machinery has no in-core consumers; it exists for game-layer use.

- **Sort lists** — A task-schedulable, heuristic-driven sort list backed by a contiguous node pool. The game installs the comparator. The manager provides allocation from a fixed pool of lists and nodes (linear scan; contiguous-block search for nodes). Supports append (O(lgN) — a binary search for the *first empty slot*, i.e. it appends at the end of the occupied prefix, not a sorted position), direct insert (O(1)), and remove (O(N)).

- **Opaque heapsort** — A single-call generic heapsort over raw arrays of any type. Game installs both heuristic and swap callbacks. Sorts in place; not task-schedulable.

- **Fixed capacity** — `SORT_LIST__MAXIMUM_QUANTITY_OF` (64) lists and `SORT_NODE__MAXIMUM_QUANTITY_OF` (512) nodes are compile-time constants in `defines.h`. The manager lives as a member of `Game`. Allocation failure returns `NULL` with optional `debug_error`.

- **Contiguous allocation** — `allocate_sort_nodes_in__sort_list_manager` finds a contiguous block of free nodes with lookahead. Returns `NULL` if no contiguous block of the requested size exists.

- **Task scheduling** — Sort step functions (`m_sort` function pointers) return `true` when fully sorted. `run_sort()` loops `m_sort()` to completion *within a single call*; to spread a sort across multiple game ticks, use `run_sort_with__this_many_steps()` (step-bounded) or the single-step `run_sort__once()` inline.

- **Heapsort odd-length requirement** — `initialize_sort_list_as__heap` calls `debug_abort` on odd-length lists (`heap_sort.c`).

## Public API Surface

### Key Types

**`Sort_Node`** — defined in `sort_node.h`. Key members:
- `void *p_node_data` — pointer to the actual data this node represents.
- `Signed_Quantity__i16 heuristic_value` — caller-supplied value written by `initialize_sort_node_as__allocated`; never read anywhere in core (effectively a game-layer cache slot).
- `Index__u16 index_for__next_node :15` — index within the list for heap-sort parent/child links.
- `bool is_allocated :1` — whether the node holds valid data.

**`Sort_List`** — defined in `sort_list.h`. Key members:
- `Sort_Node *p_node_list` — pointer to contiguous array of `Sort_Node` (must be contiguous per `defines.h`).
- `f_Sort_Heuristic f_sort_heuristic` — game-installed comparator function pointer.
- `m_Sort m_sort` — sort algorithm step function (returns `true` when fully sorted).
- `struct Sort_List_t *p_sort_list__next` — linked-list pointer for extension.
- `Quantity__u32 size_of__p_node_list :31` — number of nodes in the list.
- `bool is_allocated :1` — whether the list is active.
- `Sort_Data sort_data` — union for algorithm-specific auxiliary state (heapsort indices).

**`Sort_List_Manager`** — defined in `sort_list_manager.h`. Key members:
- `Quantity__u32 quantity_of__allocated_sort_lists`
- `Quantity__u32 quantity_of__allocated_sort_nodes`
- `Sort_List sort_lists[SORT_LIST__MAXIMUM_QUANTITY_OF]`
- `Sort_Node sort_nodes[SORT_NODE__MAXIMUM_QUANTITY_OF]`

**Heuristic and step types** — defined in `defines.h`.
- `f_Sort_Heuristic` — game-installed comparator for `Sort_Node*` pairs.
- `f_Sort_Heuristic__i32` — generic comparator for opaque heapsort (`void*` pairs).
- `m_Sort` — step function for task-schedulable sort lists.

### Key Functions

- `void initialize_sort_node_as__empty(Sort_Node *p_sort_node);` / `void initialize_sort_node_as__allocated(Sort_Node *p_sort_node, Signed_Quantity__i16 heuristic_value, Index__u16 index_for__next_node);`
- `static inline void set_sort_node_as__allocated(Sort_Node *p_sort_node);` / `static inline void set_sort_node_as__deallocated(Sort_Node *p_sort_node);`
- `static inline void set_sort_node__p_node_data(Sort_Node *p_sort_node, void *p_node_data);`
- `static inline bool is_sort_node__allocated(Sort_Node *p_sort_node);`
- `void initialize_sort_list_as__empty(Sort_List *p_sort_list);`
- `void initialize_sort_list_as__allocated(Sort_List *p_sort_list, Sort_Node *p_node_list, f_Sort_Heuristic f_sort_heuristic, Quantity__u32 size_of__sort_list);`
- `void append_into__sort_list(Sort_List *p_sort_list, void *p_data);` — O(lgN); binary-searches for the first empty slot (appends at the end of the occupied prefix).
- `void insert_into__sort_list(Sort_List *p_sort_list, void *p_data, Index__u16 index_of__sort_node);` — O(1) direct insert.
- `void remove_from__sort_list(Sort_List *p_sort_list, void *p_data);` — O(N).
- `void point_sort_list__sort_nodes_to__this_range(Sort_List *p_sort_list, void *p_node_data__range, Quantity__u32 size_of__stride_in__bytes);` — points the list's nodes at a contiguous data range (how consumers bind a list to their records).
- `void run_sort(Sort_List *p_sort_list);` — loops `m_sort` to completion in a single call.
- `static inline bool run_sort__once(Sort_List *p_sort_list);` — runs exactly one `m_sort` step.
- `bool run_sort_with__this_many_steps(Sort_List *p_sort_list, Quantity__u32 quantity_of__steps);`
- `bool run_sort_with__this_heurisitic_and__this_many_steps(Sort_List *p_sort_list, f_Sort_Heuristic f_this_sort_heuristic, Quantity__u32 quantity_of__steps);` — note typo in function name.
- `Sort_Node *get_next_p_sort_node_from__sort_list(Sort_List *p_sort_list, Sort_Node *p_sort_node);`
- `Index__u16 get_index_of__sort_node_in__sort_list(Sort_List *p_sort_list, Sort_Node *p_sort_node);` / `Sort_Node *get_p_sort_node_by__index_from__sort_list(Sort_List *p_sort_list, Index__u16 index_of__sort_node);`
- `void initialize_sort_list_as__heap(Sort_List *p_sort_list);`
- `void initialize_sort_list_as__heap_sort(Sort_List *p_sort_list);`
- `bool m_sort__heapify__sort_list(Sort_List *p_sort_list);`
- `bool m_sort__heap_sort__sort_list(Sort_List *p_sort_list);`
- `void request_resorting_of__heap(Sort_List *p_sort_list);` / `void request_resorting_of__heap_sort(Sort_List *p_sort_list);`
- `void rotate_heap(Sort_List *p_sort_list);` — swaps the root with the last leaf; pair with `request_resorting_of__heap`.
- `void swap_sort_nodes_in__heap(Sort_List *p_sort_list, Sort_Node *p_sort_node__one, Sort_Node *p_sort_node__two);`
- `static inline bool is_heap__heapifed(Sort_List *p_sort_list);` / `static inline bool is_sort_data__heapifed(Sort_Data *p_sort_data);`
- `static inline bool is_heap_sort__sorted(Sort_List *p_sort_list);`
- `void heap_sort__opaque(void *p_context, void *p_ptr_array, Quantity__u32 size_of__type, Quantity__u32 size_of__array, f_Sort_Heuristic__i32 f_sort_heuristic__void, f_Sort_Swap__Void f_sort_swap__void);` — single-call generic heapsort, sorts in place.
- `void initialize_sort_list_manager(Sort_List_Manager *p_sort_list_manager);`
- `Sort_List *allocate_sort_list_in__sort_list_manager(Sort_List_Manager *p_sort_list_manager, Quantity__u32 quantity_of__nodes);` — returns `NULL` on failure.
- `void release_sort_list_in__sort_list_manager(Sort_List_Manager *p_sort_list_manager, Sort_List *p_sort_list);`
- `Sort_Node *allocate_sort_nodes_in__sort_list_manager(Sort_List_Manager *p_sort_list_manager, Quantity__u32 quantity_of__nodes);` — returns `NULL` on failure.
- `void release_sort_nodes_in__sort_list_manager(Sort_List_Manager *p_sort_list_manager, Sort_Node *p_sort_nodes, Quantity__u32 quantity_of__nodes);`

## Known rough edges

- The manager's **release path is broken**: `release_sort_nodes_in__sort_list_manager` iterates from pool index 0 (ignoring its `p_sort_nodes` argument) and calls `set_sort_node_as__allocated()` after re-initializing each node — it re-allocates the nodes it just emptied. `release_sort_list_in__sort_list_manager` additionally **increments** `quantity_of__allocated_sort_nodes` on release instead of decrementing. Treat list release as untrustworthy; in practice lists appear to be allocated once at startup.
- The "available capacity" inline queries in `sort_list_manager.h` are **swapped**: `get_quantity_of__available_sort_lists_in__sort_list_manager` subtracts the allocated *node* count from the list capacity, and vice versa. This corrupts the pre-checks in `allocate_sort_list_in__sort_list_manager`.
- `append_into__sort_list` assumes occupied nodes form a **prefix** (no holes): `remove_from__sort_list` on a middle node creates a hole that later appends can land in, overwriting the wrong slot.

## Key Files Table

| File | Role |
|------|------|
| `core/source/sort/sort_list/sort_list_manager.c` | Pool allocation/deallocation for lists and nodes |
| `core/source/sort/sort_list/sort_list.c` | Sort list operations: append, insert, remove, run |
| `core/source/sort/sort_list/sort_node.c` | Node init, allocate, deallocate |
| `core/source/sort/sort_list/heap_sort.c` | Heapsort step functions for task-schedulable sorting |
| `core/source/sort/heap_sort__opaque.c` | Single-call generic heapsort |
| `core/include/sort/sort_list/sort_list_manager.h` | Manager struct and inline query functions |
| `core/include/sort/sort_list/sort_list.h` | Sort list operations and inline helpers |
| `core/include/sort/sort_list/sort_node.h` | Node inline helpers |
| `core/include/sort/sort_list/heap_sort.h` | Heap sort inline status checks |
| `core/include/sort/heap_sort__opaque.h` | Opaque heapsort declaration |
