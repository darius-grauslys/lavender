#ifndef UI_CONTEXT_H
#define UI_CONTEXT_H

#include "defines.h"
#include "defines_weak.h"

void initialize_ui_context(UI_Context *p_ui_context);

UI_Manager *allocate_p_ui_manager_from__ui_context(
        UI_Context *p_ui_context,
        Identifier__u32 uuid_of__ui_manager__u32);

UI_Manager *get_p_ui_manager_by__uuid_from__ui_context(
        UI_Context *p_ui_context,
        Identifier__u32 uuid_of__ui_manager);

void release_p_ui_manager_from__ui_context(
        Game *p_game,
        Identifier__u32 uuid_of__ui_manager__u32);

void register_ui_window_into__ui_context(
        UI_Context *p_ui_context,
        f_UI_Window__Load f_ui_window__load,
        f_UI_Window__Close f_ui_window__close,
        Graphics_Window_Kind the_kind_of__window,
        Signed_Quantity__i32 signed_quantity_of__sprites);

///
/// the sprite_manager can be null. If so open_ui_window
/// will attempt to allocate a new one.
///
/// NOTE: the sprite_manager will be shared if non-null.
///
Graphics_Window *open_ui_window(
        Game *p_game,
        Graphics_Window_Kind the_kind_of__window_to__open);

///
/// Will only close the given Graphics_Window uuid if
/// the resolved Graphics_Window has a non-null ui_manager pointer.
///
void close_ui_window(
        Game *p_game,
        Identifier__u32 uuid_of__graphics_window);

#endif
