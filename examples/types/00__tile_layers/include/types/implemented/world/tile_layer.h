#ifndef IMPL_TILE_LAYER_H
#define IMPL_TILE_LAYER_H

#define DEFINE_TILE_LAYER

typedef enum Tile_Layer {
    // GEN-BEGIN
    // GEN-END
    Tile_Layer__Default = 0,
    Tile_Layer__Default__Sight_Blocking = 
        Tile_Layer__Default,
    Tile_Layer__Default__Is_Passable = 
        Tile_Layer__Default,
    Tile_Layer__Default__Is_With_Ground =
        Tile_Layer__Default,
    Tile_Layer__Default__Height =
        Tile_Layer__Default,
    // ***) A SECOND tile layer. Each layer declared in tile.h
    // needs its entry (and flag aliases) here. Note the count of
    // layers (Tile_Layer__Unknown) sizes engine-side arrays such
    // as the chunk compositor's per-layer texture array.
    Tile_Layer__Cover,
    Tile_Layer__Cover__Sight_Blocking = 
        Tile_Layer__Cover,
    Tile_Layer__Cover__Is_Passable = 
        Tile_Layer__Cover,
    Tile_Layer__Cover__Is_With_Ground =
        Tile_Layer__Cover,
    Tile_Layer__Cover__Height =
        Tile_Layer__Cover,
    Tile_Layer__Unknown
} Tile_Layer;

#endif
