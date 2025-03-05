#include "multiplayer/tcp_socket.h"
#include "defines.h"
#include "defines_weak.h"
#include "multiplayer/tcp_socket_manager.h"
#include "platform.h"
#include "platform_defaults.h"
#include "serialization/serialization_header.h"

static inline
Quantity__u32 get_size_of__tcp_packet(
        TCP_Socket *p_tcp_socket,
        TCP_Packet *p_tcp_packet) {
    return p_tcp_socket->packet_size__entries[
        p_tcp_packet - p_tcp_socket->queue_of__tcp_packet];
}

static inline
void set_size_of__tcp_packet(
        TCP_Socket *p_tcp_socket,
        TCP_Packet *p_tcp_packet,
        Quantity__u32 size_of__packet) {
    p_tcp_socket->packet_size__entries[
        p_tcp_packet - p_tcp_socket->queue_of__tcp_packet] =
            size_of__packet;
}

static inline
bool can_tcp_socket__receive_more_packets(
        TCP_Socket *p_tcp_socket) {
    return p_tcp_socket->quantity_of__received_packets
        < MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET;
}

static inline
TCP_Packet *get_p_tcp_packet_by__index_from__queue_of__tcp_socket(
        TCP_Socket *p_tcp_socket,
        Index__u32 index_of__packet) {
    return &p_tcp_socket->queue_of__tcp_packet[
        index_of__packet & (MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET-1)];
}

void initialize_tcp_socket(
        TCP_Socket *p_tcp_socket,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32) {
    initialize_serialization_header(
            &p_tcp_socket->_serialization_header, 
            uuid_of__tcp_socket__u32, 
            sizeof(TCP_Socket));
    memset(&p_tcp_socket->queue_of__tcp_packet,
            0,
            sizeof(TCP_Packet)
            * MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET);
    p_tcp_socket->tcp_socket__address = ipv4_address;
    p_tcp_socket->index_of__enqueue_begin = 0;
    p_tcp_socket->quantity_of__received_packets = 0;
    p_tcp_socket->tcp_socket__state_of = 
        TCP_Socket_State__None;
}

void initialize_tcp_socket_as__deallocated(
        TCP_Socket *p_tcp_socket) {
    memset(p_tcp_socket,
            0,
            sizeof(TCP_Socket));
    initialize_serialization_header_for__deallocated_struct(
            &p_tcp_socket->_serialization_header, 
            sizeof(TCP_Socket));
}

TCP_Socket_State poll_tcp_socket_for__connection(
        TCP_Socket *p_tcp_socket) {
    if (!p_tcp_socket
            || !p_tcp_socket->p_PLATFORM_tcp_socket)
        return TCP_Socket_State__None;
    switch (get_state_of__tcp_socket(p_tcp_socket)) {
        default:
            return p_tcp_socket->tcp_socket__state_of;
        case TCP_Socket_State__None:
        case TCP_Socket_State__Connecting:
            break;
    }
    return (p_tcp_socket->tcp_socket__state_of =
        PLATFORM_tcp_poll_connect(
                p_tcp_socket->p_PLATFORM_tcp_socket));
}

void send_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of__bytes) {
    PLATFORM_tcp_send(
            p_tcp_socket->p_PLATFORM_tcp_socket, 
            p_bytes, 
            length_of__bytes);
}

i32 receive_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket) {
    if (!can_tcp_socket__receive_more_packets(
                p_tcp_socket)) {
        return TCP_ERROR__QUEUE_FULL;
    }

    i32 quantity_received = 0;
    do {
        if (!can_tcp_socket__receive_more_packets(
                    p_tcp_socket)) {
            debug_error("receive_bytes_over__tcp_socket, packet overflow.");
            break;
        }
        quantity_received =
            PLATFORM_tcp_recieve(
                    p_tcp_socket->p_PLATFORM_tcp_socket, 
                    (u8*)get_p_tcp_packet_by__index_from__queue_of__tcp_socket(
                        p_tcp_socket, 
                        p_tcp_socket->index_of__enqueue_begin
                        + p_tcp_socket->quantity_of__received_packets), 
                    MAX_SIZE_OF__TCP_PACKET);
        switch (quantity_received) {
            case TCP_ERROR__DESTINATION_OVERFLOW:
                debug_error("receive_bytes_over__tcp_socket, buffer overflow.");
                return 0;
            case 0:
                break;
            default:
                p_tcp_socket->quantity_of__received_packets++;
                break;
        }
    } while (quantity_received);

    return MAX_SIZE_OF__TCP_PACKET
        * p_tcp_socket->quantity_of__received_packets;
}

///
/// Note this removes the TCP_Packet from the socket.
///
bool get_latest__delivery_from__tcp_socket(
        TCP_Socket *p_tcp_socket,
        TCP_Packet *p_tcp_packet__returned) {
    if (!p_tcp_socket->quantity_of__received_packets)
        return false;

    TCP_Packet *p_tcp_packet =
        get_p_tcp_packet_by__index_from__queue_of__tcp_socket(
                p_tcp_socket,
                p_tcp_socket->index_of__enqueue_begin++);

    *p_tcp_packet__returned =
        *p_tcp_packet;

    memset(
            p_tcp_packet,
            0,
            sizeof(TCP_Packet));

    p_tcp_socket->quantity_of__received_packets--;

    return true;
}

void bind_tcp_socket(
        TCP_Socket *p_tcp_socket,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    if (p_tcp_socket->p_PLATFORM_tcp_socket) {
        debug_abort("bind_tcp_socket, p_tcp_socket is already bound.");
        return;
    }

    p_tcp_socket->p_PLATFORM_tcp_socket =
        p_PLATFORM_tcp_socket;
}
 
void unbind_tcp_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        TCP_Socket *p_tcp_socket) {
    if (!PLATFORM_tcp_close_socket(
                p_PLATFORM_tcp_context, 
                get_p_PLATFORM_tcp_socket_from__tcp_socket(
                    p_tcp_socket))) {
        debug_error("unbind_tcp_socket, failed to unbind.");
        return;
    }

    p_tcp_socket->p_PLATFORM_tcp_socket = 0;
}
