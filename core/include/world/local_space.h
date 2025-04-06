#ifndef LOCAL_SPACE_H
#define LOCAL_SPACE_H

#include "defines.h"
#include "world/global_space.h"

void initialize_local_space(
        Local_Space *p_local_space);

static inline
void set_neighbors_of__local_space(
        Local_Space *p_local_space,
        Local_Space *p_local_space__north,
        Local_Space *p_local_space__east,
        Local_Space *p_local_space__south,
        Local_Space *p_local_space__west) {
    p_local_space->p_local_space__north = p_local_space__north;
    p_local_space->p_local_space__east = p_local_space__east;
    p_local_space->p_local_space__south = p_local_space__south;
    p_local_space->p_local_space__west = p_local_space__west;
}

static inline
Global_Space *get_p_global_space_from__local_space(
        Local_Space *p_local_space) {
    return (p_local_space) 
        ? p_local_space->p_global_space
        : 0
        ;
}

static inline
bool is_local_space__allocated(Local_Space *p_local_space) {
    return 
        p_local_space
        && get_p_global_space_from__local_space(p_local_space)
        && is_global_space__allocated(
            get_p_global_space_from__local_space(p_local_space));
}

static inline
bool is_local_space__active(Local_Space *p_local_space) {
    return is_local_space__allocated(
            p_local_space)
        && is_global_space__active(
                get_p_global_space_from__local_space(p_local_space));
}

static inline
Chunk *get_p_chunk_from__local_space(
        Local_Space *p_local_space) {
    if (!p_local_space)
        return 0;
    if (!p_local_space->p_global_space)
        return 0;
    return p_local_space->p_global_space->p_chunk;
}

#endif
