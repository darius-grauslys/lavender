#include "world/tile_logic_table_manager.h"
#include "defines.h"
#include "types/implemented/tile_kind.h"
#include "world/tile.h"

static inline
Tile_Logic_Table *get_p_tile_logic_table_by__index_from__tile_logic_table_manager(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Index__u32 index_of__tile_logic_table) {
#ifndef NDEBUG
    if (!p_tile_logic_table_manager) {
        debug_error("get_p_tile_logic_table_by__index_from__tile_logic_table_manager, p_tile_logic_table_manager == 0.");
        return 0;
    }
    if (index_of__tile_logic_table >
            MAX_QUANTITY_OF__TILE_LOGIC_TABLES) {
        debug_error("get_p_tile_logic_table_by__index_from__tile_logic_table_manager, index out of bounds.");
        return 0;
    }
#endif
    return &p_tile_logic_table_manager
        ->tile_logic_tables[
        index_of__tile_logic_table];
}

static void m_get_tile_logic_record__default(
        Tile_Logic_Table *p_tile_logic_table,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile) {
#ifndef NDEBUG
    if (p_tile->the_kind_of_tile__this_tile_is
            >= p_tile_logic_table->quantity_of__records) {
        debug_error("m_get_tile_logic_record__default, cannot be used here as the_kind_of__tile exceeds maximum quantity of tile logic table.");
        return;
    }
#endif
    *p_tile_logic_record =
        p_tile_logic_table->p_tile_logic_records[
        get_tile_kind_from__tile(p_tile)];
}

void initialize_tile_logic_table_manager(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager) {
    memset(
            p_tile_logic_table_manager,
            0,
            sizeof(Tile_Logic_Table_Manager));

    for (Index__u32 index_of__tile_logic_table = 0;
            index_of__tile_logic_table
            < MAX_QUANTITY_OF__TILE_LOGIC_TABLES;
            index_of__tile_logic_table++) {
        Tile_Logic_Table *p_tile_logic_table =
            get_p_tile_logic_table_by__index_from__tile_logic_table_manager(
                    p_tile_logic_table_manager, 
                    index_of__tile_logic_table);

        p_tile_logic_table->m_get_tile_logic_record =
            m_get_tile_logic_record__default;
    }

    p_tile_logic_table_manager->tile_logic_tables[0]
        .quantity_of__records = Tile_Kind__Unknown;
}

void register_tile_logic_table_into__tile_logic_table_manager(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile_Logic_Record *p_tile_logic_records,
        m_Tile_Logic_Table__Get_Tile_Logic_Record m_get_tile_logic_record,
        Quantity__u32 quantity_of__records) {
    for (Index__u32 index_of__tile_logic_table = 0;
            index_of__tile_logic_table 
            < MAX_QUANTITY_OF__TILE_LOGIC_TABLES;
            index_of__tile_logic_table++) {
        Tile_Logic_Table *p_tile_logic_table =
            get_p_tile_logic_table_by__index_from__tile_logic_table_manager(
                    p_tile_logic_table_manager, 
                    index_of__tile_logic_table);

        if (!p_tile_logic_table->p_tile_logic_records) {
            p_tile_logic_table->p_tile_logic_records =
                p_tile_logic_records;
            p_tile_logic_table->m_get_tile_logic_record =
                m_get_tile_logic_record;
            p_tile_logic_table->quantity_of__records =
                quantity_of__records;

            return;
        }
    }

    debug_error("register_tile_logic_table_into__tile_logic_table_manager, too many tables registered.");
}

void get_tile_logic_record_for__this_tile(
        Tile_Logic_Table_Manager *p_tile_logic_table_manager,
        Tile_Logic_Record *p_tile_logic_record,
        Tile *p_tile) {
    for (Index__u32 index_of__tile_logic_table = 0;
            index_of__tile_logic_table 
            < MAX_QUANTITY_OF__TILE_LOGIC_TABLES;
            index_of__tile_logic_table++) {
        Tile_Logic_Table *p_tile_logic_table =
            get_p_tile_logic_table_by__index_from__tile_logic_table_manager(
                    p_tile_logic_table_manager, 
                    index_of__tile_logic_table);

        if (!p_tile_logic_table->p_tile_logic_records
                || !p_tile_logic_table->m_get_tile_logic_record) {
            return;
        }

        p_tile_logic_table->m_get_tile_logic_record(
                p_tile_logic_table,
                p_tile_logic_record,
                p_tile);
    }
}
