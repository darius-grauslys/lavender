#ifndef TILE_LOGIC_CONTEXT_H
#define TILE_LOGIC_CONTEXT_H

#include "defines.h"
#include "defines_weak.h"
#include "types/implemented/world/tile_layer.h"
#include "world/tile.h"
#include "world/tile_logic_table.h"
#include "world/tile_logic_record.h"

void initialize_tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context);

Tile_Logic_Table *allocate_tile_logic_table_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_tile_layer_to__allocate,
        Quantity__u16 quantity_of__tiles_to__keep_logic_records_of__u16);

void release_tile_logic_table_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_tile_layer_to__release);

static inline
Tile_Logic_Table *get_p_tile_logic_table_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_tile_layer_to__get) {
#ifndef NDEBUG
    if (Tile_Layer__Unknown <= the_tile_layer_to__get) {
        debug_error("get_tile_logic_table_from__tile_logic_context, invalid tile layer type.");
        return 0;
    }
#endif

    return p_tile_logic_context->array_of__pM_tile_logic_tables[
        the_tile_layer_to__get];
}

static inline
Tile_Logic_Record *get_p_tile_logic_record_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_kind_of__tile_layer,
        Index__u8 index_of__tile_logic_record__u8) {
#ifndef NDEBUG
    if (!p_tile_logic_context) {
        debug_error("get_p_tile_logic_record_from__tile_logic_context, p_tile_logic_context == 0.");
        return 0;
    }
    if (Tile_Layer__Unknown <= the_kind_of__tile_layer) {
        debug_error("get_p_tile_logic_record_from__tile_logic_context, invalid tiletype provided.");
        return 0;
    }
#endif
    Tile_Logic_Table *p_tile_logic_table =
        get_p_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                the_kind_of__tile_layer);
    return get_p_tile_logic_record_from__tile_logic_table(
            p_tile_logic_table, 
            index_of__tile_logic_record__u8);
}

static inline
bool poll__is_tile__unpassable(
        Tile_Logic_Context *p_tile_logic_context,
        Tile *p_tile) {
    Tile_Logic_Record *p_tile_logic_record =
        get_p_tile_logic_record_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default__Is_Passable,
                get_tile_kind_from__tile(p_tile));
    return is_tile_logic_record__unpassable(p_tile_logic_record);
}

static inline
bool poll__is_tile__sight_blocking(
        Tile_Logic_Context *p_tile_logic_context,
        Tile *p_tile) {
    Tile_Logic_Record *p_tile_logic_record =
        get_p_tile_logic_record_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default__Sight_Blocking,
                get_tile_kind_from__tile(p_tile));
    return is_tile_logic_record__sight_blocking(p_tile_logic_record);
}

static inline
bool poll__is_tile__without_ground(
        Tile_Logic_Context *p_tile_logic_context,
        Tile *p_tile) {
    Tile_Logic_Record *p_tile_logic_record =
        get_p_tile_logic_record_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default__Is_With_Ground,
                get_tile_kind_from__tile(p_tile));
    return is_tile_logic_record__without_ground(p_tile_logic_context);
}

static inline
i32F4 poll__tile_height(
        Tile_Logic_Context *p_tile_logic_context,
        Tile *p_tile) {
    Tile_Logic_Record *p_tile_logic_record =
        get_p_tile_logic_record_from__tile_logic_context(
                p_tile_logic_context, 
                Tile_Layer__Default__Height,
                get_tile_kind_from__tile(p_tile));
    return p_tile_logic_record->tile_height__i32F4;
}

#endif
