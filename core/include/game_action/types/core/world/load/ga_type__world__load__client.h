#if !defined(GA_TYPE__WORLD__LOAD__CLIENT_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__WORLD__LOAD__CLIENT_H
#endif
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_World_Load__Client){
    Identifier__u32 uuid_of__client__u32;
} GA_World_Load__Client;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__WORLD__LOAD__CLIENT_IMPL_H
#define GA_TYPE__WORLD__LOAD__CLIENT_IMPL_H

static inline
Identifier__u32 get_uuid_u32_of__client_from__ga_world_load(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_World_Load__Client)
        ->uuid_of__client__u32
        ;
}

static inline
Identifier__u32 *get_p_uuid_u32_of__client_from__ga_world_load(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_World_Load__Client)
        ->uuid_of__client__u32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
