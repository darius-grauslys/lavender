#ifndef GA_TYPES__AABB_H
#define GA_TYPES__AABB_H
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_AABB){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__COLLISIONS__AABB
#endif

    struct {
        union {
#include "types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32.h"
#include "types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32F4.h"
        };

        union {
#include "types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__acc_i16.h"
#include "types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__acc_i16F4.h"
#include "types/core/game_action/collisions/aabb/ga_type__collisions__aabb__update__acc_i16F8.h"
        };
    };

#ifdef INJECTION_ACTIVE__COLLISIONS__AABB
#undef INJECTION_ACTIVE__COLLISIONS__AABB
#undef INJECTION_ACTIVE
#endif

} GA_AABB;

#undef GA_TYPE_CONTEXT
#endif
