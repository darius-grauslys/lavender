#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"

// GEN-INCLUDE-BEGIN
#include "types/implemented/world/tile_cover_kind.h"
// GEN-INCLUDE-END

#define DEFINE_TILE

typedef struct Tile_t {
    union {
        // NOTE: The tile layers are configured to have a:
        // NOTE: 1) Full bit size (10)
        // NOTE: 2) A logic partition (layer0: 4, layer1: 6)
        // NOTE: 3) An animation partition (layer0: 4, layer1: 4)
        struct {
            // NOTE: The full bit fields are exposed in the first struct
            // GEN-RENDER-BEGIN
            Tile_Kind the_kind_of__tile : 10;
            Tile_Cover_Kind tike_kind_of__tile__cover : 10;
            // GEN-RENDER-END
        };
        struct {
            // NOTE: The logic and animation fields are organized to fit
            // NOTE: completely in bytes - no straddling
            // GEN-LAYER-BEGIN
            u8 tile_layer_0__field__logic : 4;
            u8 tile_layer_0__field__animation : 4;

            u8 tile_layer_0__remainder : 2;
            u8 tile_layer_1__field__animation : 4;
            u8 tile_layer_1__remainder : 2;

            u8 tile_layer_1__field__logic : 6;
            u8 : 2;
            // GEN-LAYER-END
        };
        // NOTE: 3 is determinstically automatically generated via scripting.
        u8 array_of__tile_data__u8[3];
    };
    // GEN-END
} Tile;

#endif
