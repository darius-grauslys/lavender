#ifndef REGION
#define REGION

#include "defines_weak.h"
#include "platform_defaults.h"
#include <defines.h>

bool is_tile_position_within__region(
        Tile_Vector__3i32 tile_position__3i32,
        Region_Vector__3i32 region_position__3i32);

bool is_structure_within__region(
        Structure *p_structure,
        Region_Vector__3i32 region_position__3i32);

Region_Vector__3i32 get_region_that__this_global_space_is_in(
        Global_Space *p_global_space);

void m_process__serialize_region(
        Process *p_this_process,
        Game *p_game);

void m_process__deserialize_region(
        Process *p_this_process,
        Game *p_game);

static inline
void truncate_p_chunk_vector_3i32_to__region(
        Chunk_Vector__3i32 *p_chunk_vector__3i32) {
    p_chunk_vector__3i32->x__i32 &=
        MASK(REGION__WIDTH__BIT_SHIFT)
        >> CHUNK__WIDTH__AND_HEIGHT__BIT_SHIFT;
    p_chunk_vector__3i32->y__i32 &=
        MASK(REGION__HEIGHT__BIT_SHIFT)
        >> CHUNK__WIDTH__AND_HEIGHT__BIT_SHIFT;
    // TODO: Z-axis
}

#endif
