#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"
#include "types/implemented/world/tile_kind.h"
#include "types/implemented/world/tile_layer.h"

// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

#define DEFINE_TILE

typedef struct __Tile_Data_t {
    Tile_Kind;
} __Tile_Data;

typedef struct Tile_t {
    // GEN-BEGIN
    union {
        struct {
            // GEN-RENDER-BEGIN
            DECLARE_TILE_LAYER(
                    Tile_Kind, 
                    8, 
                    the_kind_of__tile,
                    Tile_Layer__Default,
                    Tile_Layer__Default__Is_Passable,
                    Tile_Layer__Default__Sight_Blocking,
                    Tile_Layer__Default__Height,
                    Tile_Layer__Default__Is_With_Ground);
            // GEN-RENDER-END
        };
        __Tile_Data;
        u8 array_of__tile_data__u8[sizeof(__Tile_Data)];
    };
    // GEN-END
} Tile;

#endif
