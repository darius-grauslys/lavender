#ifndef UI_WINDOW_H
#define UI_WINDOW_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/ui_element_kind.h"
#include "ui/ui_element.h"

bool f_ui_window__close__default(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager);

#endif
