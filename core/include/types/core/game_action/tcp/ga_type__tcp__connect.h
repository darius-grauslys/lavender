#if !defined(GA_TYPE__TCP__CONNECT_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__TCP__CONNECT_H
#endif
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_TCP_Connect){
    Identifier__u64 session_token__uuid_u64;
} GA_TCP_Connect;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__TCP__CONNECT_IMPL_H
#define GA_TYPE__TCP__CONNECT_IMPL_H

static inline
Identifier__u64 get_session_token_uuid_64_from__ga_tcp_connect(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action,
            GA_TCP_Connect)
        ->session_token__uuid_u64
        ;
}

static inline
Identifier__u64 *get_p_session_token_uuid_64_from__ga_tcp_connect(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action,
            GA_TCP_Connect)
        ->session_token__uuid_u64
        ;
}


#endif // Impl Header guard
#endif // INJECTION_ACTIVE
