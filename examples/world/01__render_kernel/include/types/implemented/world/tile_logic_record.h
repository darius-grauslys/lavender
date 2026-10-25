#ifndef IMPL_TILE_LOGIC_RECORD_H
#define IMPL_TILE_LOGIC_RECORD_H

#define DEFINE_TILE_LOGIC_RECORD

#include "defines_weak.h"

// SIGNATURES-BEGIN
// SIGNATURES-END

typedef struct Tile_Logic_Record_t {
    i32F4                       tile_height__i32F4; // [0 - 1 + (15/16) ]
    Tile_Logic_Flags__u16       tile_logic_flags__u8;

    // FIELDS-BEGIN
    // FIELDS-END
} Tile_Logic_Record;

#endif
