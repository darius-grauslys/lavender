# register_scenes

**File of origin:** `core/source/scene/implemented/scene_registrar.c`

## Semantic

Registers all implemented scenes into the provided `Scene_Manager` by delegating to individual scene registration functions (currently `register_scene__main`).

## Pre-conditions

1. `p_scene_manager` must be a non-null pointer to a valid, initialized `Scene_Manager` instance.
2. The `Scene_Manager` must have its internal scene array allocated and accessible via `get_p_scene_from__scene_manager`.

## Post-conditions

1. All implemented scenes (currently only the "main" scene) have been registered into the `Scene_Manager` via `register_scene_into__scene_manager`, which assigns their load, enter, and unload handler function pointers.
2. The `Scene_Manager` is left in a state where the registered scenes are ready to be activated.

## Correctness Verdict

**Correct**

## Semantic Alignment

The implementation fulfills its semantic intent. The function serves as a centralized registration point that calls individual scene registration functions. Currently, it registers only the "main" scene via `register_scene__main`, which in turn calls `register_scene_into__scene_manager` with the appropriate handler functions (`m_load_scene_as__main_handler`, `m_enter_scene_as__main_handler`, `m_unload_scene_as__main_handler`). The function is a thin dispatcher and correctly delegates to the scene-specific registration logic.

## Implementation Correctness

- **Type compatibility:** The parameter `Scene_Manager *p_scene_manager` is passed directly to `register_scene__main`, which expects the same type. No implicit conversions or truncation occur.
- **Undefined behavior:** No pointer arithmetic, null dereference, or out-of-bounds access occurs within this function. Null-checking of `p_scene_manager` is not performed here, but this is consistent with the codebase pattern where validation is delegated to callee functions (e.g., `register_scene_into__scene_manager` performs null checks on the scene pointer it retrieves).
- **Validation:** No validation is performed in this function, which is appropriate for its role as a dispatcher. Validation is the responsibility of the callee functions.

## Side Effects

- Mutates the `Scene_Manager` pointed to by `p_scene_manager` by registering scene handler functions into its internal scene array. Specifically, the "main" scene's `m_load_scene_handler`, `m_enter_scene_handler`, and `m_unload_scene_handler` fields are assigned.
