#ifndef REGION_FILE_H
#define REGION_FILE_H

#include "defines.h"

///
/// Warning this function does blocking filesystem IO.
///
bool is_region_in__directory(
        World *p_world,
        Region_Vector__3i32 region_vector__3i32);

#endif
