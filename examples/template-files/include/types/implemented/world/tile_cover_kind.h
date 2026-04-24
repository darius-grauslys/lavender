#ifndef IMPL_TILE_COVER_KIND_H
#define IMPL_TILE_COVER_KIND_H

#define DEFINE_TILE_COVER_KIND

typedef enum Tile_Cover_Kind {
    Tile_Kind__None = 0,
    // GEN-LOGIC-BEGIN
    Tile_Cover_Kind__Door__Horizontal,
    Tile_Cover_Kind__Door__Vertical,
    Tile_Cover_Kind__Door__Horizontal__Open,
    Tile_Cover_Kind__Door__Vertical__Open,
    Tile_Cover_Kind__Wall__Corner__North_West,
    Tile_Cover_Kind__Wall__Corner__North,
    Tile_Cover_Kind__Wall__Corner__North_East,
    Tile_Cover_Kind__Wall__Corner__East,
    Tile_Cover_Kind__Wall__Corner__South_East,
    Tile_Cover_Kind__Wall__Corner__South,
    Tile_Cover_Kind__Wall__Corner__South_West,
    Tile_Cover_Kind__Wall__Corner__West,
    // GEN-LOGIC-END
    Tile_Kind__Logical = Tile_Cover_Kind__Wall__Corner__West,

    // GEN-NO-LOGIC-BEGIN
    Tile_Cover_Kind__Plant__Grass,
    Tile_Cover_Kind__Flower__Red,
    Tile_Cover_Kind__Flower__Blue,
    Tile_Cover_Kind__Flower__Yellow,
    // GEN-NO-LOGIC-END
    Tile_Kind__Unknown
} Tile_Cover_Kind;

#endif
