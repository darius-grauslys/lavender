#include "defines.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "ui/ui_tile.h"
#include "ui/ui_tile_map.h"
#include "ui/ui_tile_span.h"

void initialize_ui_tile_map__small_as__deallocated(
        UI_Tile_Map__Small *p_ui_tile_map__small) {
    p_ui_tile_map__small->ui_tile_map__flags =
        UI_TILE_MAP__FLAGS__NONE;
    memset(
            p_ui_tile_map__small
            ->ui_tile_data__small,
            UI_Tile_Kind__None,
            sizeof(UI_Tile_Raw)
            * UI_TILE_MAP__SMALL__WIDTH
            * UI_TILE_MAP__SMALL__HEIGHT);
}

void initialize_ui_tile_map__medium_as__deallocated(
        UI_Tile_Map__Medium *p_ui_tile_map__medium) {
    p_ui_tile_map__medium->ui_tile_map__flags =
        UI_TILE_MAP__FLAGS__NONE;
    memset(
            p_ui_tile_map__medium
            ->ui_tile_data__medium,
            UI_Tile_Kind__None,
            sizeof(UI_Tile_Raw)
            * UI_TILE_MAP__MEDIUM__WIDTH
            * UI_TILE_MAP__MEDIUM__HEIGHT);
}

void initialize_ui_tile_map__large_as__deallocated(
        UI_Tile_Map__Large *p_ui_tile_map__large) {
    p_ui_tile_map__large->ui_tile_map__flags =
        UI_TILE_MAP__FLAGS__NONE;
    memset(
            p_ui_tile_map__large
            ->ui_tile_data__large,
            UI_Tile_Kind__None,
            sizeof(UI_Tile_Raw)
            * UI_TILE_MAP__LARGE__WIDTH
            * UI_TILE_MAP__LARGE__HEIGHT);
}

void initialize_ui_tile_map__wrapper(
        UI_Tile_Map__Wrapper *p_ui_tile_map__wrapper,
        UI_Tile_Raw *p_ui_tile_data,
        Quantity__u32 width_of__tile_map,
        Quantity__u32 height_of__tile_map,
        UI_Tile_Map_Size catagory_size_of__ui_tile_map) {
    p_ui_tile_map__wrapper->p_ui_tile_data =
        p_ui_tile_data;
    p_ui_tile_map__wrapper->height_of__ui_tile_map =
        height_of__tile_map;
    p_ui_tile_map__wrapper->width_of__ui_tile_map =
        width_of__tile_map;
    p_ui_tile_map__wrapper->catagory_size_of__ui_tile_map =
        catagory_size_of__ui_tile_map;
}

void set_ui_tile_map__wrapper__utilized_size(
        UI_Tile_Map__Wrapper *p_ui_tile_map__wrapper,
        Quantity__u32 width__u32,
        Quantity__u32 height__u32) {
    Quantity__u32 area_of__allocation = 0;
    switch(get_catagory_size_of__ui_tile_map__wrapper(
                *p_ui_tile_map__wrapper)) {
        default:
            debug_error("set_ui_tile_map__wrapper__utilized_size, ui_tile_map__wrapper is invalid.");
            return;
        case UI_Tile_Map_Size__Small:
            area_of__allocation = 
                UI_TILE_MAP__SMALL__WIDTH
                * UI_TILE_MAP__SMALL__HEIGHT
                ;
            break;
        case UI_Tile_Map_Size__Medium:
            area_of__allocation = 
                UI_TILE_MAP__MEDIUM__WIDTH
                * UI_TILE_MAP__MEDIUM__HEIGHT
                ;
            break;
        case UI_Tile_Map_Size__Large:
            area_of__allocation = 
                UI_TILE_MAP__LARGE__WIDTH
                * UI_TILE_MAP__LARGE__HEIGHT
                ;
            break;
    }

    if (width__u32 * height__u32
            > area_of__allocation) {
            debug_error("set_ui_tile_map__wrapper__utilized_size, width and height exceeds allocated limit.");
        return;
    }

    p_ui_tile_map__wrapper->width_of__ui_tile_map = width__u32;
    p_ui_tile_map__wrapper->height_of__ui_tile_map = height__u32;
}

void fill_ui_tile_map(
        UI_Tile_Map__Wrapper ui_tile_map__wrapper,
        UI_Tile ui_tile) {
    for (Index__u32 index_of__y = 0;
            index_of__y
            < ui_tile_map__wrapper.height_of__ui_tile_map;
            index_of__y++) {
        for (Index__u32 index_of__x = 0;
                index_of__x
                < ui_tile_map__wrapper.width_of__ui_tile_map;
                index_of__x++) {
            ui_tile_map__wrapper
                .p_ui_tile_data[
                index_of__x
                    + index_of__y
                    * ui_tile_map__wrapper
                        .width_of__ui_tile_map] =
                        get_ui_tile_raw_from__ui_tile(&ui_tile);
        }
    }
}

void fill_ui_tile_map_in__this_region(
        UI_Tile_Map__Wrapper ui_tile_map__wrapper,
        UI_Tile ui_tile,
        Index__u32 index_x__start,
        Index__u32 index_y__start,
        Quantity__u32 width,
        Quantity__u32 height) {
    for (Index__u32 index_of__y = 0;
            index_of__y < height;
            index_of__y++) {
        Index__u32 y = 
            index_of__y
            + index_y__start;
        if (y > ui_tile_map__wrapper.height_of__ui_tile_map)
            break;
        for (Index__u32 index_of__x = 0;
                index_of__x < width;
                index_of__x++) {
            Index__u32 x = 
                index_of__x
                + index_x__start;
            if (x > ui_tile_map__wrapper.width_of__ui_tile_map)
                break;
            ui_tile_map__wrapper
                .p_ui_tile_data[
                x + y
                * ui_tile_map__wrapper
                    .width_of__ui_tile_map] =
                    get_ui_tile_raw_from__ui_tile(&ui_tile);
        }
    }
}

void generate_ui_span_in__ui_tile_map(
        UI_Tile_Map__Wrapper ui_tile_map__wrapper,
        const UI_Tile_Span *p_ui_tile_span,
        Quantity__u32 width_of__ui_tile_span__u32,
        Quantity__u32 height_of__ui_tile_span__u32,
        Index__u32 index_x__u32,
        Index__u32 index_y__u32) {
    for (Index__u32 index_y_of__ui_tile_span__u32 = 0;
            index_y_of__ui_tile_span__u32 
            < height_of__ui_tile_span__u32;
            index_y_of__ui_tile_span__u32++) {
        u32 y = 
            get_height_of__ui_tile_map__wrapper(
                    ui_tile_map__wrapper)
            - (index_y__u32
            + index_y_of__ui_tile_span__u32)
            - 1
            ;
        if (y >= get_height_of__ui_tile_map__wrapper(
                    ui_tile_map__wrapper)) {
            continue;
        }
        for (Index__u32 index_x_of__ui_tile_span__u32 = 0;
                index_x_of__ui_tile_span__u32
                < width_of__ui_tile_span__u32;
                index_x_of__ui_tile_span__u32++) {
            u32 x = 
                index_x__u32
                + index_x_of__ui_tile_span__u32
                ;
            if (x >= get_width_of__ui_tile_map__wrapper(
                        ui_tile_map__wrapper)) {
                continue;
            }

            UI_Tile_Raw ui_tile_raw = 
                get_ui_tile_raw_from__ui_tile(
                        get_ui_tile_of__ui_tile_span(
                            p_ui_tile_span, 
                            width_of__ui_tile_span__u32, 
                            height_of__ui_tile_span__u32, 
                            index_x_of__ui_tile_span__u32, 
                            index_y_of__ui_tile_span__u32));

            ui_tile_map__wrapper.p_ui_tile_data[
                x + y
                    * get_width_of__ui_tile_map__wrapper(
                            ui_tile_map__wrapper)] =
                    ui_tile_raw;
        }
    }
}
