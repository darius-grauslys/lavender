#ifndef IMPL_TILE_H
#define IMPL_TILE_H

#include "defines_weak.h"

#define DEFINE_TILE

typedef struct Tile_t {
    // GEN-BEGIN
    union {
        struct {
            Tile_Kind the_kind_of__tile;
        };
        struct {
        };
        u8 array_of__tile_data__u8[1];
    };
    // GEN-END
} Tile;

#endif
