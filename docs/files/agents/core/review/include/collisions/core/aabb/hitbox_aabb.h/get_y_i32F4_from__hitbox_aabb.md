get_y_i32F4_from__hitbox_aabb

core/include/collisions/core/aabb/hitbox_aabb.h (no line numbers; function spans lines 501–511)

## Semantic

Extracts and returns the Y-coordinate in fixed-point `i32F4` format from the
`position__3i32F4` field of a given `Hitbox_AABB`.

## Pre-conditions

1. `p_hitbox` must be a non-null pointer to a valid `Hitbox_AABB` struct.
   - In debug builds (`#ifndef NDEBUG`), a null `p_hitbox` is detected, an
     error is logged via `debug_error`, and `0` is returned.
   - In release builds (`NDEBUG` defined), no null guard is present; the caller
     is responsible for supplying a valid pointer (this is the established
     convention for all accessor functions in this file, e.g. the sibling
     `get_x_i32F4_from__hitbox_aabb`, `get_z_i32F4_from__hitbox_aabb`, and
     `get_position_3i32F4_of__hitbox_aabb`).

## Post-conditions

1. If `p_hitbox` is non-null, returns the value of
   `p_hitbox->position__3i32F4.y__i32F4` (an `i32F4`).
2. If `p_hitbox` is null in debug builds, returns `0`.
3. The `Hitbox_AABB` struct is not modified; no state is mutated.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills its semantic intent. It first delegates
to `get_position_3i32F4_of__hitbox_aabb(p_hitbox)` to retrieve the
`Vector__3i32F4` position struct, then delegates to
`get_y_i32F4_from__vector_3i32F4(...)` to extract the `.y__i32F4` member.
This two-step delegation matches the pattern used by all sibling accessors
(`get_x_*`, `get_z_*`, and the `get_*__i32` variants) in this file and
produces the correct Y-coordinate value.

## Implementation Correctness

- **Type compatibility**: The return type is `i32F4` (`typedef int32_t i32F4`
  in `defines.h:54`). The callee `get_y_i32F4_from__vector_3i32F4` returns
  `Signed_Index__i32` (`typedef int32_t Signed_Index__i32` in
  `defines_weak.h:55`). Both are `int32_t`, so the return is an exact
  type match with no implicit conversion, truncation, or data loss.
- **Undefined behavior**: In debug builds, the null check prevents any
  dereference of a null `p_hitbox`. In release builds, if the caller passes
  null, the null pointer would propagate to `get_position_3i32F4_of__hitbox_aabb`
  whose own body (line 142: `return p_hitbox_aabb->position__3i32F4;`) would
  then dereference null — undefined behavior. However, this is the documented
  and consistent contract across the entire accessor family in this file; the
  function itself introduces no novel UB.
- **Validation**: Null validation is appropriate for this accessor's role. The
  debug-only guard matches the codebase convention. No additional validation
  (e.g., range checking on the returned value) is needed for a pure field
  accessor.
- **Off-by-one / out-of-bounds**: N/A — the function is a pure field
  extraction with no array indexing or loop constructs.

## Side Effects

No side effects. The function reads from the `position__3i32F4` member of the
`Hitbox_AABB` struct and does not modify any state. (The `debug_error` call in
the null-path is a debug-only logging side effect, which is standard practice
across the codebase.)

## Notes

The debug-only error message string reads
`"get_y_i32F4_from__hitbox, p_hitbox == 0."` — it omits the `_aabb` suffix
present in the function name. This is consistent with all sibling accessors in
this file (e.g., `get_x_i32F4_from__hitbox_aabb` logs
`"get_x_i32F4_from__hitbox"`), so it is a pre-existing pattern rather than a
defect specific to this function. No action required for this review.
