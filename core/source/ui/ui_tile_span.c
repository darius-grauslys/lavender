#include "ui/ui_tile_span.h"
#include "ui/ui_tile.h"
#include "defines.h"

void initialize_ui_tile_span_as__empty(
        UI_Tile_Span *p_ui_tile_span) {
    for (Index__u32 index_of__corner = 0;
            index_of__corner <
            UI_TILE_SPAN__QUANTITY_OF__CORNERS;
            index_of__corner++) {
        initialize_ui_tile_as__empty(
                &p_ui_tile_span->ui_tile__corners[
                index_of__corner]);
    }
    for (Index__u32 index_of__edge = 0;
            index_of__edge <
            UI_TILE_SPAN__QUANTITY_OF__