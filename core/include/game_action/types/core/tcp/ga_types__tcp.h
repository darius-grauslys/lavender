#ifndef GA_TYPES__TCP_H
#define GA_TYPES__TCP_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_TCP){

#define INJECTION_ACTIVE

#include "game_action/types/core/tcp/ga_type__tcp__connect.h"
#include "game_action/types/core/tcp/ga_type__tcp__connect_begin.h"
#include "game_action/types/core/tcp/ga_type__tcp__connect_delivery.h"

#undef INJECTION_ACTIVE

} GA_TCP;

#undef GA_TYPE_CONTEXT
#endif
