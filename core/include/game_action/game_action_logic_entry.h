#ifndef GAME_ACTION_LOGIC_ENTRY_H
#define GAME_ACTION_LOGIC_ENTRY_H

#include "defines.h"

void initialize_game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action_Flags game_action_flags__outbound,
        Game_Action_Flags game_action_flags__outbound_mask,
        Game_Action_Flags game_action_flags__inbound,
        Game_Action_Flags game_action_flags__inbound_mask,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__outbound,
        Process_Flags__u8 process_flags__outbound,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound);

void santize_game_action__inbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action);

void santize_game_action__outbound(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Game_Action *p_game_action);

static inline
void initialize_game_action_logic_entry_as__process__out_and_in(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__outbound,
        Process_Flags__u8 process_flags__outbound,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE, 
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE, 
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            process_priority__u8,
            m_process__game_action__outbound, 
            process_flags__outbound,
            m_process__game_action__inbound,
            process_flags__inbound);
}

static inline
void initialize_game_action_logic_entry_as__process__out(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__outbound,
        Process_Flags__u8 process_flags__outbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE, 
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            process_priority__u8,
            m_process__game_action__outbound, 
            process_flags__outbound,
            0,
            PROCESS_FLAGS__NONE);

}

static inline
void initialize_game_action_logic_entry_as__process__in(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS
            | GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE, 
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            process_priority__u8,
            0, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__inbound,
            process_flags__inbound);

}

static inline
void initialize_game_action_logic_entry_as__react__out(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__outbound,
        Process_Flags__u8 process_flags__outbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            process_priority__u8,
            m_process__game_action__outbound,
            process_flags__outbound,
            0, 
            PROCESS_FLAGS__NONE);
}

static inline
void initialize_game_action_logic_entry_as__react__in(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        Process_Priority__u8 process_priority__u8,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE,
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            process_priority__u8,
            0, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__inbound,
            process_flags__inbound);
}

static inline
void initialize_game_action_logic_entry_as__message(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE, 
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            PROCESS_PRIORITY__MINIMUM,
            0, 
            0,
            0,
            0);
}

static inline
void initialize_game_action_logic_entry_as__broadcast(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_BROADCASTED, 
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE, 
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            PROCESS_PRIORITY__MINIMUM,
            0, 
            0,
            0,
            0);
}

static inline
void initialize_game_action_logic_entry_as__message_response(
        Game_Action_Logic_Entry *p_game_action_logic_entry,
        m_Process m_process__game_action__inbound,
        Process_Flags__u8 process_flags__inbound) {
    initialize_game_action_logic_entry(
            p_game_action_logic_entry, 
            GAME_ACTION_FLAGS__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE, 
            GAME_ACTION_FLAGS__INBOUND_SANITIZE
            | GAME_ACTION_FLAGS__BIT_IS_RESPONSE, 
            GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE, 
            PROCESS_PRIORITY__MINIMUM,
            0, 
            PROCESS_FLAGS__NONE,
            m_process__game_action__inbound,
            process_flags__inbound);
}

static inline
m_Process get_m_process__outbound_of__game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    return p_game_action_logic_entry
        ->m_process_of__game_action__outbound;
}

static inline
m_Process get_m_process__inbound_of__game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    return p_game_action_logic_entry
        ->m_process_of__game_action__inbound;
}

static inline
Process_Priority__u8 get_process_priority__game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    return p_game_action_logic_entry
        ->process_priority__u8;
}

static inline
Process_Flags__u8 get_process_flags__outbound_of__game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    return p_game_action_logic_entry
        ->process_flags_of__game_action__outbound;
}

static inline
Process_Flags__u8 get_process_flags__inbound_of__game_action_logic_entry(
        Game_Action_Logic_Entry *p_game_action_logic_entry) {
    return p_game_action_logic_entry
        ->process_flags_of__game_action__inbound;
}

#endif
