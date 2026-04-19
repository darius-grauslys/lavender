#ifndef GA_TYPE__GLOBAL_SPACE__STORE_H
#define GA_TYPE__GLOBAL_SPACE__STORE_H
#define GA_TYPE_CONTEXT

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_Global_Space__Store){
    Global_Space_Vector__3i32 gsv__3i32;
} GA_Global_Space__Store;

#undef GA_TYPE_CONTEXT
#endif // Header guard

#ifndef INJECTION_ACTIVE
#ifndef GA_TYPE__GLOBAL_SPACE__STORE_IMPL_H
#define GA_TYPE__GLOBAL_SPACE__STORE_IMPL_H

static inline
Global_Space_Vector__3i32 *get_p_gsv_3i32_from__ga_global_space__store(
        Game_Action *p_game_action) {
    return &p_game_action
        ->GA_Global_Space
        .GA_Global_Space__Store
        .gsv__3i32
        ;
}

#endif // Impl Header guard
#endif // INJECTION_ACTIVE
