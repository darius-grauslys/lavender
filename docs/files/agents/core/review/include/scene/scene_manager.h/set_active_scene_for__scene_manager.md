# set_active_scene_for__scene_manager

**File of origin:** `core/source/scene/scene_manager.c`

## Semantic

Sets the active scene in the scene manager by deactivating the currently active scene (if any) and activating the specified scene.

## Pre-conditions

1. `p_scene_manager` must be a valid, non-null pointer to an initialized `Scene_Manager`.
2. `the_kind_of__scene` must be a valid `Scene_Kind` enum value (i.e., less than `Scene_Kind__Unknown`). If an invalid value is passed, `get_p_scene_from__scene_manager` will return null, and the function will set the active scene to null without crashing.

## Post-conditions

1. If a previously active scene existed, its `is_active` field is set to `false`.
2. `p_scene_manager->p_active_scene` is set to the scene corresponding to `the_kind_of__scene`, or to null if the scene kind was invalid.
3. If the new active scene is non-null, its `is_active` field is set to `true`.
4. If the new active scene is null (invalid scene kind), no scene's `is_active` is set to `true`.

## Correctness Verdict

Correct

## Semantic Alignment

The implementation correctly fulfills the semantic intent of setting the active scene. It properly deactivates the previous active scene before activating the new one, and handles the null case gracefully when an invalid scene kind is provided. The function does not perform resource acquisition (RAII); it only manipulates existing scene state within the scene manager's array.

## Implementation Correctness

- **Type compatibility:** All parameter types match their expected types. `p_scene_manager` is `Scene_Manager*`, `the_kind_of__scene` is `Scene_Kind`, and `p_scene` is `Scene*`. No implicit conversions or truncation occur.
- **Undefined behavior:** No null pointer dereference occurs. The function checks `p_scene_manager->p_active_scene` before dereferencing it, and checks `p_scene` before dereferencing it. The `get_p_scene_from__scene_manager` function validates the scene kind before indexing into the array, preventing out-of-bounds access.
- **Validation:** Validation is appropriately handled by `get_p_scene_from__scene_manager`, which returns null for invalid scene kinds. The function itself correctly handles the null return value.

## Side Effects

- Mutates `p_scene_manager->p_active_scene` (sets it to the new scene or null).
- Mutates the `is_active` field of the previously active scene (sets to `false`), if one existed.
- Mutates the `is_active` field of the newly active scene (sets to `true`), if the new scene is non-null.
