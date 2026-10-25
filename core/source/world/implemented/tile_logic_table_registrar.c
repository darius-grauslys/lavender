#include "world/implemented/tile_logic_table_registrar.h"
#include "types/implemented/world/tile_kind.h"
#include "world/tile_logic_context.h"
#include "defines_weak.h"
#include "types/implemented/world/tile_layer.h"

// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

void register_tile_logic_tables(
        Game *p_game,
        Tile_Logic_Context *p_tile_logic_context) {
    // GEN-TABLES-BEGIN
    allocate_tile_logic_table_from__tile_logic_context(
            p_tile_logic_context, 
            Tile_Layer__Default, 
            Tile_Kind__Unknown);
    // GEN-TABLES-END
    
    // GEN-RECORDS-BEGIN
    // GEN-RECORDS-END
}
