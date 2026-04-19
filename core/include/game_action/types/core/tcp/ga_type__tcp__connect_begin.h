#ifndef GA_TYPE__TCP__CONNECT_BEGIN_H
#define GA_TYPE__TCP__CONNECT_BEGIN_H
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_TCP_Connect__Begin){
    IPv4_Address ipv4_address;
    Session_Token session_token;
} GA_TCP_Connect__Begin;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__TCP__CONNECT_BEGIN_IMPL_H

static inline
IPv4_Address get_ipv4_address_from__ga_tcp_connect__begin(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_TCP
        .GA_TCP_Connect__Begin
        .ipv4_address
        ;
}

static inline
IPv4_Address *get_p_ipv4_address_from__ga_tcp_connect__begin(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_TCP
        .GA_TCP_Connect__Begin
        .ipv4_address
        ;
}

static inline
Session_Token get_session_token_from__ga_tcp_connect__begin(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_TCP
        .GA_TCP_Connect__Begin
        .session_token
        ;
}

static inline
Session_Token *get_p_session_token_from__ga_tcp_connect__begin(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_TCP
        .GA_TCP_Connect__Begin
        .session_token
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
