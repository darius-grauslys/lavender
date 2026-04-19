#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_H

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__PosVec_I32F4){
    Vector__3i32F4 position__3i32F4;
    Vector__3i32F4 velocity__3i32F4;
} GA_AABB__Update__PosVec_I32F4;

#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_IMPL_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_IMPL_H

static inline
Vector__3i32F4 get_position_3i32F4_from__ga_aabb__update__pos_vec_i32F4(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32F4
        .position__3i32F4
        ;
}

static inline
Vector__3i32F4 *get_p_position_3i32F4_from__ga_aabb__update__pos_vec_i32F4(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32F4
        .position__3i32F4
        ;
}

static inline
Vector__3i32F4 get_velocity_3i32F4_from__ga_aabb__update__pos_vec_i32F4(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32F4
        .velocity__3i32F4
        ;
}

static inline
Vector__3i32F4 *get_p_velocity_3i32F4_from__ga_aabb__update__pos_vec_i32F4(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32F4
        .velocity__3i32F4
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
