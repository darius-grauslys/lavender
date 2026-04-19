#ifndef GA_TYPES__INPUT_H
#define GA_TYPES__INPUT_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Input){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__INPUT
#endif

#include "game_action/types/core/input/ga_type__input.h"

#ifdef INJECTION_ACTIVE__INPUT
#undef INJECTION_ACTIVE__INPUT
#undef INJECTION_ACTIVE
#endif

} GA_Input;

#undef GA_TYPE_CONTEXT
#endif
