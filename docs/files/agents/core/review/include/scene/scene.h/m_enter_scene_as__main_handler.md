m_enter_scene_as__main_handler — core/source/scene/implemented/scene__main.c

Runs the main game loop for a scene: polls whether the scene is active, and while active, performs game tick, frame processing, and rendering (pre-render and post-render) each iteration until the scene is no longer active.

Pre-conditions:
1. p_this_scene must be a non-null pointer to a valid Scene object.
2. p_game must be a non-null pointer to a valid Game object.
3. The Scene_Manager must be initialized (implicitly required by poll_is__scene_active, which calls get_p_scene_manager_from__game).

Post-conditions:
1) The function returns when poll_is__scene_active(p_game, p_this_scene) returns false — i.e., the scene is no longer the active scene.
2) The Game object may have been ticked and rendered during the loop (state of Game is mutated by poll__game_tick_timer, manage_game__pre_render, and manage_game__post_render).

Correctness Verdict: Correct

Semantic Alignment:
The function implements a main game loop for a scene. It continuously polls whether the scene is active, and while active, it performs game tick, frame processing, and rendering (pre and post). This matches the semantic intent of an "enter scene" handler that runs the main loop.

Implementation Correctness:
Type compatibility — parameter types (Scene *, Game *) match the expected types for poll_is__scene_active and poll__game_tick_timer. No implicit conversions or truncation.
No undefined behavior — no pointer arithmetic, no null dereference (caller is responsible for validation), no type punning, no out-of-bounds access.
No validation is needed — this is a high-level scene handler. The caller (scene manager) is responsible for ensuring p_this_scene and p_game are valid.

Side Effects:
Mutating — the Game object is mutated through poll__game_tick_timer, manage_game__pre_render, and manage_game__post_render each frame iteration. The Scene's active state may change (scene may be unloaded), but the Scene object itself is not directly mutated.