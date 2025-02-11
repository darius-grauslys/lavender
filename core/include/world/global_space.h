#ifndef GLOBAL_SPACE_H
#define GLOBAL_SPACE_H

#include "defines.h"

void initialize_global_space(
        Global_Space *p_global_space);

static inline
void initialize_global_space_as__allocated(
        Global_Space *p_global_space) {
    initialize_global_space(p_global_space);
    p_global_space->quantity_of__references = 1;
}

static inline
void hold_global_space(
        Global_Space *p_global_space) {
    p_global_space->quantity_of__references++;
}

///
/// Returns true if all references are dropped.
///
static inline
bool drop_global_space(
        Global_Space *p_global_space) {
    if (p_global_space->quantity_of__references <= 1) {
        p_global_space->quantity_of__references = 1;
        return true;
    }
    p_global_space->quantity_of__references--;
    return false;
}

static inline
bool is_global_space__allocated(
        Global_Space *p_global_space) {
    return p_global_space->quantity_of__references;
}

static inline
bool is_global_space__active(
        Global_Space *p_global_space) {
    return (p_global_space->global_space_flags__u8
        & GLOBAL_SPACE_FLAG__IS_ACTIVE)
        ;
}

static inline
bool set_global_space_as__active(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 |=
        GLOBAL_SPACE_FLAG__IS_ACTIVE
        ;
}

static inline
bool set_global_space_as__inactive(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 &=
        ~GLOBAL_SPACE_FLAG__IS_ACTIVE
        ;
}

#endif
