#ifndef GA_TYPES__AABB_H
#define GA_TYPES__AABB_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_AABB){

#define INJECTION_ACTIVE

    struct {
        union {
#include "game_action/types/core/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32.h"
#include "game_action/types/core/collisions/aabb/ga_type__collisions__aabb__update__pos_vec_i32F4.h"
        };

        union {
#include "game_action/types/core/collisions/aabb/ga_type__collisions__aabb__update__acc_i16.h"
#include "game_action/types/core/collisions/aabb/ga_type__collisions__aabb__update__acc_i16F4.h"
#include "game_action/types/core/collisions/aabb/ga_type__collisions__aabb__update__acc_i16F8.h"
        };
    };

#undef INJECTION_ACTIVE

} GA_AABB;

#undef GA_TYPE_CONTEXT
#endif
