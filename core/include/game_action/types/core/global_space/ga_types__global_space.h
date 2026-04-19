#ifndef GA_TYPES__GLOBAL_SPACE_H
#define GA_TYPES__GLOBAL_SPACE_H
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Global_Space){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__GLOBAL_SPACE
#endif

#include "game_action/types/core/global_space/ga_type__global_space__request.h"
#include "game_action/types/core/global_space/ga_type__global_space__resolve.h"
#include "game_action/types/core/global_space/ga_type__global_space__store.h"

#ifdef INJECTION_ACTIVE__GLOBAL_SPACE
#undef INJECTION_ACTIVE
#endif

} GA_Global_Space;

#undef GA_TYPE_CONTEXT
#endif
