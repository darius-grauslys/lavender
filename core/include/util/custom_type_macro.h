#ifndef GAME_ACTION__IMPORT_MACRO_H
#define GAME_ACTION__IMPORT_MACRO_H

///
/// The following header file provides import macros to
/// inject custom game actions into defines.h.
///
/// The macros are set up to allow for useful IDE 
/// functionality (like linting) while also serving
/// as a injection method into Game_Action_t in defines.h
///

#ifndef INJECTION_ACTIVE

#define LAV_TYPE__BEGIN(name)\
    typedef struct name ## _t

#define LAV_UNION__BEGIN(name)\
    typedef union name ## _t

#else

#define LAV_TYPE__BEGIN(name)\
    struct 

#define LAV_UNION__BEGIN(name)\
    union

#endif

#endif
