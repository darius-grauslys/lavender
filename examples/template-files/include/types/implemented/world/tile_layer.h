#ifndef IMPL_TILE_LAYER_H
#define IMPL_TILE_LAYER_H

#define DEFINE_TILE_LAYER

typedef enum Tile_Layer {
    // GEN-BEGIN
    Tile_Layer__Ground,
    Tile_Layer__Cover,
    // GEN-END
    Tile_Layer__Default = Tile_Layer__Ground,
    Tile_Layer__Default__Sight_Blocking = 
        Tile_Layer__Cover,
    Tile_Layer__Default__Is_Passable = 
        Tile_Layer__Cover,
    Tile_Layer__Default__Is_With_Ground =
        Tile_Layer__Ground,
    Tile_Layer__Default__Height =
        Tile_Layer__Ground,
    Tile_Layer__Unknown
} Tile_Layer;

#endif
