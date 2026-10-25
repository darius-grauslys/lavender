## 1. Header

**Function name:** offset_vector_by__direction

**File of origin:** core/source/vectors.c

## 2. Semantic

Offsets a `Vector__3i32F4` by one unit in the cardinal or intercardinal (diagonal) direction specified by the `Direction__u8` parameter. Only the x and y components are modified; the z component is left untouched. Unrecognized direction values (including `DIRECTION__NONE` and any direction with `UPWARDS`/`DOWNWARDS` bits set) result in no change.

## 3. Pre-conditions

1. `p_vector` must be a non-null pointer to a writable `Vector__3i32F4` object. (No null check is performed; the caller is responsible for guaranteeing validity, consistent with the codebase convention for low-level vector utility functions.)
2. `direction` may be any `Direction__u8` value. If it does not match one of the eight handled cases, the vector is left unchanged.

## 4. Post-conditions

1. On return, `p_vector` has been mutated in-place.
2. For `DIRECTION__NORTH`: `y__i32F4` is incremented by 1.
3. For `DIRECTION__EAST`: `x__i32F4` is incremented by 1.
4. For `DIRECTION__SOUTH`: `y__i32F4` is decremented by 1.
5. For `DIRECTION__WEST`: `x__i32F4` is decremented by 1.
6. For `DIRECTION__NORTH_EAST`: both `y__i32F4` and `x__i32F4` are incremented by 1.
7. For `DIRECTION__NORTH_WEST`: `y__i32F4` is incremented by 1 and `x__i32F4` is decremented by 1.
8. For `DIRECTION__SOUTH_EAST`: `y__i32F4` is decremented by 1 and `x__i32F4` is incremented by 1.
9. For `DIRECTION__SOUTH_WEST`: both `y__i32F4` and `x__i32F4` are decremented by 1.
10. For any other `direction` value (including `DIRECTION__NONE`, `DIRECTION__NORTH_UPWARDS`, etc.): no fields are modified.

## 5. Correctness Verdict

**Incorrect**

## 6. Semantic Alignment

The directional mapping is semantically correct: NORTH increments y, SOUTH decrements y, EAST increments x, WEST decrements x, and the four diagonal directions combine the appropriate cardinal offsets. The z-component is intentionally left unmodified, consistent with the function's 2D-only scope.

However, the **magnitude** of the offset does not fulfill the semantic intent. The function uses the `++` and `--` operators on `i32F4` fields, which increment/decrement the raw integer by 1. Since `i32F4` is a fixed-point type with 4 fractional bits (`FRACTIONAL_PERCISION_4__BIT_SIZE == 4`), a raw increment of 1 represents only 1/16 of a unit. A full-unit offset should use `i32_to__i32F4(1)` (which evaluates to `1 << 4 == 16`).

This is confirmed by comparison with other code in the engine:

- The `VECTOR__3i32F4__1_0_0` macro uses `i32_to__i32F4(1)` to represent one full unit in the x direction.
- The `get_2i32F4_offset_from__angle` function (in `core/source/degree.c`) returns unit-vector offsets from a lookup table where cardinal directions produce values of `2^20` in the `i32F20` domain, which converts to `i32_to__i32F4(1) == 16` in the `i32F4` domain.
- The `set_hitbox_aabb__position_with__3i32` function converts integer coordinates using `<< FRACTIONAL_PERCISION_4__BIT_SIZE` to produce proper fixed-point values.

The use of `++` instead of `+= i32_to__i32F4(1)` causes the vector to be offset by 1/16 of a unit rather than 1 full unit, which is a semantic mismatch with the function's intent.

Additionally, the function uses a `switch` statement with exact-value matching on `Direction__u8`, which is a bit-flag type. While the eight handled cases have unique values and are matched correctly, the bitmask design means that compound directions combining cardinal bits with `UPWARDS`/`DOWNWARDS` (e.g., `DIRECTION__NORTH_UPWARDS = 17`) fall through to `default:` and produce no offset. A bit-checking approach (e.g., `if (direction & DIRECTION__NORTH) ...`) would be more robust and consistent with how other functions in the codebase treat `Direction__u8` as a bitmask (e.g., `get_movement_direction_of__hitbox_aabb`, `get_tile_transition_direction_of__hitbox_aabb`).

## 7. Implementation Correctness

**Type compatibility:** Parameter and field types are compatible. `p_vector` is `Vector__i32F4 *`, and `direction` is `Direction__u8` (a `uint8_t`). The switch cases use the correct `Direction__u8` macro values. No implicit conversions or truncation occur.

**Undefined behavior:** No null dereference protection is present, but this is consistent with the codebase convention for low-level vector utility functions (e.g., `add_p_vectors__3i32F4`, `subtract_p_vectors__3i32F4`). No pointer arithmetic, type punning, or out-of-bounds access occurs.

**Validation:** No input validation is performed, which is appropriate for this low-level utility function. The caller is responsible for providing a valid pointer and a meaningful direction value.

**Fixed-point bug:** The `++` and `--` operators increment/decrement `i32F4` fields by 1 in the raw integer domain. Since `i32F4` uses 4 fractional bits, this represents a 1/16-unit offset instead of a 1-unit offset. The correct approach is `p_vector->y__i32F4 += i32_to__i32F4(1)` (or equivalently `+= 16`).

## 8. Side Effects

The function mutates the `Vector__3i32F4` struct pointed to by `p_vector` by incrementing or decrementing its `x__i32F4` and/or `y__i32F4` fields. No other side effects are produced. (See note in Section 6 regarding the magnitude of the increment being 1/16 of a unit rather than 1 full unit.)
