#include "ui/ui_text_box.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "input/input.h"
#include "ui/ui_element.h"
#include "ui/ui_text.h"

void initialize_ui_element_as__text_box_with__const_c_str(
        UI_Element *p_ui_text_box,
        Font *p_font,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    initialize_ui_element_as__text_with__const_c_str(
            p_ui_text_box,
            p_font,
            p_text__const_c_str,
            size_of__text);

    set_ui_element__clicked_handler(
            p_ui_text_box, 
            m_ui_element__clicked_handler__text_box);
    set_ui_element__compose_handler(
            p_ui_text_box, 
            m_ui_element__compose_handler__text_box);
    set_ui_element__typed_handler(
            p_ui_text_box, 
            m_ui_element__typed_handler__text_box);
}

///
/// NOTE: takes ownership of the pM_c_str pointer.
///
void initialize_ui_element_as__text_box_with__pM_c_str(
        UI_Element *p_ui_text_box,
        Font *p_font,
        char *pM_text__c_str,
        Quantity__u32 size_of__text) {
    initialize_ui_element_as__text_with__pM_c_str(
            p_ui_text_box,
            p_font,
            pM_text__c_str,
            size_of__text);

    set_ui_element__clicked_handler(
            p_ui_text_box, 
            m_ui_element__clicked_handler__text_box);
    set_ui_element__compose_handler(
            p_ui_text_box, 
            m_ui_element__compose_handler__text_box);
    set_ui_element__typed_handler(
            p_ui_text_box, 
            m_ui_element__typed_handler__text_box);
}

void m_ui_element__clicked_handler__text_box(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    set_input_mode_of__input(
            get_p_input_from__game(p_game), 
            INPUT_MODE__WRITING);
    set_ui_element_as__focused(p_this_ui_element);
}

void handle_special_symbol__backspace__text_box(
        UI_Element *p_this_ui_text_box,
        Game *p_game) {
    if (p_this_ui_text_box->index_of__cursor_in__char_buffer
            == 0) {
        return;
    }
    if (!p_this_ui_text_box->size_of__char_buffer) {
        return;
    }

    for (Index__u32 index_of__char = 
            p_this_ui_text_box->index_of__cursor_in__char_buffer-1;
            index_of__char
            < p_this_ui_text_box->size_of__char_buffer-1;
            index_of__char++) {
        p_this_ui_text_box->pM_char_buffer[index_of__char] =
            p_this_ui_text_box->pM_char_buffer[index_of__char+1];
    }
    p_this_ui_text_box->index_of__cursor_in__char_buffer--;
    p_this_ui_text_box->pM_char_buffer[
        p_this_ui_text_box->size_of__char_buffer-1] = 0;
}

void handle_special_symbol__delete__text_box(
        UI_Element *p_this_ui_text_box,
        Game *p_game) {
    if (p_this_ui_text_box->index_of__cursor_in__char_buffer
            >= p_this_ui_text_box->size_of__char_buffer) {
        return;
    }
    if (!p_this_ui_text_box->size_of__char_buffer) {
        return;
    }

    for (Index__u32 index_of__char = 
            p_this_ui_text_box->index_of__cursor_in__char_buffer;
            index_of__char
            < p_this_ui_text_box->size_of__char_buffer-1;
            index_of__char++) {
        p_this_ui_text_box->pM_char_buffer[index_of__char] =
            p_this_ui_text_box->pM_char_buffer[index_of__char+1];
    }
    p_this_ui_text_box->pM_char_buffer[
        p_this_ui_text_box->size_of__char_buffer-1] = 0;
}

///
/// Returns true if a special symbol consumes input.
///
bool handle_special_symbols__text_box(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        unsigned char symbol) {
    switch (symbol) {
        case ASCII__ESCAPE:
            set_ui_element_as__NOT_focused(p_this_ui_text_box);
            break;
        case ASCII__BACKSPACE:
            handle_special_symbol__backspace__text_box(
                    p_this_ui_text_box, 
                    p_game);
            break;
        case ASCII__DELETE:
            handle_special_symbol__delete__text_box(
                    p_this_ui_text_box, 
                    p_game);
            break;
        case ASCII_LAVENDER__UP_ARROW:
            // TODO: impl
            break;
        case ASCII_LAVENDER__DOWN_ARROW:
            // TODO: impl
            break;
        case ASCII_LAVENDER__LEFT_ARROW:
            // TODO: impl
            break;
        case ASCII_LAVENDER__RIGHT_ARROW:
            // TODO: impl
            break;
        default:
            return false;
    }

    return true;
}

void m_ui_element__typed_handler__text_box(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        unsigned char symbol) {
    if (handle_special_symbols__text_box(
                p_this_ui_text_box, 
                p_game,
                symbol)) {
        return;
    }
    append_symbol_into__ui_text_box(
            p_this_ui_text_box, 
            symbol);    
}

void m_ui_element__typed_handler__text_box__numeric(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        unsigned char symbol) {
    if (handle_special_symbols__text_box(
                p_this_ui_text_box, 
                p_game,
                symbol)) {
        return;
    }
    if (symbol < '0' || symbol > '9')
        return;
    append_symbol_into__ui_text_box(
            p_this_ui_text_box, 
            symbol);    
}

void m_ui_element__typed_handler__text_box__alphanumeric(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        unsigned char symbol) {
    if (handle_special_symbols__text_box(
                p_this_ui_text_box, 
                p_game,
                symbol)) {
        return;
    }
    if (!((symbol > '0' && symbol < '9')
                || (symbol > 'a' && symbol < 'z')
                || (symbol > 'A' && symbol < 'Z'))) {
        return;
    }
    append_symbol_into__ui_text_box(
            p_this_ui_text_box, 
            symbol);    
}

void m_ui_element__compose_handler__text_box(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    m_ui_element__compose_handler__default_non_recursive(
            p_this_ui_element, 
            p_game, 
            p_gfx_window);
    m_ui_element__compose_handler__text(
            p_this_ui_element, 
            p_game, 
            p_gfx_window);
    m_ui_element__compose_handler__default_only_recursive(
            p_this_ui_element, 
            p_game, 
            p_gfx_window);
}
