#include "ui/ui_window.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window_manager.h"
#include "ui/ui_context.h"

bool f_ui_window__close__default(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager) {
    release_p_ui_manager_from__ui_context(
            p_game, 
            get_p_ui_context_from__gfx_context(p_gfx_context), 
            p_gfx_window, 
            p_ui_manager);
    release_graphics_window_from__graphics_window_manager(
            p_game, 
            p_gfx_window);
    return true;
}
