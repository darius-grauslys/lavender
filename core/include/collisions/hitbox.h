#ifndef HITBOX_H
#define HITBOX_H

#include "defines.h"

void f_object_handler__hitbox__activate(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32);
void f_object_handler__hitbox__deactivate(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32);
void f_object_handler__hitbox__pre_teleport(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32);
void f_object_handler__hitbox__post_teleport(
        Game *p_game,
        Identifier__u32 uuid_of__object__u32);

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
