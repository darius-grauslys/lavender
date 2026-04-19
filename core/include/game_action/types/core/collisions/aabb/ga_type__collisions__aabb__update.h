#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE_H

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update){
    uint32_t error_code__u32;
} GA_AABB__Update;

#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE_IMPL_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE_IMPL_H

static inline
uint32_t get_error_code_u32_from__ga_aabb__update(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update
        .error_code__u32
        ;
}

static inline
uint32_t *get_p_error_code_u32_from__ga_aabb__update(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update
        .error_code__u32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
