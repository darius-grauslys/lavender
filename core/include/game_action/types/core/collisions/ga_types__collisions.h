#ifndef GA_TYPES__COLLISIONS_H
#define GA_TYPES__COLLISIONS_H
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Collisions){

#define INJECTION_ACTIVE
    struct {
        Identifier__u32 uuid_of__target; 
        union {
#include "game_action/types/core/collisions/aabb/ga_types__aabb.h"
        };
    };

#undef INJECTION_ACTIVE

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

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
