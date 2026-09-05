#ifndef DEBUG_SCENE_H
#define DEBUG_SCENE_H

#include <defines.h>

/*
 * debug_scene.h provides functions which are intended to be invoked through
 * gdb or other debug modules.
 *
 * DO NOT USE debug_* functions in non-debug modules.
 * With the only exception being debug_* functions for logging.
 * See docs/core/debug/debug.md
 * TODO: make docs/core/debug/debug.md
 */

#ifndef NDEBUG

typedef struct DEBUG_Scene_Scanner_t DEBUG_Scene_Scanner;

///
/// A function to perform debug scanning operations with.
///
typedef DEBUG_Scene_Scanner (*m_DEBUG_Scene_Scanner_Func)();

typedef struct DEBUG_Scene_Scanner_t {
    Scene_Manager *p_scene_manager;
    Scene *p_scene__running;
    Scene *p_scene__current_in__scan;
    ///
    /// Moves p_scene__current_in__scan through available scenes in the manager,
    ///
    m_DEBUG_Scene_Scanner_Func m_iterate_scene;
    ///
    /// Causes the current scene to begin transitioning to the scene selected
    /// in p_scene__current_in__scan.
    ///
    m_DEBUG_Scene_Scanner_Func m_go_to__scene;
} DEBUG_Scene_Scanner;

DEBUG_Scene_Scanner debug_get_scene_scanner(Game *p_game);

#endif

#endif
