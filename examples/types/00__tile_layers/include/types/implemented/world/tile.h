#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"
#include "types/implemented/world/tile_kind.h"
#include "types/implemented/world/tile_layer.h"

// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

#define DEFINE_TILE

// TUTORIAL NOTE: __Tile_Data_t is a vestige; the real fields are
// declared by the DECLARE_TILE_LAYER calls below. Each
// DECLARE_TILE_LAYER is one RENDERABLE TILE LAYER (one bitfield of
// the union == one result slot of the tile render kernel == one
// graphics window in the render hierarchy).
typedef struct __Tile_Data_t {
    Tile_Kind;
} __Tile_Data;

typedef struct Tile_t {
    // GEN-BEGIN
    union {
        struct {
            // GEN-RENDER-BEGIN
            // ***) Layer 0: the "ground" layer (8 bits).
            DECLARE_TILE_LAYER(
                    Tile_Kind, 
                    8, 
                    the_kind_of__tile,
                    Tile_Layer__Default,
                    Tile_Layer__Default__Is_Passable,
                    Tile_Layer__Default__Sight_Blocking,
                    Tile_Layer__Default__Height,
                    Tile_Layer__Default__Is_With_Ground);
            // ***) Layer 1: a second "cover" layer (8 bits). This
            // is the whole point of this example: with TWO layers
            // declared here, the tile render kernel receives TWO
            // result slots per tile, and the render hierarchy can
            // have TWO windows (one per layer).
            DECLARE_TILE_LAYER(
                    Tile_Kind, 
                    8, 
                    the_kind_of__cover,
                    Tile_Layer__Cover,
                    Tile_Layer__Cover__Is_Passable,
                    Tile_Layer__Cover__Sight_Blocking,
                    Tile_Layer__Cover__Height,
                    Tile_Layer__Cover__Is_With_Ground);
            // GEN-RENDER-END
        };
        __Tile_Data;
        u8 array_of__tile_data__u8[sizeof(__Tile_Data)];
    };
    // GEN-END
} Tile;

#endif
