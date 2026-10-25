#include "world/implemented/tile_logic_table_registrar.h"
#include "world/tile_logic_context.h"
#include "world/tile_logic_table.h"
#include "defines_weak.h"
#include "types/implemented/world/tile_layer.h"

// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

void register_tile_logic_tables(
        Game *p_game,
        Tile_Logic_Context *p_tile_logic_context) {
    // GEN-TABLES-BEGIN
    // ***) Allocate the Default-layer tile logic table. The
    // second argument is the number of tile logic records to
    // make room for (one per tile kind, up to and including
    // Tile_Kind__Unknown).
    Tile_Logic_Table *p_tile_logic_table__default =
        allocate_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context,
                Tile_Layer__Default,
                Tile_Kind__Unknown);

    // ***) initialize zeroes the table header, and this
    // allocates the record array itself. Without these two
    // calls the table has NO records, so every tile kind
    // looks up nothing and every tile is treated as
    // without-ground / non-collidable.
    initialize_tile_logic_table(p_tile_logic_table__default);
    allocate_tile_logic_table__tile_logic_entries(
            p_tile_logic_table__default,
            Tile_Kind__Unknown);
    // GEN-TABLES-END

    // GEN-RECORDS-BEGIN
    // ***) Tile logic records, one per tile kind. The record
    // is zeroed by the allocation above: zero flags means
    // WITH ground, passable, height 0 — which is exactly what
    // our checkerboard ground tiles (RED and GREEN) need, so
    // they are left as-is. The collision resolver's falling
    // ray-cast finds the first tile with ground below the
    // hitbox and lands it there; without these ground records
    // the ray-cast never hits and the client's hitbox falls
    // straight through the world.
    //
    // Tile_Kind__None is transparent/empty: mark it explicitly
    // as without-ground (the engine also treats None as
    // without-ground by convention).
    p_tile_logic_table__default->pM_tile_logic_records[Tile_Kind__None]
        .tile_logic_flags__u8 = TILE_LOGIC_FLAG__IS_WITHOUT_GROUND;
    // GEN-RECORDS-END
}
