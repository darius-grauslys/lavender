#ifndef TILE_LOGIC_TABLE_MANAGER_H
#define TILE_LOGIC_TABLE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_tile_logic_table_manager(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager);

void register_tile_logic_table_into__tile_logic_table_manager(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile_Logic_Record *p_tile_logic_records,
        m_Tile_Logic_Table__Get_Tile_Logic_Record m_get_tile_logic_record,
        Quantity__u32 quantity_of__records);

void get_tile_logic_record_for__this_tile(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile);

static inline
bool poll__is_tile__unpassable(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table_manager, 
            &record, 
            p_tile);
    return record.tile_logic_flags__u8
        & TILE_FLAGS__BIT_IS_UNPASSABLE;
}

bool poll__is_tile__sight_blocking(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile *p_tile) {
    Tile_Logic_Record record;
    get_tile_logic_record_for__this_tile(
            p_tile_logic_table_manager, 
            &record, 
            p_tile);
    return record.tile_logic_flags__u8
        & TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
}

#endif
