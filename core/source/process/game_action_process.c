#include "process/game_action_process.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/implemented/tcp/game_action__tcp_delivery.h"
#include "platform.h"
#include "process/process.h"
#include "serialization/serialization_request.h"

bool set_game_action_process_as__tcp_payload_receiver(
        Game *p_game,
        Process *p_process,
        u8 *p_payload_destination,
        Quantity__u16 quantity_of__bytes_in__payload_destination) {
    Serialization_Request *p_serialization_request =
        PLATFORM_allocate_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(p_game));

    if (!p_serialization_request) {
        debug_error("set_game_action_process_as__tcp_payload_receiver, failed to allocate p_serialization_request.");
        return false;
    }

    activate_serialization_request(
            p_serialization_request, 
            p_payload_destination, 
            quantity_of__bytes_in__payload_destination, 
            true);

    void *p_process_data =
        p_process->p_process_data;
    p_serialization_request->p_data =
        p_process_data;
    p_process->p_process_data =
        p_serialization_request;

    set_serialization_request_as__tcp(
            p_serialization_request);
    set_the_kind_of__process(
            p_process, 
            Process_Kind__Serialized);

    return true;
}

void complete_game_action_process_for__tcp(
        Game *p_game,
        Process *p_process) {
    Serialization_Request *p_serialization_request =
            (Serialization_Request *)p_process->p_process_data;
    if (p_serialization_request->p_data) {
        resolve_game_action(
                p_game, 
                (Game_Action *)p_serialization_request->p_data);
        p_serialization_request->p_data = 0;
    }
    PLATFORM_release_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_serialization_request);
    complete_process(p_process);
}

void fail_game_action_process_for__tcp(
        Game *p_game,
        Process *p_process) {
    Serialization_Request *p_serialization_request =
            (Serialization_Request *)p_process->p_process_data;
    if (p_serialization_request->p_data) {
        resolve_game_action(
                p_game, 
                (Game_Action *)p_serialization_request->p_data);
    }
    deactivate_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_serialization_request);
    fail_process(p_process);
}

Index__u32 get_tcp_packet__bitmap_data(
        u8 *p_bitmap,
        Quantity__u16 quantity_of__tcp_packets__anticipated) {
    Index__u32 index_of__bitmap_byte = 0;
    for (; index_of__bitmap_byte <
            TCP_PAYLOAD_BYTE(
                quantity_of__tcp_packets__anticipated);
            index_of__bitmap_byte++) {
        if (p_bitmap[index_of__bitmap_byte] == (u8)-1) {
            continue;
        }
        break;
    }
    Index__u32 index_of__bitmap_bit = 0;
    for (; index_of__bitmap_bit < 8; index_of__bitmap_bit++) {
        if (p_bitmap[index_of__bitmap_byte]
                    & BIT(index_of__bitmap_bit)) {
            continue;
        }
        break;
    }
    index_of__bitmap_bit += index_of__bitmap_byte << 3;
    return index_of__bitmap_bit;
}

///
/// game_action_processes that set themselves as tcp_payload_receivers
/// should call this function on every process iteration.
///
/// It will return System_Busy until all expected tcp packets have
/// arrived, after which it will return None.
///
PLATFORM_Read_File_Error poll_game_action_process__tcp_receive(
        Game *p_game,
        Process *p_process) {
    Serialization_Request *p_serialization_request =
        p_process->p_process_data;

#ifndef NDEBUG
    if (!is_serialization_request__tcp_or_io(
                p_serialization_request)) {
        debug_error("poll_game_action_process__tcp_receive, bad state.");
        return PLATFORM_Read_File_Error__Unknown;
    }
#endif

    u8 *p_bitmap = p_serialization_request->pM_packet_bitmap;
    Index__u32 index_of__bitmap_bit =
        get_tcp_packet__bitmap_data(
                p_bitmap,
                p_serialization_request
                ->quantity_of__tcp_packets__anticipated);

    if (index_of__bitmap_bit
            >= p_serialization_request->quantity_of__tcp_packets__anticipated) {
        return PLATFORM_Read_File_Error__End_Of_File;
    }
    
    return PLATFORM_Read_File_Error__System_Busy;
}

///
/// Returns System_Busy until it finishes with Max_Size_Reached.
/// Will return ANYTHING else as an error.
///
/// NOTE: You >>DO NOT<< have to set your process as a tcp process
/// to call this function. 
///
PLATFORM_Write_File_Error poll_game_action_process__tcp_delivery(
        Game *p_game,
        Identifier__u32 uuid_of__client_to__send_to,
        Identifier__u32 uuid_of__game_action__responding_to,
        u8 *p_payload__source,
        Quantity__u32 quantity_of__bytes_in__payload__source,
        u8 *p_payload__bitmap,
        Quantity__u16 quantity_of__bits_in__payload__bitmap) {
    u8 *p_bitmap = p_payload__bitmap;
    Index__u32 index_of__bitmap_bit =
        get_tcp_packet__bitmap_data(
                p_bitmap,
                quantity_of__bits_in__payload__bitmap);

    if (index_of__bitmap_bit
            >= quantity_of__bits_in__payload__bitmap) {
        return PLATFORM_Write_File_Error__Max_Size_Reached;
    }

    Quantity__u32 quantity_of__bytes_to__send =
        GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
        * (index_of__bitmap_bit+1);
    quantity_of__bytes_to__send = 
        (quantity_of__bytes_to__send
            > quantity_of__bytes_in__payload__source)
        ? quantity_of__bytes_in__payload__source
            - (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
                    * index_of__bitmap_bit)
        : GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
        ;

    dispatch_game_action__tcp_delivery(
            p_game, 
            uuid_of__client_to__send_to, 
            uuid_of__game_action__responding_to, 
            p_payload__source
            + (GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
                * index_of__bitmap_bit), 
            quantity_of__bytes_to__send, 
            index_of__bitmap_bit);

    p_bitmap[TCP_PAYLOAD_BYTE(index_of__bitmap_bit)] |=
        BIT(TCP_PAYLOAD_BIT(index_of__bitmap_bit));

    return PLATFORM_Write_File_Error__System_Busy;
}
