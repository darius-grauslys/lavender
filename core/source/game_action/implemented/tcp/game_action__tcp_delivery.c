#include "game_action/implemented/tcp/game_action__tcp_delivery.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_entry.h"
#include "game_action/game_action_logic_table.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "process/game_action_process.h"

void m_process__game_action__tcp_delivery__inbound(
        Process *p_this_process,
        Game *p_game) {
    Game_Action *p_game_action =
        (Game_Action*)p_this_process->p_process_data;

    Process *p_process =
        get_p_process_by__uuid(
                get_p_process_manager_from__game(p_game), 
                p_game_action->uuid_of__game_action__responding_to);

    if (!p_process) {
        debug_error("m_process__game_action__tcp_delivery__inbound, no receiver.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }
    
    switch (get_the_kind_of__process(p_process)) {
        default:
            debug_error("m_process__game_action__tcp_delivery__inbound, invalid receiver.");
            fail_game_action_process(
                    p_game, 
                    p_this_process);
            return;
        case Process_Kind__Serialized:
            break;
    }

    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_process->p_process_data;

    if (p_serialization_request->quantity_of__tcp_packets__anticipated
            <= p_game_action->ga_kind__tcp_delivery__packet_index) {
        debug_error("m_process__game_action__tcp_delivery__inbound, excessive packet.");
        fail_game_action_process(
                p_game, 
                p_this_process);
        return;
    }

    Index__u32 index_of__memcpy = 
        GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
        * p_game_action->ga_kind__tcp_delivery__packet_index;
    
    Quantity__u32 quantity_of__bytes_to__copy =
        min__u32(
                GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES,
                p_serialization_request
                    ->quantity_of__bytes_in__destination
                - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
                    * (p_game_action->ga_kind__tcp_delivery__packet_index+1)));

    memcpy(
            p_serialization_request->p_tcp_packet_destination,
            p_game_action->ga_kind__tcp_delivery__payload,
            quantity_of__bytes_to__copy);

    p_serialization_request
        ->pM_packet_bitmap[TCP_PAYLOAD_BYTE(
                p_game_action->ga_kind__tcp_delivery__packet_index)] |=
        TCP_PAYLOAD_BIT(p_game_action->ga_kind__tcp_delivery__packet_index);

    complete_game_action_process(
            p_game, 
            p_this_process);
}

void register_game_action__tcp_delivery(
        Game_Action_Logic_Table *p_game_action_logic_table) {
    initialize_game_action_logic_entry_as__message_response(
            get_p_game_action_logic_entry_by__game_action_kind(
                p_game_action_logic_table, 
                Game_Action_Kind__TCP_Delivery));
}

void initialize_game_action_for__tcp_delivery(
        Game_Action *p_game_action,
        Identifier__u32 uuid_of__client_to__send_to,
        Identifier__u32 uuid_to__respond,
        u8 *p_payload,
        u32 quantity_of__bytes_in__payload,
        Index__u16 index_of__payload) {
    initialize_game_action(p_game_action);
    set_the_kind_of__game_action(
            p_game_action, 
            Game_Action_Kind__TCP_Delivery);
    memcpy(p_game_action->ga_kind__tcp_delivery__payload,
            p_payload,
            min__u32(
                quantity_of__bytes_in__payload,
                GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES));
    p_game_action->ga_kind__tcp_delivery__packet_index =
        index_of__payload;
    p_game_action->uuid_of__client__u32 =
        uuid_of__client_to__send_to;
    p_game_action->uuid_of__game_action__responding_to =
        uuid_to__respond;
}
