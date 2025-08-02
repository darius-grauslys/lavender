#ifndef IMPL_TILE_LOGIC_RECORD_DATA_H
#define IMPL_TILE_LOGIC_RECORD_DATA_H

#include "defines_weak.h"

#define DEFINE_TILE_LOGIC_TABLE_DATA

typedef struct Tile_Logic_Table_Data_t {
    Tile_Logic_Record tile_logic_record__tile_kind[
        Tile_Kind__Unknown];
} Tile_Logic_Table_Data;

#endif
