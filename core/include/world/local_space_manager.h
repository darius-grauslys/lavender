#ifndef LOCAL_SPACE_MANAGER_H
#define LOCAL_SPACE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Global_Space_Vector__3i32 center_of__local_space_manager__3i32);

void set_center_of__local_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Local_Space_Manager *p_local_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32);

void move_local_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Local_Space_Manager *p_local_space_manager,
        Direction__u8 direction__u8);

Local_Space *get_p_local_space_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4);

Tile *get_p_tile_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4);

#endif
