#ifndef UI_WINDOW_RECORD_H
#define UI_WINDOW_RECORD_H

#include "defines.h"

static inline
bool is_ui_window_record__valid(
        UI_Window_Record *p_ui_window_record) {
    return p_ui_window_record->f_ui_window__load 
        && p_ui_window_record->f_ui_window__close;
}

static inline
bool is_ui_window_record__allocating_a_sprite_pool(
        UI_Window_Record *p_ui_window_record) {
    return p_ui_window_record->signed_quantity_of__sprites > 0;
}

static inline
bool is_ui_window_record__using_parent_sprite_pool(
        UI_Window_Record *p_ui_window_record) {
    return p_ui_window_record->signed_quantity_of__sprites < 0;
}

#endif
