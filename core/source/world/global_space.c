#include "world/global_space.h"
#include "defines.h"

void initialize_global_space(
        Global_Space *p_global_space) {
    memset(p_global_space,
            0,
            sizeof(Global_Space));
}

