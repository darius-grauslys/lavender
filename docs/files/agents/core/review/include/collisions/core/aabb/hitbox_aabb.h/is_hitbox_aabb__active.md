is_hitbox_aabb__active — core/include/collisions/core/aabb/hitbox_aabb.h, lines 118-121

## Semantic

Checks whether the `HITBOX_FLAG__IS_ACTIVE` bit is set on the hitbox's flags, indicating the hitbox is active.

## Pre-conditions

1. `p_hitbox_aabb` must be non-null. The function dereferences the pointer to access `hitbox_aabb_flags__u8` and passes its address to `is_hitbox_flags__active`.

## Post-conditions

1. Returns `true` if the `HITBOX_FLAG__IS_ACTIVE` bit is set in `p_hitbox_aabb->hitbox_aabb_flags__u8`, `false` otherwise.
2. `p_hitbox_aabb` is not modified; the query is read-only.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills its intent: it delegates to `is_hitbox_flags__active`, which performs a bitwise AND of the flags field against `HITBOX_FLAG__IS_ACTIVE`. The result is returned as a `bool`, which normalizes any non-zero value to `true`. The bit-flag check is semantically correct for determining the active state.

## Implementation Correctness

- **Type compatibility:** `Hitbox_AABB *p_hitbox_aabb` — the parameter is used to access `p_hitbox_aabb->hitbox_aabb_flags__u8`, which is of type `Hitbox_Flags__u8` (defined in the `Hitbox_AABB_t` struct at `core/include/defines.h:457`). The address-of operator yields `Hitbox_Flags__u8 *`, matching the expected parameter type of `is_hitbox_flags__active`. No implicit conversion or truncation occurs.
- **Undefined behavior:** No pointer arithmetic, no null dereference (assumes non-null caller responsibility), no out-of-bounds access.
- **Validation:** No NULL check is performed on `p_hitbox_aabb`. This is consistent with the surrounding lightweight flag accessor functions (lines 103-131), none of which perform NULL checks. The heavier `get_position_*` accessors (lines 134+) do include debug-mode NULL checks, suggesting the flag accessors rely on caller responsibility for non-nullity. Validation is appropriate for this function's role as a thin flag query.

## Side Effects

No side effects. The function only reads from `p_hitbox_aabb->hitbox_aabb_flags__u8` and returns the result of the flag check.
