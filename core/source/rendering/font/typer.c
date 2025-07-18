#include "rendering/font/typer.h"
#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform.h"
#include "rendering/texture.h"
#include "vectors.h"

void initialize_typer(
        Typer *p_typer,
        i32 x, i32 y,
        Quantity__u32 width,
        Quantity__u32 height,
        Quantity__u32 quantity_of__spacing,
        i32 x__cursor, i32 y__cursor) {
    initialize_hitbox_as__allocated(
            &p_typer->text_bounding_box, 
            IDENTIFIER__UNKNOWN__u32,
            width, height, 
            get_vector__3i32F4_using__i32(
                x, y, 0));
    p_typer->cursor_position__3i32 =
        get_vector__3i32(
                x__cursor,
                y__cursor, 
                0);
    p_typer->quantity_of__space_in__pixels_between__lines = 
        quantity_of__spacing;
    p_typer->p_font = 0;
    initialize_texture(p_typer->texture_of__typer_target);
    p_typer->is_using_PLATFORM_texture_or__PLATFORM_graphics_window = true;
}

bool poll_typer_for__cursor_wrapping(
        Typer *p_typer,
        Font_Letter *p_font_letter) {

    Hitbox_AABB font_letter_hitbox;
    initialize_hitbox_as__allocated(
            &font_letter_hitbox, 
            IDENTIFIER__UNKNOWN__u32,
            p_font_letter->width_of__font_letter, 
            p_font_letter->height_of__font_letter,
            get_vector__3i32F4_using__i32(0, 0, 0));

    Vector__3i32F4 hitbox_position =
        get_vector__3i32F4_using__i32(
                p_typer->cursor_position__3i32.x__i32
                + (p_font_letter->width_of__font_letter >> 1),
                p_typer->cursor_position__3i32.y__i32
                + (p_font_letter->height_of__font_letter >> 1),
                0);

    add_p_vectors__3i32F4(
            &hitbox_position, 
            &p_typer->text_bounding_box.position__3i32F4);

    hitbox_position.x__i32F4 -=
        i32_to__i32F4(p_typer->text_bounding_box.width__quantity_u32 >> 1);
    hitbox_position.y__i32F4 -=
        i32_to__i32F4(p_typer->text_bounding_box.height__quantity_u32 >> 1);

    font_letter_hitbox.position__3i32F4 =
        hitbox_position;

    if (is_this_hitbox__fully_inside_this_hitbox__without_velocity(
                &font_letter_hitbox,
                &p_typer->text_bounding_box)) {
        return true;
    }

    Vector__3i32 aa;
    initialize_vector_3i32_as__aa_bb_without__velocity(
            &aa, 
            &p_typer->text_bounding_box, 
            DIRECTION__SOUTH_WEST);

    p_typer->cursor_position__3i32.x__i32 = 0;
    p_typer->cursor_position__3i32.y__i32 +=
        p_typer->p_font->max_height_of__font_letter
        + p_typer->quantity_of__space_in__pixels_between__lines;

    hitbox_position =
        get_vector__3i32F4_using__i32(
                p_typer->cursor_position__3i32.x__i32
                + (p_font_letter->width_of__font_letter >> 1),
                p_typer->cursor_position__3i32.y__i32
                + (p_font_letter->height_of__font_letter >> 1),
                0);

    add_p_vectors__3i32F4(
            &hitbox_position, 
            &p_typer->text_bounding_box.position__3i32F4);

    hitbox_position.x__i32F4 -=
        i32_to__i32F4(p_typer->text_bounding_box.width__quantity_u32 >> 1);
    hitbox_position.y__i32F4 -=
        i32_to__i32F4(p_typer->text_bounding_box.height__quantity_u32 >> 1);

    font_letter_hitbox.position__3i32F4 =
        hitbox_position;

    return is_this_hitbox__fully_inside_this_hitbox__without_velocity(
                &font_letter_hitbox,
                &p_typer->text_bounding_box);
}

void put_c_string_in__typer(
        Gfx_Context *p_gfx_context,
        Typer *p_typer,
        const char *c_string,
        Quantity__u32 max_length_of__c_string) {
    if (!max_length_of__c_string)
        return;
    if (!*c_string)
        return;

    do {
        char letter = *c_string;
        switch (letter) {
            default:
                break;
            case '\n':
            case '\r':
                p_typer->cursor_position__3i32.y__i32 +=
                    p_typer->p_font->max_height_of__font_letter;
                p_typer->cursor_position__3i32.x__i32 = 0;
                return;
        }
        Font_Letter *p_font_letter =
            get_p_font_letter_from__typer(
                p_typer, 
                letter);
        if (!poll_typer_for__cursor_wrapping(
                p_typer, 
                p_font_letter)) {
            break;
        }
        PLATFORM_put_char_in__typer(
                p_gfx_context, 
                p_typer, 
                letter);
        offset_typer_by__font_letter(
                p_typer, 
                p_font_letter);
    } while (--max_length_of__c_string
            && *(++c_string));
}
