#ifndef GA_TYPES__WORLD_H
#define GA_TYPES__WORLD_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_World){

#define INJECTION_ACTIVE

#include "game_action/types/core/world/load/ga_types__world__load.h"

#undef INJECTION_ACTIVE

} GA_World;

#undef GA_TYPE_CONTEXT
#endif
