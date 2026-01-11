#ifndef UI_TEXT_H
#define UI_TEXT_H

#include "defines.h"
#include "defines_weak.h"

void initialize_ui_element_as__text_with__const_c_str(
        UI_Element *p_ui_text,
        Font *p_font,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text);

///
/// NOTE: takes ownership of the pM_c_str pointer.
///
void initialize_ui_element_as__text_with__pM_c_str(
        UI_Element *p_ui_text,
        Font *p_font,
        char *pM_text__c_str,
        Quantity__u32 size_of__text);

void initialize_ui_element_as__text_with__buffer_size(
        UI_Element *p_ui_text,
        Font *p_font,
        Quantity__u32 size_of__text);

void set_c_str_of__ui_text_with__const_c_str(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text);

void set_c_str_of__ui_text_with__pM_c_str(
        UI_Element *p_ui_text,
        char *pM_text__c_str,
        Quantity__u32 size_of__text);

void buffer_c_str_of__ui_text(
        UI_Element *p_ui_text,
        Quantity__u32 size_of__text);

void clear_c_str_of__ui_text(
        UI_Element *p_ui_text);

void set_cursor_of__ui_text(
        UI_Element *p_ui_text,
        Index__u32 index_of__cursor_in__c_str__u32);

void append_symbol_into__ui_text(
        UI_Element *p_ui_text,
        char symbol);

void append_c_str_into__ui_text(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text);

void insert_c_str_into__ui_text(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text,
        Index__u32 index_to__insert_at);

void m_ui_element__compose_handler__text(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__transformed_handler__text(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i32 position_NEW_of__hitbox__3i32,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__transformed_handler__text__centered(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Vector__3i32 position_NEW_of__hitbox__3i32,
        Game *p_game,
        Graphics_Window *p_graphics_window);

void m_ui_element__dispose_handler__text(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window);

static inline
const char *get_p_const_c_str_text_of__ui_text(
        UI_Element *p_ui_text,
        Quantity__u32 *p_OUT_size_of__text) {
    *p_OUT_size_of__text = p_ui_text->size_of__char_buffer;
    return p_ui_text->pM_char_buffer;
}

static inline
Typer *get_p_typer_of__ui_text(
        UI_Element *p_ui_text) {
    return &p_ui_text->typer;
}

#endif
