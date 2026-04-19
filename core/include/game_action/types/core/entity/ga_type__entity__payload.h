#if !defined(GA_TYPE__ENTITY__PAYLOAD_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__ENTITY__PAYLOAD_H
#endif
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_Entity__Payload){
    TCP_PAYLOAD_BITMAP(Entity, tcp_payload_bitmap);
    Identifier__u32 uuid_of__entity__u32;
    Entity_Kind the_kind_of__entity;
} GA_Entity__Payload;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__ENTITY__PAYLOAD_IMPL_H
#define GA_TYPE__ENTITY__PAYLOAD_IMPL_H

#define SIZE_OF__TCP_PAYLOAD_BITMAP__ENTITY \
    (sizeof(((Game_Action*)0)\
            ->_ga_payload_union.GA_Entity.GA_Entity__Payload.tcp_payload_bitmap))

static inline
u8 *get_p_tcp_payload_bitmap__ga_entity__payload(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_Entity__Payload)
        ->tcp_payload_bitmap
        ;
}

static inline
Identifier__u32 get_uuid_u32_of__entity_from__ga_entity__payload(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_Entity__Payload)
        ->uuid_of__entity__u32
        ;
}

static inline
Identifier__u32 *get_p_uuid_u32_of__entity_from__ga_entity__payload(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_Entity__Payload)
        ->uuid_of__entity__u32
        ;
}

static inline
Entity_Kind get_the_kind_of__entity_from__ga_entity__payload(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_Entity__Payload)
        ->the_kind_of__entity
        ;
}

static inline
Entity_Kind *get_p_the_kind_of__entity_from__ga_entity__payload(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action, 
            GA_Entity__Payload)
        ->the_kind_of__entity
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
