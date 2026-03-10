#ifndef HITBOX_H
#define HITBOX_H

#include "defines.h"
static inline
bool is_hitbox_flags__dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8
        & HITBOX_FLAG__IS_DIRTY
        ;
}

static inline
bool set_hitbox_flags_as__dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 |=
        HITBOX_FLAG__IS_DIRTY
        ;
}

static inline
bool set_hitbox_flags_as__not_dirty(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 &=
        ~HITBOX_FLAG__IS_DIRTY
        ;
}

static inline
bool is_hitbox_flags__active(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8
        & HITBOX_FLAG__IS_ACTIVE
        ;
}

static inline
bool set_hitbox_flags_as__active(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 |=
        HITBOX_FLAG__IS_ACTIVE
        ;
}

static inline
bool set_hitbox_flags_as__disabled(Hitbox_Flags__u8 *p_hitbox_flags__u8) {
    return *p_hitbox_flags__u8 &=
        ~HITBOX_FLAG__IS_ACTIVE
        ;
}

#endif
