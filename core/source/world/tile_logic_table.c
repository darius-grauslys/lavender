#include "world/tile_logic_table.h"
#include "defines.h"
#include "defines_weak.h"
#include "world/tile.h"

void initialize_tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table) {
    memset(
            p_tile_logic_table,
            0,
            sizeof(Tile_Logic_Table));
}

bool allocate_tile_logic_records_in__tile_logic_table(
        Tile_Logic_Table *p_tile_logic_table,
        Quantity__u16 quantity_of__tile_logic_records__u16) {
    if (0 == quantity_of__tile_logic_records__u16) {
        debug_error("allocate_tile_logic_records_in__tile_logic_table, quantity_of__tile_logic_records__u16 == 0.");
        return false;
    }

    p_tile_logic_table->pM_tile_logic_records =
        malloc(sizeof(Tile_Logic_Record) * quantity_of__tile_logic_records__u16);

    return (bool)p_tile_logic_table->pM_tile_logic_records;
}
