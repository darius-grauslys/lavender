#ifndef GA_TYPES__WORLD__LOAD_H
#define GA_TYPES__WORLD__LOAD_H
#define GA_TYPE_CONTEXT

#include <defines.h>

#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_World_Load){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__WORLD__LOAD
#endif

#include "game_action/types/core/world/load/ga_type__world__load__client.h"

#ifdef INJECTION_ACTIVE__WORLD__LOAD
#undef INJECTION_ACTIVE
#endif

} GA_World_Load;

#undef GA_TYPE_CONTEXT
#endif
