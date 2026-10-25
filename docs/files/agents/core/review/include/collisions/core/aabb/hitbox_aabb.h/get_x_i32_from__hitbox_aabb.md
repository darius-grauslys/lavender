# get_x_i32_from__hitbox_aabb

- **Function name**: `get_x_i32_from__hitbox_aabb`
- **File of origin**: `core/include/collisions/core/aabb/hitbox_aabb.h`

## Semantic

Returns the X position of a `Hitbox_AABB` as a plain 32-bit signed integer, converting the hitbox's internal 4-bit fixed-point (`i32F4`) representation to an integer world/grid index.

## Pre-conditions

1. `p_hitbox` must point to a valid, initialized `Hitbox_AABB` struct.
2. In debug builds (`#NDEBUG` undefined), a null `p_hitbox` is detected and short-circuited; in release builds the caller is responsible for ensuring non-nullity.

## Post-conditions

1. Returns `Signed_Index__i32` (`int32_t`), the integer X coordinate derived from the hitbox's `position__3i32F4` field.
2. In debug builds, if `p_hitbox` is null, `debug_error` is invoked and `0` is returned.
3. The returned value is the result of an arithmetic right-shift by `FRACTIONAL_PERCISION_4__BIT_SIZE` (4 bits) of the stored fixed-point X component, i.e. `i32F4_to__i32`.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation faithfully realizes the declared intent. The function composes two existing helpers:

- `get_position_3i32F4_of__hitbox_aabb(p_hitbox)` — fetches the `position__3i32F4` member (`Vector__3i32F4`).
- `get_x_i32_from__vector_3i32F4(...)` — extracts the X component and converts it from `i32F4` to `i32` via `i32F4_to__i32`.

The result is the X coordinate in integer form, matching the semantic of the `_i32` (as opposed to `_i32F4`) accessor family. The conversion semantics (fixed-point → integer) are correct and consistent with the rest of the coordinate-extraction accessors. No struct fields are omitted or reordered.

## Implementation Correctness

- **Type compatibility**: `Signed_Index__i32` is a typedef for `int32_t` (`core/include/defines_weak.h:55,111`). The helper `get_x_i32_from__vector_3i32F4` returns `Signed_Index__i32`, exactly matching this function's return type. The debug-guard `return 0;` is a valid `int32_t` literal — no implicit conversion or truncation occurs.
- **Undefined behavior**: No pointer arithmetic, no null dereference in the checked path. In release builds the null check is elided (see below); a null caller argument would then dereference null, but this is the established codebase contract, not a defect unique to this function.
- **Validation appropriateness**: Validation is debug-only (`#ifndef NDEBUG`), delegating null-safety responsibility to the caller in release builds. This matches the convention used by every sibling accessor in this file (`get_*_i32[_i32F4]_from__hitbox_aabb`, `get_chunk_*_i32_from__hitbox_aabb`) and the underlying `get_position_3i32F4_of__hitbox_aabb`. The validation is therefore appropriate for the function's role as a lightweight inline accessor.
- **Return-value usage (callers, out of scope per guide — noted only for self-contained completeness)**: the returned `0` sentinel on a null debug hit is indistinguishable from a legitimate X coordinate of `0`; this is an accepted tradeoff across the accessor family and is not a per-function defect.

## Side Effects

No side effects. The function is a pure reader: it does not mutate `p_hitbox` or any other observable state. The only observable action is the return value (and, in debug builds with a null argument, the `debug_error` log emission, which is a diagnostic side effect rather than a functional mutation).

## Notes

- The `debug_error` diagnostic string is `"get_x_i32_from__hitbox, p_hitbox == 0."` — it omits the `_aabb` suffix and renames `p_hitbox_aabb` to `p_hitbox`. This is consistent with the immediate sibling accessors (`get_y_i32_from__hitbox_aabb`, `get_z_i32_from__hitbox_aabb`, `get_chunk_*_i32_from__hitbox_aabb`, and the `_i32F4` variants), which all use the same truncated wording. It is therefore an established local convention rather than a defect of this specific function; no change is warranted here.
- This function is not an initializer; the "Initialization ≠ RAII" rule does not apply.
