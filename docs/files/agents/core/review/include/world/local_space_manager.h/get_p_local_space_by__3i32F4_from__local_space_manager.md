# get_p_local_space_by__3i32F4_from__local_space_manager

**File of origin:** `core/include/world/local_space_manager.h`

## Semantic

Retrieves a `Local_Space` pointer from a `Local_Space_Manager` by converting a fixed-point 4-bit vector (`Vector__3i32F4`) into a chunk vector (`Chunk_Vector__3i32`) and delegating to `get_p_local_space_from__local_space_manager`.

## Pre-conditions

1. `p_local_space_manager` must be a valid, non-null pointer to an initialized `Local_Space_Manager`.
2. The `Local_Space_Manager` must have its neighbor pointers (`p_local_space__south_west`, etc.) properly set, as `get_p_local_space_from__local_space_manager` traverses from the south-west corner.
3. `vector__3i32F4` is a fixed-point 4-bit vector; no constraints on its value (it may represent any valid or out-of-bounds position).

## Post-conditions

1. On success, returns a pointer to the `Local_Space` whose `global_space__vector__3i32` matches the chunk vector derived from `vector__3i32F4`.
2. If the derived chunk vector falls outside the bounds of the local space manager's grid (i.e., the traversed space's `global_space__vector__3i32` does not match the target), returns `0` (null).
3. The `Local_Space_Manager` itself is not mutated; this is a read-only lookup.

## Correctness Verdict

Correct.

## Semantic Alignment

The implementation faithfully fulfills the semantic intent: it converts a `Vector__3i32F4` to a `Chunk_Vector__3i32` using the existing `vector_3i32F4_to__chunk_vector_3i32` helper and delegates to the canonical `get_p_local_space_from__local_space_manager` function. The conversion correctly applies `normalize_xyz_i32F4_to__chunk_xyz_i32` to each component, which handles the fixed-point-to-chunk-index mapping including the negative-value edge case. No struct fields are omitted or reordered.

## Implementation Correctness

- **Type compatibility:** All types align exactly. `Chunk_Vector__3i32`, `Tile_Vector__3i32`, and `Global_Space_Vector__3i32` are all typedefs of the same underlying `Vector__3i32` struct (defined in `defines_weak.h`). The return type of `vector_3i32F4_to__chunk_vector_3i32` (`Chunk_Vector__3i32`) matches the parameter type expected by `get_p_local_space_from__local_space_manager` (`Chunk_Vector__3i32`). No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer dereference (the function itself does not dereference any pointer; it delegates to callee functions). No out-of-bounds access within this function. No type punning.
- **Validation:** No validation is performed within this function, which is appropriate for a thin inline wrapper — validation (including debug bounds checks) is the responsibility of `get_p_local_space_from__local_space_manager` and the functions it calls.

## Side Effects

No side effects. This is a pure lookup function that does not modify the `Local_Space_Manager` or any of its member `Local_Space` entries.
