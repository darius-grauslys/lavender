# set_f_tile_render_kernel_of__world

**File of origin:** `core/include/world/world.h`

## Semantic

Sets (replaces) the tile render kernel function pointer on a `World` struct. The tile render kernel is a callback that examines a local area and determines how a tile should be rendered (e.g., selecting a texture index and flip flags).

## Pre-conditions

1. `p_world` must be a non-null pointer to a valid, initialized `World` struct.
2. `f_tile_render_kernel` may be a valid function pointer or `NULL`. Passing `NULL` will clear the kernel, which may be valid depending on engine usage (no explicit validation is performed).

## Post-conditions

1. `p_world->f_tile_render_kernel` is assigned the value of the `f_tile_render_kernel` parameter.
2. No other state on `p_world` is modified.
3. The function returns `void`; no return value is produced.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation correctly assigns the `f_Tile_Render_Kernel` parameter to the `f_tile_render_kernel` field of the `World` struct. The parameter type (`f_Tile_Render_Kernel`, a function pointer typedef) matches the struct field type exactly. The assignment is a direct, semantically faithful setter operation with no computation or transformation that could introduce semantic drift.

## Implementation Correctness

- **Type compatibility:** The parameter `f_tile_render_kernel` is of type `f_Tile_Render_Kernel`, which is a typedef for a function pointer. The struct field `p_world->f_tile_render_kernel` is also of type `f_Tile_Render_Kernel`. Types match exactly — no implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic is performed. The only dereference is `p_world->f_tile_render_kernel`, which requires `p_world` to be non-null (a precondition). No null dereference occurs if pre-conditions are met. No out-of-bounds access.
- **Validation:** No null-check on `p_world` is performed. This is consistent with the pattern used by all other setter functions in `world.h` (e.g., `set_f_hitbox_aabb_tile_touch_handler_of__world`, `set_f_hitbox_aabb_collision_handler_of__world`, `set_spawn_point_of__world`). Validation is the caller's responsibility, which aligns with the function's role as a low-level setter.

## Side Effects

- Mutates `p_world->f_tile_render_kernel` by assigning the provided function pointer.
- No other memory or external state is affected.
- This is not an initialization function in the Lavender sense (it is not a pool cleanup or reset-to-default operation); it is a straightforward setter that replaces an existing function pointer value.
