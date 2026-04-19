#ifndef GA_TYPES__WORLD_H
#define GA_TYPES__WORLD_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_World){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__WORLD
#endif

#include "game_action/types/core/world/load/ga_types__world__load.h"

#ifdef INJECTION_ACTIVE__WORLD
#undef INJECTION_ACTIVE
#endif

} GA_World;

#undef GA_TYPE_CONTEXT
#endif
