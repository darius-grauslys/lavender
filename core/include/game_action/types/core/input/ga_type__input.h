#ifndef GA_TYPE__INPUT_H
#define GA_TYPE__INPUT_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_Input__Payload){
    Input input;
} GA_Input__Payload;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__INPUT_IMPL_H
#define GA_TYPE__INPUT_IMPL_H

static inline
Input *get_p_input_from__game_action(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Input
        .GA_Input__Payload
        .input
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
