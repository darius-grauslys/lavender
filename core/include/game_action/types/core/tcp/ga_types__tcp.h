#ifndef GA_TYPES__TCP_H
#define GA_TYPES__TCP_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_UNION__BEGIN(GA_TCP){

#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__TCP
#endif

#include "game_action/types/core/tcp/ga_type__tcp__connect.h"
#include "game_action/types/core/tcp/ga_type__tcp__connect_begin.h"
#include "game_action/types/core/tcp/ga_type__tcp__connect_delivery.h"

#ifdef INJECTION_ACTIVE__TCP
#undef INJECTION_ACTIVE__TCP
#undef INJECTION_ACTIVE
#endif

} GA_TCP;

#undef GA_TYPE_CONTEXT
#endif
