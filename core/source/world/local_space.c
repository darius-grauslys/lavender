#include "defines.h"
#include "world/local_space.h"

void initialize_local_space(
        Local_Space *p_local_space) {
    memset(p_local_space,
            0,
            sizeof(Local_Space));
}
