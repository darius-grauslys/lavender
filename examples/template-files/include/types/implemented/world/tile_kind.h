#ifndef IMPL_TILE_KIND_H
#define IMPL_TILE_KIND_H

#define DEFINE_TILE_KIND

typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    Tile_Kind__Teleport_Tile,
    Tile_Kind__Heal_Tile,
    Tile_Kind__Power_Up_Tile,
    Tile_Kind__Lava,
    Tile_Kind__Water,
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Kind__Water,

    // GEN-NO-LOGIC-BEGIN
    Tile_Kind__Grass,
    Tile_Kind__Stone,
    Tile_Kind__Wood,
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Kind;

#endif
