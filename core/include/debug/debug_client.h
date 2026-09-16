#ifndef DEBUG_CLIENT_H
#define DEBUG_CLIENT_H

#include "defines_weak.h"
#include <defines.h>

/*
 * debug_entiy.h provides functions which are intended to be invoked through
 * gdb or other debug modules.
 *
 * DO NOT USE debug_* functions in non-debug modules.
 * With the only exception being debug_* functions for logging.
 * See docs/core/debug/debug.md
 * TODO: make docs/core/debug/debug.md
 */

#ifndef NDEBUG

typedef struct DEBUG_Client_Scanner_t DEBUG_Client_Scanner;

///
/// A function to perform debug scanning operations with.
///
typedef DEBUG_Client_Scanner (*m_DEBUG_Client_Scanner_Func)();

typedef struct DEBUG_Client_Scanner_t {
    Game *p_game;
    Client *p_client__current;
    Game_Action *p_game_action__inbound__current;
    Game_Action *p_game_action__outbound__current;

    m_DEBUG_Client_Scanner_Func m_refresh;
    m_DEBUG_Client_Scanner_Func m_next_client;
    m_DEBUG_Client_Scanner_Func m_next_game_action__inbound;
    m_DEBUG_Client_Scanner_Func m_next_game_action__outbound;

    ///
    /// Module Post Condition:
    /// After every module function and ever m_ func
    /// the following fields will be updated to
    /// reflect engine state.
    ///
    Quantity__u32 quantity_of__clients;
    
    struct {
        Quantity__u32 quantity_of__game_actions__inbound;
        _Game_Action_Header game_action_header__inbound__current;
        Game_Action_Logic_Entry game_action_logic_entry__inbound__current;

        Quantity__u32 quantity_of__game_actions__outbound;
        _Game_Action_Header game_action_header__outbound__current;
        Game_Action_Logic_Entry game_action_logic_entry__outbound__current;
    } game_actions;
    
    Identifier__u32 uuid_of__client__current;
    Chunk_Vector__3i32 current_client__local_space__center__3i32;
    Client_Flags__u16 current_client__client_flags__u16;
} DEBUG_Client_Scanner;

DEBUG_Client_Scanner debug_get_client_scanner(Game *p_game);

#endif

#endif
