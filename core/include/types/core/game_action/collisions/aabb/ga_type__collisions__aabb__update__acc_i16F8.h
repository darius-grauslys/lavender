#if !defined(GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F8_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F8_H
#endif
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__Acc_I16F8){
    Vector__3i16F8 acceleration__3i16F8;
} GA_AABB__Update__Acc_I16F8;

#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F8_IMPL_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__ACC_I16F8_IMPL_H

static inline
Vector__3i16F8 get_acceleration_3i16F8_from__ga_aabb__update__acc_i16F8(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_AABB__Update__Acc_I16F8)
        ->acceleration__3i16F8
        ;
}

static inline
Vector__3i16F8 *get_p_acceleration_3i16F8_from__ga_aabb__update__acc_i16F8(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_AABB__Update__Acc_I16F8)
        ->acceleration__3i16F8
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
