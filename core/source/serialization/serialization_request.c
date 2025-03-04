#include "serialization/serialization_request.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform.h"

bool initialize_serialization_request(
        Serialization_Request *p_serialization_request,
        void *p_file_handler,
        Quantity__u16 size_of__tcp_payload,
        Serialization_Request_Flags serialization_request_flags) {
    p_serialization_request
        ->serialization_request_flags = serialization_request_flags;

    if (!is_serialization_request__tcp_or_io(
                p_serialization_request)) {
        p_serialization_request
            ->p_file_handler = p_file_handler;
        return true;
    }

    Quantity__u16 quantity_of__expected__tcp_packets =
        (size_of__tcp_payload
         + GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES)
        / GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES
        ;
    Quantity__u16 quantity_of__bytes_in__bitmap =
        (quantity_of__expected__tcp_packets >> 3) + 1;

    p_serialization_request
        ->pM_packet_bitmap = malloc(
                quantity_of__bytes_in__bitmap);
    memset(
            p_serialization_request
            ->pM_packet_bitmap,
            0,
            quantity_of__bytes_in__bitmap);
    if (!p_serialization_request
            ->pM_packet_bitmap) {
        debug_error("initialize_serialization_request, failed to allocate pM_packet_bitmap.");
        return false;
    }

    p_serialization_request
        ->p_tcp_packet_destination =
        p_file_handler;
    p_serialization_request
        ->quantity_of__bytes_in__destination =
        size_of__tcp_payload;
    p_serialization_request
        ->quantity_of__tcp_packets__anticipated =
        quantity_of__expected__tcp_packets;

    return true;
}

void release_serialization_request(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialization_request) {
    if (is_serialization_request__tcp_or_io(
                p_serialization_request)) {
        free(p_serialization_request->pM_packet_bitmap);
    }
    PLATFORM_release_serialization_request(
            p_PLATFORM_file_system_context, 
            p_serialization_request);
}

void initialize_serialization_request_as__uninitalized(
        Serialization_Request *p_serialization_request) {
    initialize_serialization_request(
            p_serialization_request, 
            0,
            0,
            SERIALIZATION_REQUEST_FLAGS__NONE);
}
