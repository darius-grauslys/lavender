#ifndef TILE_LOGIC_TABLE_REGISTRAR_H
#define TILE_LOGIC_TABLE_REGISTRAR_H

#include "defines.h"

void register_tile_logic_tables(
        Game *p_game,
        Tile_Logic_Context *p_tile_logic_context);

// See example: examples/template-files/include/types/implemented/world/tile.h
u8 get_tile_logic_index_by__tile_layer_from__tile(
        Tile *p_tile,
        Tile_Layer the_tile_layer) {
#ifndef NDEBUG
    if (Tile_Layer__Unknown <= the_tile_layer) {
        debug_error("get_tile_logic_index_by__tile_layer_from__tile, invalid tile layer provided.");
        return 0;
    }
#endif

    // GET-LOGIC-BEGIN
    switch (the_tile_layer) {
        case Tile_Layer__Default:
        case Tile_Layer__Ground:
            return (p_tile->array_of__tile_data__u8[0] & (MASK(4) << 4))
                >> 4
                ;
        case Tile_Layer__Cover:
            return (p_tile->array_of__tile_data__u8[2] & (MASK(6) << 2))
                >> 2
                ;
        default:
            return 0;
    }
    // GET-LOGIC-END
}

u8 get_tile_animation_index_by__tile_layer_from__tile(
        Tile *p_tile,
        Tile_Layer the_tile_layer) {
#ifndef NDEBUG
    if (Tile_Layer__Unknown <= the_tile_layer) {
        debug_error("get_tile_animation_index_by__tile_layer_from__tile, invalid tile layer provided.");
        return 0;
    }
#endif

    // GET-ANIMATION-BEGIN
    switch (the_tile_layer) {
        case Tile_Layer__Default:
        case Tile_Layer__Ground:
            return (p_tile->array_of__tile_data__u8[0] & (MASK(4)))
                >> 4
                ;
        case Tile_Layer__Cover:
            return (p_tile->array_of__tile_data__u8[2] & (MASK(4) << 2))
                >> 2
                ;
        default:
            return 0;
    }
    // GET-ANIMATION-END
}

#endif
