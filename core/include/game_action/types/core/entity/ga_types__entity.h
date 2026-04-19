#ifndef GA_TYPES__ENTITY_H
#define GA_TYPES__ENTITY_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_Entity){

#define INJECTION_ACTIVE

#include "game_action/types/core/entity/ga_type__entity__payload.h"

#undef INJECTION_ACTIVE

} GA_Entity;

#undef GA_TYPE_CONTEXT
#endif
