#include "defines_weak.h"
#include "nds/arm9/background.h"
#include "platform.h"
#include "ui/ui_element.h"
#include "vectors.h"
#include <ui/ui_slider.h>
#include <ui/nds_ui__slider.h>
#include <game.h>
#include <nds_defines.h>

void m_NDS_ui_slider__dragged_handler_for__backgrounds(
        UI_Element *p_this_draggable,
        Game *p_game) {
    NDS_Background *p_NDS_background =
        (NDS_Background *)p_this_draggable->p_ui_data;

    bool is_snapped_x_or__y_axis =
        is_ui_element__snapped_x_or_y_axis(p_this_draggable);

    Vector__3i32 position_for__bgSetScroll =
        p_NDS_background
        ->starting_position__3i32;

    i32 *p_starting_distance =
        (is_snapped_x_or__y_axis)
        ? &position_for__bgSetScroll
            .y__i32
        : &position_for__bgSetScroll
            .x__i32
        ;

    i32 spanning_length =
        (is_snapped_x_or__y_axis)
        ? p_NDS_background
            ->spanning_scroll_lengths__3i32.y__i32
        : p_NDS_background
            ->spanning_scroll_lengths__3i32.x__i32
        ;

    m_ui_slider__dragged_handler__default(
            p_this_draggable, 
            p_game);

    i32 offset = 
        get_offset_from__ui_slider_percentage(
                p_this_draggable, 
                spanning_length);

    *p_starting_distance -=
        offset;

    Vector__3i32 position_for__elements =
        position_for__bgSetScroll;
    position_for__elements.x__i32 *= -1;
    position_for__elements.x__i32 += 
        (get_width_from__p_ui_element(p_this_draggable->p_child) >> 1)
        + 4
        ;
    position_for__elements.y__i32 += 
        get_height_from__p_ui_element(p_this_draggable->p_child) >> 1;
    set_positions_of__ui_elements_in__succession(
            p_this_draggable->p_child, 
            position_for__elements, 
            24, 
            3, 
            28);

    bgSetScroll(
            p_NDS_background
            ->background_index_from__hardware, 
            position_for__bgSetScroll.x__i32, 
            -position_for__bgSetScroll.y__i32);
}
