#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"
#include "types/implemented/world/tile_kind.h"
#include "types/implemented/world/tile_layer.h"

// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

#define DEFINE_TILE

// TUTORIAL NOTE (2.3 "bitfield size of tile layers"): the second
// argument of DECLARE_TILE_LAYER is the size IN BITS of that layer's
// bitfield. It is the single knob that sets a layer's "logical
// resolution": a layer of N bits can hold 2^N distinct tile values,
// and therefore can address 2^N tilesheet slots.
//
//   stock:  ONE layer x 8 bits  -> 2^8 = 256 values, tile = 1 byte
//   here:   TWO layers x 4 bits -> 2^4 = 16 values each, tile = 1 byte
//
// By halving each layer's bitfield (8 -> 4 bits) we DOUBLE the number
// of layers while keeping sizeof(Tile) at 1 byte (4 + 4 == 8 bits).
// The price is that each layer can now only name 16 tilesheet slots
// (indices 0..15) instead of 256.
typedef struct __Tile_Data_t {
    Tile_Kind;
} __Tile_Data;

typedef struct Tile_t {
    // GEN-BEGIN
    union {
        struct {
            // GEN-RENDER-BEGIN
            // ***) Layer 0: "ground" layer, 4 bits (resolution 16).
            DECLARE_TILE_LAYER(
                    Tile_Kind,
                    4,
                    the_kind_of__tile,
                    Tile_Layer__Default,
                    Tile_Layer__Default__Is_Passable,
                    Tile_Layer__Default__Sight_Blocking,
                    Tile_Layer__Default__Height,
                    Tile_Layer__Default__Is_With_Ground);
            // ***) Layer 1: "cover" layer, ALSO 4 bits (resolution 16).
            // 4 + 4 == 8 bits, so the union is still exactly 1 byte.
            DECLARE_TILE_LAYER(
                    Tile_Kind,
                    4,
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
