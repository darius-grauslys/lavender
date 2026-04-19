#ifndef GA_TYPES__IMPLEMENTED_H
#define GA_TYPES__IMPLEMENTED_H
#define GA_TYPE_CONTEXT

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_Implemented) {
#ifndef INJECTION_ACTIVE
#define INJECTION_ACTIVE
#define INJECTION_ACTIVE__IMPLEMENTED
#endif

// GEN-BEGIN
// GEN-END

#ifdef INJECTION_ACTIVE__IMPLEMENTED
#undef INJECTION_ACTIVE__IMPLEMENTED
#undef INJECTION_ACTIVE
#endif
} GA_Implemented;

#undef GA_TYPE_CONTEXT
#endif // Header guard
