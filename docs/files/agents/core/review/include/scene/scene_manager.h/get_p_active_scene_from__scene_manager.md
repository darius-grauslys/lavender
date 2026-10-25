get_p_active_scene_from__scene_manager — core/include/scene/scene_manager.h

Returns the active scene pointer from the scene manager.

Pre-conditions:
1. p_scene_manager must be a non-null pointer to a Scene_Manager object.

Post-conditions:
1) p_scene_manager is not modified.
2) The function returns the value of p_scene_manager->p_active_scene.

Correctness Verdict: Correct

Semantic Alignment:
The implementation faithfully returns the active scene pointer stored in the
Scene_Manager. No computation or transformation is performed, so there is no
semantic drift.

Implementation Correctness:
Type compatibility — the return type (Scene *) matches the field type
(Scene *p_active_scene) exactly. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference, no type
punning, no out-of-bounds access.
No validation is needed — this is a trivial field read. The caller is
responsible for ensuring p_scene_manager is valid.

Side Effects:
No side effects — the only observable effect is returning the value of the
p_active_scene field.