run_game — core/source/game.c

Runs the scene state machine for the game, then drains pending serialization requests.

Pre-conditions:
1. p_game must be a non-null pointer to an initialized Game struct.
2. p_game->scene_manager must have been initialized via initialize_scene_manager (or equivalent), so that scene_manager.scenes is a valid array and p_active_scene is either NULL or points to a valid Scene within that array.
3. If p_game->scene_manager.p_active_scene is NULL on entry, the scene registered at Scene_Kind__None must have a valid m_enter_scene_handler (i.e., is_scene__valid must return true). Otherwise the function aborts and returns -1.
4. The scene handlers (m_load_scene_handler, m_enter_scene_handler, m_unload_scene_handler) are expected to conform to their documented contracts: m_enter_scene_handler acts as the per-scene main loop and may call set_active_scene_for__scene_manager to transition to a new scene.

Post-conditions:
1. If no active scene was established and Scene_Kind__None is invalid, returns -1 and calls debug_abort.
2. If p_active_scene->m_enter_scene_handler is NULL during the loop, returns -1 and calls debug_abort.
3. Otherwise, returns 0 after all scenes have transitioned (p_active_scene becomes NULL) and all pending serialization requests have been drained via poll_process_manager and the game tick timer.
4. The Game struct is mutated through scene handler callbacks and through poll_process_manager / timer polling during the serialization drain phase.

Correctness Verdict: Correct

Semantic Alignment:
The function correctly implements a scene state machine: it ensures an initial active scene exists, then loops loading, entering, and unloading each active scene until the active scene becomes NULL (indicating the game should stop). The m_enter_scene_handler is documented as "Functions as main loop" (see defines.h, line 1357-1358), so it is expected to block until the scene is done and may transition to a new active scene via set_active_scene_for__scene_manager. After the enter handler returns, the unload handler runs for the scene that was just entered (via the local p_active_scene variable, which is not affected by changes to p_game->scene_manager.p_active_scene during handler execution). The while loop condition then re-reads the active scene, picking up any transition. This is semantically correct.

However, there is a redundant assignment on lines 702-703:
    p_active_scene = p_game->scene_manager.p_active_scene;
This reassigns p_active_scene to the same value already set by the while condition on line 697 (since p_scene_manager == &p_game->scene_manager). The redundancy is harmless — the local variable is not modified by any handler call before this point — but it is unnecessary and could mislead readers into thinking the value might differ.

Lavender-Specific Semantics:
This function is not an initialization function (its name does not contain "init", "initialize", or "reset"). The set_active_scene_for__scene_manager call on line 690-692 is a scene manager operation that assigns the active scene pointer, not a resource acquisition (RAII). The function follows Lavender conventions correctly.

Implementation Correctness:
Type compatibility — p_scene_manager is Scene_Manager* and is assigned from &p_game->scene_manager, which is Scene_Manager. p_active_scene is Scene* and is assigned from get_p_active_scene_from__scene_manager (returns Scene*) and from p_game->scene_manager.p_active_scene (Scene*). All types match exactly. No implicit conversions or truncation.
Undefined behavior — No null dereference. The while condition checks p_active_scene for non-null before dereferencing. The m_enter_scene_handler null check on line 710 guards the required handler. The optional handlers (m_load_scene_handler, m_unload_scene_handler) are guarded by if-checks. No pointer arithmetic, no type punning, no out-of-bounds access.
Validation — The is_scene__valid check on the initial scene and the m_enter_scene_handler null check are appropriate for the function's role as a top-level game runner. Null-checking p_game itself is not performed, but this is consistent with the codebase pattern (callers are responsible for passing valid pointers).

Side Effects:
Mutates p_game indirectly through scene handler callbacks (m_load_scene_handler, m_enter_scene_handler, m_unload_scene_handler) and through poll_process_manager and timer polling during the serialization drain phase. The scene handlers may change p_game->scene_manager.p_active_scene to transition scenes. No other direct side effects outside of handler invocations.
