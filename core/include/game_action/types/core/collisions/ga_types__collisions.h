#ifndef GA_TYPES__COLLISIONS_H
#define GA_TYPES__COLLISIONS_H
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Collisions){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__COLLISIONS
#endif
    struct {
        Identifier__u32 uuid_of__target; 
        union {
#include "game_action/types/core/collisions/aabb/ga_types__aabb.h"
        };
        Hitbox_Kind the_kind_of__hitbox;;
    };

#ifdef INJECTION_ACTIVE__COLLISIONS
#undef INJECTION_ACTIVE
#endif

} GA_Collisions;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPES__COLLISIONS_IMPL_H
#define GA_TYPES__COLLISIONS_IMPL_H

static inline
Identifier__u32 get_uuid_of__target_from__ga_collisions(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .uuid_of__target
        ;
}

static inline
Identifier__u32 *get_p_uuid_of__target_from__ga_collisions(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .uuid_of__target
        ;
}

static inline
Identifier__u32 get_the_kind_of_hitbox_from__ga_collisions(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .the_kind_of__hitbox
        ;
}

static inline
Identifier__u32 *get_p_the_kind_of_hitbox_from__ga_collisions(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .the_kind_of__hitbox
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
