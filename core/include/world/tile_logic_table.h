#ifndef TILE_LOGIC_TABLE_MANAGER_H
#define TILE_LOGIC_TABLE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table);

bool get_tile_logic_record_for__this_tile(
        Tile_Logic_Table *p_tile_logic_table,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile);

static inline
bool poll__is_tile__unpassable(
        Tile_Logic_Table *p_tile_logic_table,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table, 
            &record, 
            p_tile);
    return record.tile_logic_flags__u8
        & TILE_LOGIC_FLAG__IS_UNPASSABLE;
}

static inline
bool poll__is_tile__sight_blocking(
        Tile_Logic_Table *p_tile_logic_table,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table, 
            &record, 
            p_tile);
    return record.tile_logic_flags__u8
        & TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING;
}

static inline
bool poll__is_tile__without_ground(
        Tile_Logic_Table *p_tile_logic_table,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table, 
            &record, 
            p_tile);
    return record.tile_logic_flags__u8
        & TILE_LOGIC_FLAG__IS_WITHOUT_GROUND;
}

static inline
i32F4 poll__tile_height(
        Tile_Logic_Table *p_tile_logic_table,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table, 
            &record, 
            p_tile);
    return record.tile_height__i32F4;
}

#endif
