#ifndef GA_TYPES__ENTITY_H
#define GA_TYPES__ENTITY_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Entity){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE__ENTITY
#define INJECTION_ACTIVE
#endif

#include "game_action/types/core/entity/ga_type__entity__payload.h"

#ifdef INJECTION_ACTIVE__ENTITY
#undef INJECTION_ACTIVE__ENTITY
#undef INJECTION_ACTIVE
#endif

} GA_Entity;

#undef GA_TYPE_CONTEXT
#endif
