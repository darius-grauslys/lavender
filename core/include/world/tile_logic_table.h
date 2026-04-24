#ifndef TILE_LOGIC_TABLE_MANAGER_H
#define TILE_LOGIC_TABLE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table);

bool allocate_tile_logic_table__tile_logic_entries(
        Tile_Logic_Table *p_tile_logic_table,
        Quantity__u16 quantity_of__tile_logic_records__u16);

void release_tile_logic_table__tile_logic_entries(
        Tile_Logic_Table *p_tile_logic_table);

static inline
Tile_Logic_Record *get_p_tile_logic_record_from__tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table,
        Index__u8 index_of__tile_logic_record__u8) {
#ifndef NDEBUG
    if (!p_tile_logic_table) {
        debug_error("get_p_tile_logic_record_from__tile_logic_table, p_tile_logic_table == 0.");
        return 0;
    }
    if (p_tile_logic_table->quantity_of__tile_logic_records__u16 
            <= index_of__tile_logic_record__u8) {
        debug_error("get_p_tile_logic_record_from__tile_logic_table, invalid tile logic record index.");
        return 0;
    }
#endif
    return &p_tile_logic_table->pM_tile_logic_records[
        index_of__tile_logic_record__u8];
}

#endif
