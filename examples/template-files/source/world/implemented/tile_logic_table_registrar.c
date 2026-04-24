#include "world/implemented/tile_logic_table_registrar.h"
#include "defines_weak.h"
#include "world/tile_logic_context.h"
#include "world/tile_logic_table.h"
#include "world/tile_logic_table__default.h"

// See ./examples/template-files/include/types/implemented/world/tile_kind.h
// See ./examples/template-files/include/types/implemented/world/tile_cover_kind.h
// GEN-INCLUDE-BEGIN
#include "world/implemented/tile_logic_table__ground.h"
#include "world/implemented/tile_logic_table__cover.h"
// GEN-INCLUDE-END

void register_tile_logic_tables(
        Game *p_game,
        Tile_Logic_Context *p_tile_logic_context) {
    // GEN-TABLES-BEGIN
    if (!allocate_tile_logic_table__tile_logic_entries(
            allocate_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default, 
                Tile_Kind__Logical),
            Tile_Kind__Logical, 
            sizeof(Tile_Logic_Record__Ground))) {
        debug_error("register_tile_logic_tables, failed to allocate tile_logic_table for Tile_Logic_Record__Ground");
    }
    if (!allocate_tile_logic_table__tile_logic_entries(
            allocate_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default, 
                Tile_Kind__Logical),
            // TODO: in this rework, do we even still use Tile_Kind within CORE?
            // TODO: we probably still do.
            Tile_Cover_Kind__Logical, 
            sizeof(Tile_Logic_Record__Cover))) {
        debug_error("register_tile_logic_tables, failed to allocate tile_logic_table for Tile_Logic_Record__Cover");
    }
    // GEN-TABLES-END
    
    // GEN-RECORDS-BEGIN
    register_tile_logic_table__ground(
            get_p_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Ground));
    register_tile_logic_table__cover(
            get_p_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Cover));
    // GEN-RECORDS-END
}

