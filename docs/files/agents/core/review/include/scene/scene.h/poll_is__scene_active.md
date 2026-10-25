# Function Review: poll_is__scene_active

**File of origin:** `core/include/scene/scene.h`

## Semantic

Checks whether the given `Scene` pointer is the currently active scene by comparing it against the `p_active_scene` pointer held in the game's `Scene_Manager`.

## Pre-conditions

1. `p_game` must be non-null. The function dereferences `p_game` via `get_p_scene_manager_from__game(p_game)`, which accesses `p_game->scene_manager`. Passing null results in undefined behavior.
2. `p_scene` may be null. Comparing a null pointer against `p_active_scene` is well-defined in C and will simply return `false` (unless `p_active_scene` is also null, in which case it returns `true`).
3. The `Game` struct's `scene_manager` field must be initialized (i.e., `initialize_scene_manager` has been called or the field is otherwise valid).

## Post-conditions

1. Returns `true` if `p_scene` is the same pointer as `p_game`'s scene manager's `p_active_scene`; returns `false` otherwise.
2. No state is modified. The function is read-only with respect to both `p_game` and `p_scene`.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills the semantic intent. The function retrieves the `Scene_Manager` from the `Game` via the existing accessor `get_p_scene_manager_from__game`, then performs a direct pointer comparison between `p_active_scene` and the provided `p_scene`. This is a valid and robust approach — pointer identity is the most direct way to determine if a specific scene instance is the active one, and it does not depend on the `is_active` boolean flag being correctly maintained (though that flag is also set by `set_active_scene_for__scene_manager`).

## Implementation Correctness

- **Type compatibility:** `p_active_scene` is of type `Scene*` and `p_scene` is of type `Scene*`. The comparison `==` between two `Scene*` values is well-defined and type-safe. No implicit conversions or truncation occur.
- **Undefined behavior:** No null dereference occurs (assuming `p_game` is non-null per pre-conditions). No out-of-bounds access, no type punning, no broken pointer arithmetic.
- **Validation:** The function does not validate `p_game` for null. This is consistent with the codebase convention — other inline accessor functions in `game.h` (e.g., `get_p_scene_manager_from__game`, `get_p_world_from__game`) also do not perform null checks on their parameters. Null validation is the caller's responsibility, not the function's.

## Side Effects

No side effects. This is a pure function: it reads from `p_game` (via the scene manager's `p_active_scene` field) and returns a boolean result. No memory is allocated, no state is mutated, and no I/O occurs.
