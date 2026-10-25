# Function Review: quit_scene_state_machine

## 1. Header
- **Function name:** `quit_scene_state_machine`
- **File of origin:** `core/source/scene/scene_manager.c`

## 2. Semantic
Quits the active scene by deactivating it (setting `is_active` to `false`) and then clearing the active scene pointer to null.

## 3. Pre-conditions
1. `p_scene_manager` must be a non-null pointer to a valid `Scene_Manager` struct.
2. `p_scene_manager->p_active_scene` may be null (no active scene) or point to a valid `Scene` within the `scenes` array.

## 4. Post-conditions
1. If an active scene existed, its `is_active` field is set to `false`.
2. `p_scene_manager->p_active_scene` is set to `0` (null) regardless of prior state.

## 5. Correctness Verdict
**Incorrect**

## 6. Semantic Alignment
The implementation does NOT fulfill the semantic intent. The function is intended to deactivate the currently active scene and then null the active scene pointer. However, the condition guarding the deactivation is inverted:

```c
if (!p_scene_manager->p_active_scene) {
    p_scene_manager->p_active_scene->is_active = false;
}
```

The condition `!p_scene_manager->p_active_scene` evaluates to `true` when `p_active_scene` is **null** (i.e., there is no active scene). Inside this block, the code then dereferences `p_scene_manager->p_active_scene->is_active`, which is a **null pointer dereference** — undefined behavior.

The correct condition should be `if (p_scene_manager->p_active_scene)` (without the negation), matching the pattern used in `set_active_scene_for__scene_manager`:

```c
if (p_scene_manager->p_active_scene) {
    p_scene_manager->p_active_scene->is_active = false;
}
```

This way, the `is_active` flag is only set to `false` when there is actually an active scene to deactivate.

## 7. Implementation Correctness
- **Type compatibility:** Parameter type `Scene_Manager *` matches the struct definition. Field access `p_active_scene->is_active` is of type `bool`, which is correct.
- **Undefined behavior:** The inverted condition causes a null pointer dereference when `p_active_scene` is null. This is a critical bug.
- **Validation:** The function does not validate that `p_scene_manager` itself is non-null. While this may be acceptable if callers are expected to always pass a valid pointer (consistent with the codebase's pattern), the null check on `p_active_scene` is present but logically inverted.

## 8. Side Effects
- **Mutates** `p_scene_manager->p_active_scene->is_active` to `false` (intended, but only when an active scene exists — currently broken due to inverted condition).
- **Mutates** `p_scene_manager->p_active_scene` to `0` (null).
