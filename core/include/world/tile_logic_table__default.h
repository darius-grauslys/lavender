#ifndef TILE_LOGIC_TABLE__DEFAULT_H
#define TILE_LOGIC_TABLE__DEFAULT_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/world/tile_layer.h"

static inline
Tile_Logic_Table *get_p_tile_logic_table__default_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context) {
    return p_tile_logic_context->array_of__pM_tile_logic_tables[
        Tile_Layer__Default];
}

static inline
Tile_Logic_Table 
*get_p_tile_logic_table__default_for__sight_blocking_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context) {
    return p_tile_logic_context->array_of__pM_tile_logic_tables[
        Tile_Layer__Default__Sight_Blocking];
}

static inline
Tile_Logic_Table 
*get_p_tile_logic_table__default_for__is_passable_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context) {
    return p_tile_logic_context->array_of__pM_tile_logic_tables[
        Tile_Layer__Default__Is_Passable];
}

static inline
Tile_Logic_Table 
*get_p_tile_logic_table__default_for__is_with_ground_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context) {
    return p_tile_logic_context->array_of__pM_tile_logic_tables[
        Tile_Layer__Default__Is_With_Ground];
}

#endif
