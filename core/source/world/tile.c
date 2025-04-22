#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "world/chunk.h"
#include "world/world.h"
#include <world/tile.h>
#include <defines.h>
#include <vectors.h>

Index__u16 get_tile_sheet_index_offset_for__cover_from__wall_adjacency(
        Tile_Wall_Adjacency_Code__u16 wall_adjacency) {
    return 
        TILE_SHEET_TILE_WIDTH
        * (4
        * (1 + (wall_adjacency & TILE_RENDER__WALL_ADJACENCY__COVER_MASK))
        - 1)
        ;
}

