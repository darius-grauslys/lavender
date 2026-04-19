#ifndef GA_TYPE__GLOBAL_SPACE__REQUEST_H
#define GA_TYPE__GLOBAL_SPACE__REQUEST_H
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

// in seconds:
#define GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT 4

LAV_TYPE__BEGIN(GA_Global_Space__Request){
    Global_Space_Vector__3i32 gsv_3i32;
    TCP_PAYLOAD_BITMAP(Chunk, chunk_payload_bitmap);
    Timer__u32 timeout__timer_u32;
} GA_Global_Space__Request;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__GLOBAL_SPACE__REQUEST_IMPL_H
#define GA_TYPE__GLOBAL_SPACE__REQUEST_IMPL_H

#define SIZE_OF__TCP_PAYLOAD_BITMAP__CHUNK \
    (sizeof(((Game_Action*)0)->GA_Global_Space.GA_Global_Space__Request.\
            chunk_payload_bitmap))

static inline
Global_Space_Vector__3i32 get_gsv_3i32_from__ga_global_space__request(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Request
        .gsv_3i32
        ;
}

static inline
Global_Space_Vector__3i32 *get_p_gsv_3i32_from__ga_global_space__request(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Request
        .gsv_3i32
        ;
}

static inline
u8 *get_p_tcp_payload_bitmap_u8_from__ga_global_space__request(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Request
        .chunk_payload_bitmap
        ;
}

static inline
Timer__u32 get_timeout_timer_u32_from__ga_global_space__request(
        Game_Action *p_game_action) {
    return p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Request
        .timeout__timer_u32
        ;
}

static inline
Timer__u32 *get_p_timeout_timer_u32_from__ga_global_space__request(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Request
        .gsv_3i32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
