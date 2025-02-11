#ifndef GLOBAL_SPACE_MANAGER_H
#define GLOBAL_SPACE_MANAGER_H

#include "defines.h"
#include "defines_weak.h"

void initialize_global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        m_Process m_process__construct_global_space,
        m_Process m_process__destruct_global_space);

Global_Space *allocate_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32);

void release_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Global_Space *p_global_space);

Global_Space *hold_global_space_within__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Chunk_Vector__3i32 local_space_vector__3i32);

void drop_global_space_within__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Global_Space *p_global_space);

#endif
