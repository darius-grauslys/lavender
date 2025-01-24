#include "defines.h"
#include <world/tile_logic_record.h>

void initialize_tile_logic_record(
        Tile_Logic_Record *p_tile_logic_record,
        f_Tile_Handler__Touch f_tile_handler__touch,
        f_Tile_Handler__Place f_tile_handler__place,
        f_Tile_Handler__Destroy f_tile_handler__destroy,
        Tile_Logic_Flags__u8 tile_logic_flags__u8) {
    p_tile_logic_record
        ->f_tile_handler__touch =
        f_tile_handler__touch;
    p_tile_logic_record
        ->f_tile_handler__place =
        f_tile_handler__place;
    p_tile_logic_record
        ->f_tile_handler__destroy =
        f_tile_handler__destroy;
    p_tile_logic_record
        ->tile_logic_flags__u8 =
        tile_logic_flags__u8;
}
