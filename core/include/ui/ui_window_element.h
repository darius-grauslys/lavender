#ifndef UI_WINDOW_ELEMENT_H
#define UI_WINDOW_ELEMENT_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/graphics_window_kind.h"

void initialize_ui_element_as__window_element_and__open_window(
        UI_Element *p_ui_window_element,
        Game *p_game,
        Graphics_Window_Kind the_kind_of__graphics_window_to__open,
        Identifier__u32 uuid_of__parent_window__u32);

#endif
