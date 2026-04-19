#ifndef GA_TYPES__WORLD__LOAD_H
#define GA_TYPES__WORLD__LOAD_H
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_World_Load){

#define INJECTION_ACTIVE

#include "game_action/types/core/world/load/ga_type__world__load__client.h"

#undef INJECTION_ACTIVE

} GA_World_Load;

#undef GA_TYPE_CONTEXT
#endif
