#ifndef LOCAL_SPACE_MANAGER_H
#define LOCAL_SPACE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "vectors.h"

void initialize_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Global_Space_Vector__3i32 center_of__local_space_manager__3i32);

void set_center_of__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Chunk_Vector__3i32 chunk_vector__3i32);

void move_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Direction__u8 direction__u8);

Local_Space *get_p_local_space_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4);

Tile *get_p_tile_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4);

void poll_local_space_for__scrolling(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Global_Space_Manager *p_global_space_manager,
        Global_Space_Vector__3i32 global_space_vector__center__3i32);

bool is_vector_3i32F4_within__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector_3i32F4);

static inline
void load_local_space_manager_at__global_space_vector__3i32(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Global_Space_Vector__3i32 global_space_vector__3i32) {
    p_local_space_manager->center_of__local_space_manager__3i32 =
        VECTOR__3i32__OUT_OF_BOUNDS;
    set_center_of__local_space_manager(
            p_local_space_manager, 
            p_game, 
            global_space_vector__3i32);
}

static inline
Chunk_Vector__3i32 get_center_of__local_space_manager(
        Local_Space_Manager *p_local_space_manager) {
    return p_local_space_manager->center_of__local_space_manager__3i32;
}

#endif
