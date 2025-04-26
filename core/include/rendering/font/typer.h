#ifndef TYPER_H
#define TYPER_H

#include "defines_weak.h"
#include <defines.h>

void initialize_typer(
        Typer *p_typer,
        i32 x, i32 y,
        Quantity__u32 width,
        Quantity__u32 height,
        Quantity__u32 quantity_of__spacing,
        i32 x__cursor, i32 y__cursor);

static inline
void initialize_typer_with__font(
        Typer *p_typer,
        i32 x, i32 y,
        Quantity__u32 width,
        Quantity__u32 height,
        Quantity__u32 quantity_of__spacing,
        i32 x__cursor, i32 y__cursor,
        Font *p_font) {
    initialize_typer(
            p_typer, 
            x, 
            y, 
            width, 
            height, 
            quantity_of__spacing,
            x__cursor, 
            y__cursor);

    p_typer->p_font = p_font;
}

bool poll_typer_for__cursor_wrapping(
        Typer *p_typer,
        Font_Letter *p_font_letter);

void put_c_string_in__typer(
        Gfx_Context *p_gfx_context,
        Typer *p_typer,
        const char *c_string,
        Quantity__u32 max_length_of__c_string);

static inline
void set_typer__cursor(
        Typer *p_typer,
        Vector__3i32 position__3i32) {
    p_typer->cursor_position__3i32 =
        position__3i32;
}

static inline
void offset_typer_by__font_letter(
        Typer *p_typer,
        Font_Letter *p_font_letter) {
    p_typer->cursor_position__3i32
        .x__i32 +=
        p_font_letter->width_of__font_letter;
}

static inline
Font_Letter *get_p_font_letter_from__typer(
        Typer *p_typer,
        unsigned char letter) {
    return &p_typer->p_font->font_lookup_table[letter];
}

static inline
void set_PLATFORM_texture_target_for__typer(
        Typer *p_typer,
        PLATFORM_Texture *p_PLATFORM_texture) {
    p_typer->p_PLATFORM_texture__typer_target =
        p_PLATFORM_texture;
    p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window =
        true;
}

static inline
void set_PLATFORM_graphics_window_target_for__typer(
        Typer *p_typer,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window) {
    p_typer->p_PLATFORM_graphics_window__typer_target =
        p_PLATFORM_graphics_window;
    p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window =
        false;
}

static inline
bool is_typer_targetting__PLATFORM_texture(
        Typer *p_typer) {
    return p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window;
}

static inline
bool is_typer_targetting__PLATFORM_graphics_window(
        Typer *p_typer) {
    return !p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window;
}

#endif
