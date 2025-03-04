#ifndef GAME_ACTION_PROCESS_H
#define GAME_ACTION_PROCESS_H

#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "process/process.h"

///
/// Set this process to receive tcp packets for a certain payload.
/// This will result in p_process_data pointing to a p_serialization_request
/// and the p_serialization_request's p_data set to the former contents of
/// p_process_data.
///
/// NOTE: If p_serialization_request->p_data is NOT a game_action, 
/// then you >>MUST<< release p_data prior to calling the complete/fail
/// variants below, >>AND<< set p_data to >>NULL<<.
///
/// NOTE: After calling this, you >>MUST<< use the corresponding
/// complete/fail functions below instead of the inlined variants.
///
/// Returns false if failed to modify the process.
///
bool set_game_action_process_as__tcp_payload_receiver(
        Game *p_game,
        Process *p_process,
        u8 *p_payload_destination,
        Quantity__u16 quantity_of__bytes_in__payload_destination);

void complete_game_action_process_for__tcp(
        Game *p_game,
        Process *p_process);

void fail_game_action_process_for__tcp(
        Game *p_game,
        Process *p_process);

///
/// game_action_processes that set themselves as tcp_payload_receivers
/// should call this function on every process iteration.
///
/// It will return System_Busy until all expected tcp packets have
/// arrived, after which it will return End_Of_File.
///
PLATFORM_Read_File_Error poll_game_action_process__tcp_receive(
        Game *p_game,
        Process *p_process);

///
/// Returns System_Busy until it finishes with Max_Size_Reached.
/// Will return ANYTHING else as an error.
///
/// NOTE: You >>DO NOT<< have to set your process as a tcp process
/// to call this function. p_game_action must be your process's
/// assigned game_action.
///
PLATFORM_Write_File_Error poll_game_action_process__tcp_delivery(
        Game *p_game,
        Identifier__u32 uuid_of__client_to__send_to,
        Identifier__u32 uuid_of__game_action__responding_to,
        u8 *p_payload__source,
        Quantity__u32 quantity_of__bytes_in__payload__source,
        u8 *p_payload__bitmap,
        Quantity__u16 quantity_of__bits_in__payload__bitmap);

///
/// NOTE: This is only valid to call if
/// p_process->p_process_data is to the
/// associated persisted game_action.
///
/// If this is not the case, call
/// finish_process(...) instead.
///
static inline
void complete_game_action_process(
        Game *p_game,
        Process *p_process) {
    Game_Action *p_game_action =
        (Game_Action*)p_process->p_process_data;
    resolve_game_action(
            p_game, 
            p_game_action);
    complete_process(p_process);
}

///
/// NOTE: This is only valid to call if
/// p_process->p_process_data is to the
/// associated persisted game_action.
///
/// If this is not the case, call
/// fail_process(...) instead.
///
static inline
void fail_game_action_process(
        Game *p_game,
        Process *p_process) {
    Game_Action *p_game_action =
        (Game_Action*)p_process->p_process_data;
    resolve_game_action(
            p_game, 
            p_game_action);
    fail_process(p_process);
}
#endif
