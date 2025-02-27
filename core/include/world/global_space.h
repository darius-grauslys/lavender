#ifndef GLOBAL_SPACE_H
#define GLOBAL_SPACE_H

#include "defines.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"

void initialize_global_space(
        Global_Space *p_global_space);

void initialize_global_space_as__allocated(
        Global_Space *p_global_space,
        Identifier__u64 uuid_64);

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
    return p_global_space
        && !is_serialized_struct__deallocated__uuid_64(
                &p_global_space->_serialization_header)
        && p_global_space->quantity_of__references;
}

static inline
bool is_global_space__constructing(
        Global_Space *p_global_space) {
    return (p_global_space->global_space_flags__u8
        & GLOBAL_SPACE_FLAG__IS_CONSTRUCTING)
        ;
}

static inline
bool set_global_space_as__constructing(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 |=
        GLOBAL_SPACE_FLAG__IS_CONSTRUCTING
        ;
}

static inline
bool set_global_space_as__NOT_constructing(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 &=
        ~GLOBAL_SPACE_FLAG__IS_CONSTRUCTING
        ;
}

static inline
bool is_global_space__deconstructing(
        Global_Space *p_global_space) {
    return (p_global_space->global_space_flags__u8
        & GLOBAL_SPACE_FLAG__IS_DECONSTRUCTING)
        ;
}

static inline
bool set_global_space_as__deconstructing(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 |=
        GLOBAL_SPACE_FLAG__IS_DECONSTRUCTING
        ;
}

static inline
bool set_global_space_as__NOT_deconstructing(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 &=
        ~GLOBAL_SPACE_FLAG__IS_DECONSTRUCTING
        ;
}

static inline
bool is_global_space__dirty(
        Global_Space *p_global_space) {
    return (p_global_space->global_space_flags__u8
        & GLOBAL_SPACE_FLAG__IS_DIRTY)
        ;
}

static inline
bool set_global_space_as__dirty(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 |=
        GLOBAL_SPACE_FLAG__IS_DIRTY
        ;
}

static inline
bool set_global_space_as__NOT_dirty(
        Global_Space *p_global_space) {
    return p_global_space->global_space_flags__u8 &=
        ~GLOBAL_SPACE_FLAG__IS_DIRTY
        ;
}

static inline
bool is_global_space__active(
        Global_Space *p_global_space) {
    return p_global_space
        && !is_global_space__constructing(p_global_space)
        && !is_global_space__deconstructing(p_global_space);
}

static inline
Chunk *get_p_chunk_from__global_space(
        Global_Space *p_global_space) {
    return p_global_space->p_chunk;
}

static inline
Collision_Node *get_p_collision_node_from__global_space(
        Global_Space *p_global_space) {
    return p_global_space->p_collision_node;
}

#endif
