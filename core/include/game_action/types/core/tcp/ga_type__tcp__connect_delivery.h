#if !defined(GA_TYPE__TCP__CONNECT_DELIVERY_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__TCP__CONNECT_DELIVERY_H
#endif
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_TCP_Connect__Delivery){
    u8 payload[
        GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES];
    Quantity__u16 packet_index;
} GA_TCP_Connect__Delivery;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__TCP__CONNECT_DELIVERY_IMPL_H

static inline
u8 *get_p_payload_u8_from__ga_tcp_connect__delivery(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_TCP_Connect__Delivery)
        ->payload
        ;
}

static inline
u16 get_packet_index_u16_from__ga_tcp_connect__delivery(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_TCP_Connect__Delivery)
        ->packet_index
        ;
}

static inline
u16 *get_p_packet_index_u16_from__ga_tcp_connect__delivery(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_TCP_Connect__Delivery)
        ->packet_index
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
