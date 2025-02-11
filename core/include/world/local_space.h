#ifndef LOCAL_SPACE_H
#define LOCAL_SPACE_H

#include "defines.h"
#include "world/global_space.h"

void initialize_local_space(
        Local_Space *p_local_space);

static inline
Global_Space *get_p_global_space_from__local_space(
        Local_Space *p_local_space) {
    return p_local_space->p_global_space;
}

static inline
bool is_local_space__allocated(Local_Space *p_local_space) {
    return get_p_global_space_from__local_space(p_local_space)
        && is_global_space__allocated(
            p_local_space->p_global_space);
}

static inline
bool is_local_space__active(Local_Space *p_local_space) {
    return is_local_space__allocated(
            p_local_space)
        && is_global_space__active(
                get_p_global_space_from__local_space(p_local_space));
}

#endif
