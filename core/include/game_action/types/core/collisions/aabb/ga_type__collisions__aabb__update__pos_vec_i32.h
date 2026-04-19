#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_H
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__PosVec_I32){
    Vector__3i32 position__3i32;
    Vector__3i32 velocity__3i32;
} GA_AABB__Update__PosVec_I32;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_IMPL_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_IMPL_H

static inline
Vector__3i32 get_position_3i32_from__ga_aabb__update__pos_vec_i32(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32
        .position__3i32
        ;
}

static inline
Vector__3i32 *get_p_position_3i32_from__ga_aabb__update__pos_vec_i32(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32
        .position__3i32
        ;
}

static inline
Vector__3i32 get_velocity_3i32_from__ga_aabb__update__pos_vec_i32(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32
        .velocity__3i32
        ;
}

static inline
Vector__3i32 *get_p_velocity_3i32_from__ga_aabb__update__pos_vec_i32(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__PosVec_I32
        .velocity__3i32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
