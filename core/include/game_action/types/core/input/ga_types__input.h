#ifndef GA_TYPES__INPUT_H
#define GA_TYPES__INPUT_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Input){

#define INJECTION_ACTIVE

#include "game_action/types/core/input/ga_type__input.h"

#undef INJECTION_ACTIVE

} GA_Input;

#undef GA_TYPE_CONTEXT
#endif
