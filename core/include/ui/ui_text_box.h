#ifndef UI_TEXT_BOX_H
#define UI_TEXT_BOX_H

#include "defines.h"
#include "defines_weak.h"
#include "ui/ui_text.h"

void initialize_ui_element_as__text_box_with__const_c_str(
        UI_Element *p_ui_text_box,
        Font *p_font,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text);

///
/// NOTE: takes ownership of the pM_c_str pointer.
///
void initialize_ui_element_as__text_box_with__pM_c_str(
        UI_Element *p_ui_text_box,
        Font *p_font,
        char *pM_text__c_str,
        Quantity__u32 size_of__text);

void initialize_ui_element_as__text_box_with__buffer_size(
        UI_Element *p_ui_text_box,
        Font *p_font,
        Quantity__u32 size_of__text);

void m_ui_element__compose_handler__text_box(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window);

void m_ui_element__clicked_handler__text_box(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window);

void m_ui_element__typed_handler__text_box(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        Graphics_Window *p_graphics_window,
        unsigned char symbol);

void m_ui_element__typed_handler__text_box__numeric(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        Graphics_Window *p_graphics_window,
        unsigned char symbol);

void m_ui_element__typed_handler__text_box__alphanumeric(
        UI_Element *p_this_ui_text_box,
        Game *p_game,
        Graphics_Window *p_graphics_window,
        unsigned char symbol);

static inline
void set_c_str_of__ui_text_box_with__const_c_str(
        UI_Element *p_ui_text_box,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    set_c_str_of__ui_text_with__const_c_str(
            p_ui_text_box, 
            p_text__const_c_str, 
            size_of__text);
}

static inline
void set_c_str_of__ui_text_box_with__pM_c_str(
        UI_Element *p_ui_text_box,
        char *pM_text__c_str,
        Quantity__u32 size_of__text) {
    set_c_str_of__ui_text_with__pM_c_str(
            p_ui_text_box,
            pM_text__c_str,
            size_of__text);
}

static inline
void buffer_c_str_of__ui_text_box(
        UI_Element *p_ui_text_box,
        Quantity__u32 size_of__text) {
    buffer_c_str_of__ui_text(
            p_ui_text_box,
            size_of__text);
}

static inline
void clear_c_str_of__ui_text_box(
        UI_Element *p_ui_text_box) {
    clear_c_str_of__ui_text(
            p_ui_text_box);
}

static inline
void set_cursor_of__ui_text_box(
        UI_Element *p_ui_text_box,
        Index__u32 index_of__cursor_in__c_str__u32) {
    set_cursor_of__ui_text(
            p_ui_text_box,
            index_of__cursor_in__c_str__u32);
}

static inline
void append_symbol_into__ui_text_box(
        UI_Element *p_ui_text_box,
        char symbol) {
    append_symbol_into__ui_text(
            p_ui_text_box,
            symbol);
}

static inline
void append_c_str_into__ui_text_box(
        UI_Element *p_ui_text_box,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    append_c_str_into__ui_text(
            p_ui_text_box,
            p_text__const_c_str,
            size_of__text);
}

static inline
void insert_c_str_into__ui_text_box(
        UI_Element *p_ui_text_box,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text,
        Index__u32 index_to__insert_at) {
    insert_c_str_into__ui_text(
            p_ui_text_box,
            p_text__const_c_str,
            size_of__text,
            index_to__insert_at);
}

static inline
const char *get_p_const_c_str_text_of__ui_text_box(
        UI_Element *p_ui_text_box,
        Quantity__u32 *p_OUT_size_of__text) {
    return get_p_const_c_str_text_of__ui_text(
            p_ui_text_box, 
            p_OUT_size_of__text);
}

static inline
Typer *get_p_typer_of__ui_text_box(
        UI_Element *p_ui_text_box) {
    return get_p_typer_of__ui_text(p_ui_text_box);
}

#endif
