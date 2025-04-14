#include "world/region.h"
#include "defines.h"
#include "defines_weak.h"
#include "util/bitmap/bitmap.h"
#include "vectors.h"

bool is_tile_position_within__region(
        Tile_Vector__3i32 tile_position__3i32,
        Region_Vector__3i32 region_position__3i32) {
    return
        tile_position__3i32.x__i32
        >> REGION__WIDTH__BIT_SHIFT
        == region_position__3i32.x__i32
        && tile_position__3i32.y__i32
        >> REGION__WIDTH__BIT_SHIFT
        == region_position__3i32.y__i32
        ;
}

bool is_structure_within__region(
        Structure *p_structure,
        Region_Vector__3i32 region_position__3i32) {
    debug_abort("is_structure_within__region, not impl");
    return false;
}

Region_Vector__3i32 get_region_that__this_global_space_is_in(
        Global_Space *p_global_space) {
    return get_vector__3i32(
            p_global_space->chunk_vector__3i32.x__i32 
            >> REGION__WIDTH__BIT_SHIFT, 
            p_global_space->chunk_vector__3i32.y__i32 
            >> REGION__HEIGHT__BIT_SHIFT, 
            0);
}

bool is_chunk_serialized_in__region(
        Region *p_region,
        Chunk_Vector__3i32 chunk_vector__3i32) {
    i32 x__clamped =
        (chunk_vector__3i32.x__i32 < 0)
        ? REGION__WIDTH_IN__CHUNKS
            - ((-chunk_vector__3i32.x__i32)
                    & MASK(REGION__WIDTH__BIT_SHIFT))
        : (-chunk_vector__3i32.x__i32)
                & MASK(REGION__WIDTH__BIT_SHIFT)
        ;
    i32 y__clamped =
        (chunk_vector__3i32.y__i32 < 0)
        ? REGION__HEIGHT_IN__CHUNKS
            - ((-chunk_vector__3i32.y__i32)
                    & MASK(REGION__HEIGHT__BIT_SHIFT))
        : (-chunk_vector__3i32.y__i32)
                & MASK(REGION__HEIGHT__BIT_SHIFT)
        ;

    return is_bit_set_in__bitmap(
            p_region
            ->bitmap_of__serialized_chunks, 
            sizeof(p_region->bitmap_of__serialized_chunks), 
            x__clamped 
            + y__clamped
            * REGION__WIDTH_IN__CHUNKS);
}
