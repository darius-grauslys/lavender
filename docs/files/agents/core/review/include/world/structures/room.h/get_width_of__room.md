# get_width_of__room

**File of origin:** `core/include/world/structures/room.h`

## Semantic

Returns the width (as a `Quantity__u32`) of the room's axis-aligned bounding box (`bounding_box_of__room`).

## Pre-conditions

1. `p_room` must be non-null. The function dereferences `p_room` without any null check, so passing a null pointer results in undefined behavior.

## Post-conditions

1. On return, the function yields the value of `p_room->bounding_box_of__room.width__quantity_u32`.
2. The `Room` struct pointed to by `p_room` is not modified.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function is a pure accessor that reads the `width__quantity_u32` field from the `Hitbox_AABB` struct embedded in the `Room` struct via the `bounding_box_of__room` member. The field name (`width__quantity_u32`) and the return type (`Quantity__u32`) are semantically consistent — the function returns the room's width as a quantity.

## Implementation Correctness

- **Type compatibility:** The return type `Quantity__u32` matches the field type `Quantity__u32` exactly (both are `uint32_t`). There are no implicit conversions or truncation.
- **Undefined behavior:** No null dereference guard exists, but this is consistent with the codebase convention for `static inline` accessor functions (e.g., `get_height_of__room`, `get_the_type_of__room` all follow the same pattern). Null validation is the caller's responsibility.
- **Validation:** No validation is performed, which is appropriate for a lightweight `static inline` accessor in this codebase. The caller is expected to ensure `p_room` is valid.

## Side Effects

No side effects. The function is a pure read accessor; it does not modify any state.
