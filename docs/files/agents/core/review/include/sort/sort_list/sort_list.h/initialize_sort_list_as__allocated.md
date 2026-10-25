initialize_sort_list_as__allocated — core/source/sort/sort_list/sort_list.c

Sets up a Sort_List to manage a caller-provided, pre-allocated contiguous array of
Sort_Nodes. Initializes all nodes to their "empty" state, records the heuristic
function, size, and marks the list as allocated. This is a Lavender-style
initialization (reset to initial conditions), NOT RAII — no memory is allocated.

Pre-conditions:
1. p_sort_list must be a non-null pointer to a writable Sort_List object.
2. p_node_list must point to a contiguous array of at least size_of__sort_list
   Sort_Node elements. May be NULL only if size_of__sort_list is 0.
3. f_sort_heuristic may be any f_Sort_Heuristic function pointer, including NULL.
4. size_of__sort_list must be less than SORT_NODE__MAXIMUM_QUANTITY_OF (512).
   This is enforced only in debug builds (#ifndef NDEBUG).
5. No debug null-check is performed on p_sort_list, unlike other functions in
   the file (e.g., append_into__sort_list, remove_from__sort_list, run_sort).

Post-conditions:
1. p_sort_list->p_node_list is set to p_node_list.
2. p_sort_list->f_sort_heuristic is set to f_sort_heuristic.
3. p_sort_list->size_of__p_node_list is set to size_of__sort_list.
4. p_sort_list->is_allocated is set to true.
5. p_sort_list->p_sort_list__next is set to 0 (null).
6. Each Sort_Node in the range [0, size_of__sort_list) is passed to
   initialize_sort_node_as__empty, which sets heuristic_value to 0 and
   index_for__next_node to INDEX__UNKNOWN__SORT_NODE.
7. p_sort_list->m_sort is NOT initialized — left with whatever stale value it
   held previously.
8. p_sort_list->sort_data is NOT initialized — left with whatever stale value
   it held previously.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to reset a Sort_List to its "allocated" initial
conditions by pointing it at a pre-allocated node list and clearing all nodes.
The core assignments (p_node_list, f_sort_heuristic, size_of__p_node_list,
is_allocated, p_sort_list__next) are correct and match the struct's field types
exactly with no implicit conversions or truncation.

However, two struct fields are left uninitialized: m_sort (a function pointer)
and sort_data (a union). In Lavender semantics, "initialization" means cleaning
a struct to its initial conditions. Leaving m_sort uninitialized means a stale
function pointer may persist, which could cause undefined behavior if run_sort
or related functions are called before m_sort is explicitly set. sort_data is
similarly left in an indeterminate state. This is consistent with
initialize_sort_list_as__empty, which also omits these fields, but it means
neither init function fully resets the struct.

The more critical semantic failure is in the node initialization loop. The
function calls get_p_sort_node_by__index_from__sort_list to obtain each node
pointer, but that accessor returns null (0) whenever a node's is_allocated bit
is false. During initialization, nodes may have is_allocated == false (e.g.,
freshly zeroed memory or previously deallocated nodes). When the accessor
returns null, that null pointer is passed directly to
initialize_sort_node_as__empty, which dereferences it without a null check,
causing undefined behavior. This defeats the purpose of the loop — nodes that
are not allocated are precisely the ones that need to be initialized, yet they
are skipped or cause a crash.

Implementation Correctness:
- Type compatibility: All field assignments use matching types. size_of__sort_list
  (Quantity__u32, uint32_t) is assigned to a 31-bit bitfield, but the debug check
  ensures it is less than 512, so no truncation occurs. The loop variable
  index_of__sort_node (Index__u16, uint16_t) is compared against size_of__sort_list
  (uint32_t); since size is bounded to < 512, no comparison issue arises.
- Undefined behavior: The primary UB is the null dereference described above.
  get_p_sort_node_by__index_from__sort_list can return null, and
  initialize_sort_node_as__empty dereferences its argument unconditionally.
  Additionally, no null check on p_sort_list means a null p_sort_list would
  cause immediate UB on the first field write.
- Validation: The debug-only size check (size_of__sort_list >=
  SORT_NODE__MAXIMUM_QUANTITY_OF) is appropriate. Missing null checks for
  p_sort_list and p_node_list are inconsistent with the rest of the file and
  should be added in debug builds.

Side Effects:
Mutates p_sort_list and all Sort_Node elements in the range [0, size_of__sort_list).
Specifically:
- Writes p_node_list, f_sort_heuristic, size_of__p_node_list, is_allocated, and
  p_sort_list__next on the Sort_List struct.
- Calls initialize_sort_node_as__empty on each node, which sets
  heuristic_value and index_for__next_node.
- Does NOT modify m_sort or sort_data (left stale).
- No side effects on global state or I/O.
