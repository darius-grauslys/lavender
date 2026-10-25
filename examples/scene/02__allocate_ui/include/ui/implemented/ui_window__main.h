#ifndef UI_WINDOW__MAIN_H
#define UI_WINDOW__MAIN_H

#include "defines.h"

bool allocate_ui_for__ui_window__main(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager,
        Identifier__u16 index_of__ui_element_offset__u16);

bool f_ui_window__close__main(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager);

#endif
