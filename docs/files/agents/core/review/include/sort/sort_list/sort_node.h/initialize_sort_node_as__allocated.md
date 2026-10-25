# initialize_sort_node_as__allocated

**File of origin:** `core/source/sort/sort_list/sort_node.c`

## Semantic

Sets the sort metadata fields of a `Sort_Node` (heuristic value, next-node index, and allocated flag) to prepare it for active use in a sort list.

## Pre-conditions

1. `p_sort_node` must be a non-null pointer to a writable `Sort_Node` object.
2. `heuristic_value` may be any `Signed_Quantity__i16` value (any signed 16-bit integer).
3. `index_for__next_node` must fit within 15 bits (0–32767). Values exceeding this range will be silently truncated by the 15-bit bitfield. The sentinel value `INDEX__UNKNOWN__SORT_NODE` (0x7FFF) is valid.
4. `p_node_data` is not set by this function; the caller is expected to set it separately via `set_sort_node__p_node_data` if needed.

## Post-conditions

1. `p_sort_node->heuristic_value` is set to the provided `heuristic_value`.
2. `p_sort_node->index_for__next_node` is set to the provided `index_for__next_node` (subject to 15-bit truncation).
3. `p_sort_node->is_allocated` is set to `true`.
4. `p_sort_node->p_node_data` is left unchanged (not initialized by this function).

## Correctness Verdict

Correct

## Semantic Alignment

The function fulfills its intent of transitioning a `Sort_Node` into an "allocated" (in-use) state by setting the three metadata fields. However, it does not assign `p_node_data`, which is the fourth field of the `Sort_Node` struct. This omission is by design: `p_node_data` is consistently set separately in the codebase via `set_sort_node__p_node_data` (e.g., in `insert_into__sort_list` and `point_sort_list__sort_nodes_to__this_range`). The companion function `initialize_sort_node_as__empty` also omits `p_node_data` and `is_allocated`, confirming this is an established pattern.

Regarding Lavender-specific semantics: in Lavender, "initialization" typically means cleaning up a struct to its initial conditions for pool reuse, not resource acquisition (RAII). The function name `initialize_sort_node_as__allocated` is slightly inconsistent with this convention — it is more of a "setup" or "configure" operation that marks a node as allocated and assigns sort metadata, rather than a cleanup/reset. The `initialize_sort_node_as__empty` counterpart is more aligned with Lavender initialization semantics (resetting to default/empty state).

## Implementation Correctness

- **Type compatibility**: `heuristic_value` parameter type (`Signed_Quantity__i16`) matches the struct field type exactly. The `index_for__next_node` parameter is `Index__u16` (uint16_t), but the struct field is a 15-bit bitfield (`Index__u16 :15`). This creates a potential for silent truncation if a value greater than 32767 is passed. In practice this is not an issue since valid indices are bounded by `SORT_NODE__MAXIMUM_QUANTITY_OF` (512), but the parameter type does not enforce this constraint. The `is_allocated` field is a 1-bit bitfield and `true` is correctly assigned.
- **Undefined behavior**: No pointer arithmetic, no null dereference (assuming caller provides valid pointer), no type punning, no out-of-bounds access. The function performs simple struct member assignments.
- **Validation**: No validation is performed. This is consistent with the codebase pattern for low-level struct assignment functions — debug-mode null checks are present in higher-level functions (e.g., `sort_list.c`) but not in low-level node-level operations. The inline helpers in `sort_node.h` also do not validate.

## Side Effects

Mutates the `Sort_Node` pointed to by `p_sort_node`: sets `heuristic_value`, `index_for__next_node`, and `is_allocated`. Does not modify `p_node_data`. No other memory or state is affected.
