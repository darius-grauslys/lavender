#include "world/tile_logic_context.h"
#include "defines.h"
#include "world/tile_logic_table.h"

void initialize_tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context) {
    memset(p_tile_logic_context,
            0,
            sizeof(Tile_Logic_Context));
}

Tile_Logic_Table *allocate_tile_logic_table_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_tile_layer_to__allocate,
        Quantity__u16 quantity_of__tiles_to__keep_logic_records_of__u16) {
#ifndef NDEBUG
    if (Tile_Layer__Unknown <= the_tile_layer_to__allocate) {
        debug_error("allocate_tile_logic_table_from__tile_logic_context, invalid tile layer type.");
        return 0;
    }
#endif
    if (0 != p_tile_logic_context->array_of__pM_tile_logic_tables[
            the_tile_layer_to__allocate]) {
        debug_error("allocate_tile_logic_table_from__tile_logic_context, tile_logic_table already present for given type, it must be released first.");
        return 0;
    }

    // Attempt to allocate Tile_Logic_Table
    Tile_Logic_Table *p_tile_logic_table =
        (p_tile_logic_context->array_of__pM_tile_logic_tables[
            the_tile_layer_to__allocate] = malloc(sizeof(Tile_Logic_Table)));

    // Verify attempt
    if (!p_tile_logic_table) {
        debug_error("allocate_tile_logic_table_from__tile_logic_context, failed to allocate Tile_Logic_Table.");
        return 0;
    }

    // Attempt to allocate Tile_Logic_Table's fields
    if (!allocate_tile_logic_table__tile_logic_entries(
            p_tile_logic_table, 
            quantity_of__tiles_to__keep_logic_records_of__u16)) {
        // Attempt failed, remove record from context.
        release_tile_logic_table_from__tile_logic_context(
                p_tile_logic_context, 
                the_tile_layer_to__allocate);
        return 0;
    }

    return p_tile_logic_table;
}

void release_tile_logic_table_from__tile_logic_context(
        Tile_Logic_Context *p_tile_logic_context,
        Tile_Layer the_tile_layer_to__release) {
#ifndef NDEBUG
    if (Tile_Layer__Unknown <= the_tile_layer_to__release) {
        debug_error("release_tile_logic_table_from__tile_logic_context, invalid tile layer type.");
        return;
    }
#endif

    Tile_Logic_Table *p_tile_logic_table =
        p_tile_logic_context->array_of__pM_tile_logic_tables[
        the_tile_layer_to__release];

    if (0 == p_tile_logic_table) {
        debug_error("release_tile_logic_table_from__tile_logic_context, tile_logic_table record already released for given type.");
        return;
    }

    release_tile_logic_table__tile_logic_entries(p_tile_logic_table);

    free(p_tile_logic_context->array_of__pM_tile_logic_tables[
            the_tile_layer_to__release]);

    p_tile_logic_context->array_of__pM_tile_logic_tables[
        the_tile_layer_to__release] = 0;
}
