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

#endif
