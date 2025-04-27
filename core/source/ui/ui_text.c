#include "ui/ui_text.h"
#include "collisions/hitbox_aabb.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "numerics.h"
#include "rendering/font/typer.h"
#include "ui/ui_element.h"

void initialize_ui_element_as__text_with__const_c_str(
        UI_Element *p_ui_text,
        Font *p_font,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    if (p_ui_text->pM_char_buffer) {
        debug_warning("If you're trying to set the text of this element, use set_c_str__ui_text_with__...");
        debug_error("initialize_ui_element_as__text_with__const_c_str, ui_element is not properly initialized, or is being re-initialized as ui_text!");
        return;
    }
    initialize_ui_element(
            p_ui_text, 
            0, 
            0, 
            0, 
            UI_Element_Kind__Text, 
            p_ui_text->ui_flags);
    p_ui_text->pM_char_buffer = malloc(size_of__text);
    if (!p_ui_text->pM_char_buffer) {
        set_ui_element_as__disabled(p_ui_text);
        p_ui_text->size_of__char_buffer = 0;
        debug_error("initialize_ui_element_as__text_with__const_c_str, failed to allocate pM_char_buffer.");
        return;
    }

    initialize_typer_with__font(
            get_p_typer_of__ui_text(p_ui_text), 
            0, 0, 
            0, 0, 
            0, 
            0, 0, 
            p_font);

    set_ui_element__compose_handler(
            p_ui_text, 
            m_ui_element__compose_handler__text);
    set_ui_element__transformed_handler(
            p_ui_text, 
            m_ui_element__transformed_handler__text);
    set_ui_element__dispose_handler(
            p_ui_text, 
            m_ui_element__dispose_handler__text);

#warning TODO: clamp c_str size based on config.
    p_ui_text->size_of__char_buffer = size_of__text;
    memcpy(
            p_ui_text->pM_char_buffer,
            p_text__const_c_str,
            size_of__text);
}

///
/// NOTE: takes ownership of the pM_c_str pointer.
///
void initialize_ui_element_as__text_with__pM_c_str(
        UI_Element *p_ui_text,
        Font *p_font,
        char *pM_text__c_str,
        Quantity__u32 size_of__text) {
    if (p_ui_text->pM_char_buffer) {
        debug_warning("If you're trying to set the text of this element, use set_c_str__ui_text_with__...");
        debug_error("initialize_ui_element_as__text_with__pM_c_str, ui_element is not properly initialized, or is being re-initialized as ui_text!");
        return;
    }
    initialize_ui_element(
            p_ui_text, 
            0, 
            0, 
            0, 
            UI_Element_Kind__Text, 
            p_ui_text->ui_flags);

    initialize_typer_with__font(
            get_p_typer_of__ui_text(p_ui_text), 
            0, 0, 
            0, 0, 
            0, 
            0, 0, 
            p_font);

    set_ui_element__compose_handler(
            p_ui_text, 
            m_ui_element__compose_handler__text);
    set_ui_element__transformed_handler(
            p_ui_text, 
            m_ui_element__transformed_handler__text);
    set_ui_element__dispose_handler(
            p_ui_text, 
            m_ui_element__dispose_handler__text);

    p_ui_text->pM_char_buffer = pM_text__c_str;
#warning TODO: clamp c_str size based on config.
    p_ui_text->size_of__char_buffer = 
        (pM_text__c_str)
        ? size_of__text
        : 0
        ;
}

static inline
void free_pM_text_of__ui_text(
        UI_Element *p_ui_element) {
    if (p_ui_element->pM_char_buffer) {
        free(p_ui_element->pM_char_buffer);
        p_ui_element->pM_char_buffer = 0;
    }
}

void set_c_str_of__ui_text_with__const_c_str(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    free_pM_text_of__ui_text(p_ui_text);
    p_ui_text->pM_char_buffer = malloc(size_of__text);
    if (!p_ui_text->pM_char_buffer) {
        p_ui_text->size_of__char_buffer = 0;
        debug_error("set_c_str_of__ui_text_with__const_c_str, failed to allocate pM_char_buffer.");
        return;
    }
    p_ui_text->size_of__char_buffer = size_of__text;
}

void set_c_str_of__ui_text_with__pM_c_str(
        UI_Element *p_ui_text,
        char *pM_text__c_str,
        Quantity__u32 size_of__text) {
    free_pM_text_of__ui_text(p_ui_text);
    p_ui_text->pM_char_buffer = pM_text__c_str; 
    p_ui_text->size_of__char_buffer = 
        (pM_text__c_str)
        ? size_of__text
        : 0
        ;
}

void buffer_c_str_of__ui_text(
        UI_Element *p_ui_text,
        Quantity__u32 size_of__text) {
    free_pM_text_of__ui_text(p_ui_text);
    if (!size_of__text) {
        p_ui_text->size_of__char_buffer = 0;
        return;
    }
    p_ui_text->pM_char_buffer = malloc(size_of__text); 
    p_ui_text->size_of__char_buffer = size_of__text;
}

void clear_c_str_of__ui_text(
        UI_Element *p_ui_text) {
#warning TODO: clamp c_str size based on config.
    memset(p_ui_text->pM_char_buffer,
            0,
            p_ui_text->size_of__char_buffer);
}

void set_cursor_of__ui_text(
        UI_Element *p_ui_text,
        Index__u32 index_of__cursor_in__c_str__u32) {
    p_ui_text->index_of__cursor_in__char_buffer = 
        (index_of__cursor_in__c_str__u32
         >= p_ui_text->size_of__char_buffer)
        ? p_ui_text->size_of__char_buffer - 1
        : index_of__cursor_in__c_str__u32
        ;
}

void append_symbol_into__ui_text(
        UI_Element *p_ui_text,
        char symbol) {
    if (p_ui_text->index_of__cursor_in__char_buffer
            >= p_ui_text->size_of__char_buffer) {
        debug_warning__verbose("append_symbol_into__ui_text, text buffer is full.");
        return;
    }

    p_ui_text->pM_char_buffer[
        p_ui_text->index_of__cursor_in__char_buffer++] = symbol;
}

void append_c_str_into__ui_text(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text) {
    Quantity__u32 clamp__u32 =
        min__u32(
                size_of__text, 
                p_ui_text->size_of__char_buffer
                - p_ui_text->index_of__cursor_in__char_buffer);
    memcpy(
            p_ui_text->pM_char_buffer
            + p_ui_text->index_of__cursor_in__char_buffer,
            p_text__const_c_str,
            clamp__u32);
}

void insert_c_str_into__ui_text(
        UI_Element *p_ui_text,
        const char *p_text__const_c_str,
        Quantity__u32 size_of__text,
        Index__u32 index_to__insert_at) {
    debug_error("insert_c_str_into__ui_text, impl");
}

void m_ui_element__compose_handler__text(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    set_PLATFORM_graphics_window_target_for__typer(
            get_p_typer_of__ui_text(p_this_ui_element), 
            p_graphics_window->p_PLATFORM_gfx_window);
    reset_typer_cursor(get_p_typer_of__ui_text(p_this_ui_element));
    put_c_string_in__typer(
            get_p_gfx_context_from__game(p_game), 
            get_p_typer_of__ui_text(p_this_ui_element), 
            p_this_ui_element->pM_char_buffer, 
            p_this_ui_element->size_of__char_buffer);
}

void m_ui_element__transformed_handler__text(
        UI_Element *p_this_ui_element,
        Hitbox_AABB *p_hitbox_aabb,
        Game *p_game) {
    set_typer__position(
            get_p_typer_of__ui_text(p_this_ui_element),
            get_position_3i32_of__hitbox_aabb(
                p_hitbox_aabb));

    set_typer__bounding_box_size(
            get_p_typer_of__ui_text(p_this_ui_element),
            get_width_u32_of__hitbox_aabb(p_hitbox_aabb), 
            get_height_u32_of__hitbox_aabb(p_hitbox_aabb));
}

void m_ui_element__dispose_handler__text(
        UI_Element *p_this_ui_element,
        Game *p_game) {
    free_pM_text_of__ui_text(p_this_ui_element);
    m_ui_element__dispose_handler__default(
            p_this_ui_element, 
            p_game);
}
