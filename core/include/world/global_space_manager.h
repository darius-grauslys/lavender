#ifndef GLOBAL_SPACE_MANAGER_H
#define GLOBAL_SPACE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_global_space_manager(
        Global_Space_Manager *p_global_space_manager);

Global_Space *allocate_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32);

void release_global_space(
        World *p_world,
        Global_Space *p_global_space);

void release_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Global_Space *p_global_space);

Global_Space *get_p_global_space_from__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 local_space_vector__3i32);

Tile *get_p_tile_from__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Tile_Vector__3i32 tile_vector__3i32);

Global_Space *hold_global_space_within__global_space_manager(
        Game *p_game,
        Chunk_Vector__3i32 local_space_vector__3i32);

void drop_global_space_within__global_space_manager(
        Game *p_game,
        Chunk_Vector__3i32 local_space_vector__3i32);

#define BIT_MASK__GLOBAL_SPACE__0_XY__u24 0b101010101010101010101010
#define BIT_MASK__GLOBAL_SPACE__1_XY__u24 0b010101010101010101010101

#define BIT_MASK__GLOBAL_SPACE__0_Z__u8 MASK(8)
#define BIT_MASK__GLOBAL_SPACE__1_Z__u8 (MASK(8) << 7)


static inline
Identifier__u64 get_uuid_for__global_space(
        Chunk_Vector__3i32 chunk_vector__3i32) {
    return
            (uint64_t)((BIT_MASK__GLOBAL_SPACE__0_XY__u24 & chunk_vector__3i32.x__i32)
                    | (BIT_MASK__GLOBAL_SPACE__1_XY__u24 & chunk_vector__3i32.y__i32))
            | (((uint64_t)(BIT_MASK__GLOBAL_SPACE__1_XY__u24 & chunk_vector__3i32.x__i32)
                    | (BIT_MASK__GLOBAL_SPACE__0_XY__u24 & chunk_vector__3i32.y__i32)) << 32)
            | ((uint64_t)(BIT_MASK__GLOBAL_SPACE__0_Z__u8 & chunk_vector__3i32.z__i32) << 24)
            | ((uint64_t)(BIT_MASK__GLOBAL_SPACE__1_Z__u8 & chunk_vector__3i32.z__i32) << 56)
            ;
}


#endif
