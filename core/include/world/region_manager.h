#ifndef REGION_MANAGER_H
#define REGION_MANAGER_H

#include "defines.h"

void initialize_region_manager(
        Region_Manager *p_region_manager);

void set_center_of__region_manager(
        Game *p_game,
        Region_Manager *p_region_manager,
        Region_Vector__3i32 region_vector__3i32);

#endif
