#include "world/tile_logic_table.h"
#include "defines.h"
#include "types/implemented/tile_kind.h"
#include "world/tile.h"

static void m_get_tile_logic_record__default(
        Tile_Logic_Table *p_tile_logic_table,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile) {
#ifndef NDEBUG
    if (p_tile->the_kind_of__tile
            >= p_tile_logic_table->quantity_of__records) {
        debug_error("m_get_tile_logic_record__default, cannot be used here as the_kind_of__tile exceeds maximum quantity of tile logic table.");
        return;
    }
#endif
    *p_tile_logic_record =
        p_tile_logic_table->tile_logic_table_data.tile_logic_record__tile_kind[
        get_tile_kind_from__tile(p_tile)];
}

void initialize_tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table) {
    memset(
            p_tile_logic_table,
            0,
            sizeof(Tile_Logic_Table));

    p_tile_logic_table->m_get_tile_logic_record =
        m_get_tile_logic_record__default;
}

bool get_tile_logic_record_for__this_tile(
        Tile_Logic_Table *p_tile_logic_table,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile) {
    memset(p_tile_logic_record,
            0,
            sizeof(Tile_Logic_Record));
    if (!p_tile_logic_table->m_get_tile_logic_record) {
        return false;
    }
    p_tile_logic_table->m_get_tile_logic_record(
            p_tile_logic_table,
            p_tile_logic_record,
            p_tile);
    return true;
}
