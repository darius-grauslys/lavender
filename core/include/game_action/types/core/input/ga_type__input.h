#if !defined(GA_TYPE__INPUT_H) || defined(INJECTION_ACTIVE)

#ifndef INJECTION_ACTIVE
#define GA_TYPE__INPUT_H
#endif
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
    return &((GA_Input__Payload *)(((u8 *)p_game_action) +
                                sizeof(_Game_Action_Header)))
             ->input;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
