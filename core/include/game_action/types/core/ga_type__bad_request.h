#if !defined(GA_TYPE__BAD_REQUEST_H) \
    || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__BAD_REQUEST_H
#endif
#define GA_TYPE_CONTEXT

#include <util/custom_type_macro.h>

#ifndef DEFINES_H
#include <defines.h>
#endif

LAV_TYPE__BEGIN(GA_Bad_Request){
    uint32_t error_code__u32;
} GA_Bad_Request;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__BAD_REQUEST_IMPL_H
#define GA_TYPE__BAD_REQUEST_IMPL_H

static inline
u32 get_error_code_u32_from__ga_bad_request(
        Game_Action *p_game_action) {
    return GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action,
            GA_Bad_Request)
        ->error_code__u32
        ;
}

static inline
u32 *get_p_error_code_u32_from__ga_bad_request(
        Game_Action *p_game_action) {
    return &GET_P_GAME_ACTION_PAYLOAD_AS_P(
            p_game_action,
            GA_Bad_Request)
        ->error_code__u32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
