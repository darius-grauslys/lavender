#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F4_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F4_H

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__Acc_I16F4){
    Vector__3i16F4 acceleration__3i16F4;
} GA_AABB__Update__Acc_I16F4;

#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F4_IMPL_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F4_IMPL_H

static inline
Vector__3i16F4 get_acceleration_3i16F4_from__ga_aabb__update__acc_i16F4(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__Acc_I16F4
        .acceleration__3i16F4
        ;
}

static inline
Vector__3i16F4 *get_p_acceleration_3i16F4_from__ga_aabb__update__acc_i16F4(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Collisions
        .GA_AABB
        .GA_AABB__Update__Acc_I16F4
        .acceleration__3i16F4
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
