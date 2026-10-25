set_size_of__hitbox_aabb — core/include/collisions/core/aabb/hitbox_aabb.h, lines 207-221

## Header

- **Function name**: `set_size_of__hitbox_aabb`
- **File of origin**: `core/include/collisions/core/aabb/hitbox_aabb.h`

## Semantic

Sets the width and height (i.e. the size) of a `Hitbox_AABB` and marks the hitbox as dirty so that any downstream cached computations know to recompute.

## Pre-conditions

1. `p_hitbox_aabb` must be a valid, non-null pointer to an initialized `Hitbox_AABB` struct. This is enforced in debug builds via the `#ifndef NDEBUG` null guard.
2. `width__quantity_u32` is of type `Quantity__u32` and may be any valid value for that type.
3. `height__quantity_u32` is of type `Quantity__u32` and may be any valid value for that type.

## Post-conditions

1. `p_hitbox_aabb->width__quantity_u32` is assigned the value of the `width__quantity_u32` parameter.
2. `p_hitbox_aabb->height__quantity_u32` is assigned the value of the `height__quantity_u32` parameter.
3. The dirty flag on `p_hitbox_aabb->hitbox_aabb_flags__u8` is set (via `set_hitbox_aabb_as__dirty`), indicating the hitbox shape has changed.
4. The function returns `void`; there is no return value.

## Correctness Verdict

Correct.

## Semantic Alignment

The implementation fulfills the semantic intent. It sets both the width and height fields on the `Hitbox_AABB` struct and marks the hitbox dirty to signal that cached AABB corner/edge computations need to be refreshed. No fields are omitted or reordered; the two size fields (`width__quantity_u32` and `height__quantity_u32`) map directly to the two size parameters.

## Implementation Correctness

- **Type compatibility**: Parameter types match target struct field types exactly. Both `width__quantity_u32` and `height__quantity_u32` parameters are of type `Quantity__u32`, matching the struct fields `Hitbox_AABB::width__quantity_u32` and `Hitbox_AABB::height__quantity_u32` respectively. No implicit conversions or truncation occur.
- **Undefined behavior**: No null dereference; the null check is performed in debug builds (`#ifndef NDEBUG`). In release builds the null check is elided, which is consistent with the codebase's convention across all sibling accessor/mutator functions (e.g., `get_position_3i32F4_of__hitbox_aabb`, `set_width_of__hitbox_aabb`, etc.). The `debug_error` call on null also returns early, preventing the subsequent dereference.
- **Return value discard**: `set_hitbox_aabb_as__dirty` returns a `bool`, whose return value is intentionally discarded here. This is acceptable because the function's purpose in this context is solely the side effect of marking the hitbox dirty; the returned bool merely indicates whether the flag changed state. This matches the pattern used by all other mutator functions in this file that call `set_hitbox_aabb_as__dirty`.
- **Validation**: The validation approach (debug-only null guard) is appropriate and consistent for this layer of the codebase; callers are expected to pass valid pointers per the precondition.

## Side Effects

- Mutates `p_hitbox_aabb->width__quantity_u32` to the provided `width__quantity_u32`.
- Mutates `p_hitbox_aabb->height__quantity_u32` to the provided `height__quantity_u32`.
- Mutates `p_hitbox_aabb->hitbox_aabb_flags__u8` by setting the dirty flag (via `set_hitbox_aabb_as__dirty`, which delegates to `set_hitbox_flags_as__dirty`).

This function does not perform any resource acquisition, so the Lavender distinction between "initialization" and "RAII" does not apply (the function name does not contain "init", "initialize", or "reset").
