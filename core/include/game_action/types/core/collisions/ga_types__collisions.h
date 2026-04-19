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
#endif
