#include <ui/menu/nds_ui_window__menu__multiplayer.h>
#include <ui/nds_ui.h>
#include <ui/ui_element.h>
#include <ui/ui_button.h>
#include <ui/ui_manager.h>
#include <vectors.h>
#include <defines.h>
#include <game.h>
// THIS CODE IS AUTO GENERATED. Go to ./nds/assets/ui/xml/ instead of modifying this file.

UI_Element *NDS_allocate_ui_for__nds_ui_window__menu__multiplayer(Game *p_game, UI_Manager *p_ui_manager){
    UI_Element *p_ui_iterator = 0;
    UI_Element *p_ui_iterator_previous_previous = 0;
    UI_Element *p_ui_iterator_previous = 0;
    UI_Element *p_ui_iterator_child = 0;
    UI_Element *p_button__singleplayer = allocate_ui_element_from__ui_manager(p_ui_manager);
    initialize_ui_element_as__button(p_button__singleplayer, 80, 24, get_vector__3i32(52 + 0, 72 + 0, 0), m_ui_button__clicked_handler__default, false, false);

    UI_Element *p_button__multiplayer = allocate_ui_element_from__ui_manager(p_ui_manager);
    initialize_ui_element_as__button(p_button__multiplayer, 80, 24, get_vector__3i32(52 + 0, 116 + 0, 0), m_ui_button__clicked_handler__default, false, false);

    UI_Element *p_button__settings = allocate_ui_element_from__ui_manager(p_ui_manager);
    initialize_ui_element_as__button(p_button__settings, 80, 24, get_vector__3i32(52 + 0, 160 + 0, 0), m_ui_button__clicked_handler__default, false, false);

}
