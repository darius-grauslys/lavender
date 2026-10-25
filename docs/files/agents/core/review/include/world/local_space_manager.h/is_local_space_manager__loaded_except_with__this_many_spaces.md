# is_local_space_manager__loaded_except_with__this_many_spaces

**File of origin:** `core/source/world/local_space_manager.c`

## Semantic

Iterates over all local spaces in the `Local_Space_Manager`, counts how many have an associated `Global_Space` that is not yet "active" (i.e., still constructing, awaiting construction, deconstructing, or awaiting deconstruction), and returns true if that count is within the caller-supplied maximum threshold.

## Pre-conditions

1. `p_local_space_manager` must be non-null and point to a valid, initialized `Local_Space_Manager` struct.
2. `p_game` is accepted as a parameter for API consistency (matching the signature of the inline wrapper `is_local_space_manager__loaded`) but is **not used** within this function. It may be null without affecting behavior.
3. `maximum_quantity_of__loading_spaces` is a `Quantity__u32` (uint32_t); any value is valid. A value of 0 means the manager must be fully loaded (all spaces active) for the function to return true.

## Post-conditions

1. Returns `true` if the number of local spaces whose `Global_Space` is non-null but not active (still loading/transitioning) is less than or equal to `maximum_quantity_of__loading_spaces`.
2. Returns `false` if the count of non-active global spaces exceeds the maximum.
3. No state is modified. The `Local_Space_Manager` and `Game` are read-only.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation faithfully fulfills the semantic intent expressed by the function name. The function name `is_local_space_manager__loaded_except_with__this_many_spaces` translates to: "Is the local space manager loaded, allowing at most N spaces to still be loading?"

The implementation:
- Iterates over the entire `local_spaces` array (size `VOLUME_OF__LOCAL_SPACE_MANAGER`, which is `LOCAL_SPACE_MANAGER__WIDTH * LOCAL_SPACE_MANAGER__HEIGHT * LOCAL_SPACE_MANAGER__DEPTH`).
- Skips local spaces that have no global space (null `p_global_space`), since those are not "loading" — they are simply unheld/unallocated.
- Counts local spaces whose global space exists but is not "active" per `is_global_space__active`. A global space is considered not active when it is in any of these transitional states: constructing, awaiting construction, deconstructing, or awaiting deconstruction.
- Returns `true` when the count of such "loading" spaces is within the allowed maximum.

The inline wrapper `is_local_space_manager__loaded` calls this function with a computed threshold based on chunk dimensions, confirming the intended usage pattern.

## Implementation Correctness

- **Type compatibility:** All types match correctly. `Quantity__u32` (uint32_t) is used for both the counter and the maximum parameter. `Index__u32` (uint32_t) is used for the loop index. `VOLUME_OF__LOCAL_SPACE_MANAGER` is a compile-time constant macro. The comparison `<=` between two `Quantity__u32` values is valid.
- **No undefined behavior:** No null pointer dereference (the loop accesses array elements directly, not through a potentially-null pointer). No out-of-bounds access (loop bound is strictly `< VOLUME_OF__LOCAL_SPACE_MANAGER`, matching the array size). No type punning or broken pointer arithmetic.
- **Validation:** The function does not validate that `p_local_space_manager` is non-null, consistent with the codebase convention where callers are responsible for passing valid pointers. The `get_p_global_space_from__local_space` helper includes a null check for `p_local_space`, which is redundant here (since `p_local_space` is always the address of a valid array element) but harmless.
- **Unused parameter:** `p_game` is unused. This is a deliberate API design choice — the inline wrapper `is_local_space_manager__loaded` forwards `p_game` to this function for interface consistency. Not a bug, but worth noting for maintainability.

## Side Effects

No side effects. This is a pure query function. It reads from the `Local_Space_Manager` and the `Global_Space` structs it references, but does not modify any state.
