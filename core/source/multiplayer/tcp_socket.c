#include "multiplayer/tcp_socket.h"
#include "defines.h"
#include "defines_weak.h"
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
    return p_tcp_socket->index_of__enqueue_end
        != p_tcp_socket->index_of__enqueue_begin;
}

static inline
Quantity__u32 get_quantity_of__remaining_packet_slots_in__tcp_socket(
        TCP_Socket *p_tcp_socket) {
    if (p_tcp_socket->index_of__enqueue_begin
            > p_tcp_socket->index_of__enqueue_end) {
        return
            (MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET
             - p_tcp_socket->index_of__enqueue_begin)
            + p_tcp_socket->index_of__enqueue_end
            ;
    }

    return p_tcp_socket->index_of__enqueue_end
        - p_tcp_socket->index_of__enqueue_begin;
}

static inline
TCP_Packet *get_p_tcp_packet_thats__available_for_enqueue(
        TCP_Socket *p_tcp_socket) {
    return &p_tcp_socket->queue_of__tcp_packet[
        p_tcp_socket->index_of__enqueue_begin];
}

static inline
TCP_Packet *get_p_tcp_packet_thats__oldest_in_queue(
        TCP_Socket *p_tcp_socket) {
    return &p_tcp_socket->queue_of__tcp_packet[
        p_tcp_socket->index_of__enqueue_end];
}

static inline
Quantity__u32 get_quantity_of__available_sequential_bytes_for__packet_reception(
        TCP_Socket *p_tcp_socket) {
    if (p_tcp_socket->index_of__enqueue_begin
            > p_tcp_socket->index_of__enqueue_end) {
        return MAX_SIZE_OF__TCP_PACKET
            * (MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET
                    - p_tcp_socket->index_of__enqueue_begin);
    }
    return (p_tcp_socket->index_of__enqueue_end
            - p_tcp_socket->index_of__enqueue_begin)
        * MAX_SIZE_OF__TCP_PACKET;
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
            sizeof(TCP_Socket)
            * MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET);
    p_tcp_socket->tcp_socket__address = ipv4_address;
    p_tcp_socket->index_of__enqueue_begin = 0;
    p_tcp_socket->index_of__enqueue_end = 
        MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET - 1;
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

void send_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of__bytes) {
    PLATFORM_tcp_send(
            p_tcp_socket, 
            p_bytes, 
            length_of__bytes);
}

i32 receive_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket) {

    Quantity__u32 quantity_of__total_bytes_in__destination =
        get_quantity_of__remaining_packet_slots_in__tcp_socket(
                p_tcp_socket)
        * MAX_SIZE_OF__TCP_PACKET;
    i32 total_quantity__received = 0;
    i32 quantity_received = 0;
    do {
        Quantity__u32 length_of_bytes_in__destination =
            get_quantity_of__available_sequential_bytes_for__packet_reception(
                    p_tcp_socket);
        quantity_received =
            PLATFORM_tcp_recieve(
                    p_tcp_socket, 
                    (u8*)&p_tcp_socket->queue_of__tcp_packet[
                        p_tcp_socket->index_of__enqueue_begin], 
                    length_of_bytes_in__destination,
                    quantity_of__total_bytes_in__destination);
        switch (quantity_received) {
            default:
                break;
            case TCP_ERROR__DESTINATION_OVERFLOW:
                break;
            case TCP_ERROR__TOO_MANY_PACKETS:
                return quantity_received;
        }
        total_quantity__received += quantity_received;
    } while (!quantity_received);

    Quantity__u16 length_of__bytes = total_quantity__received;
    for (Index__u32 index_of__packet = 0;
            index_of__packet 
            < (total_quantity__received / MAX_SIZE_OF__TCP_PACKET);
            index_of__packet++) {

        p_tcp_socket->packet_size__entries[
            p_tcp_socket->index_of__enqueue_begin] =
                (length_of__bytes > MAX_SIZE_OF__TCP_PACKET)
                ? MAX_SIZE_OF__TCP_PACKET
                : length_of__bytes
                ;
        length_of__bytes -= 
            p_tcp_socket->packet_size__entries[
            p_tcp_socket->index_of__enqueue_begin];

        p_tcp_socket->index_of__enqueue_begin =
            (p_tcp_socket->index_of__enqueue_begin
             + 1)
            % MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET
            ;
    }

    return total_quantity__received;
}

///
/// Note this removes the TCP_Packet from the socket.
///
bool get_latest__delivery_from__tcp_socket(
        TCP_Socket *p_tcp_socket,
        TCP_Packet *p_tcp_packet__returned) {
    TCP_Packet *p_tcp_packet =
        get_p_tcp_packet_thats__oldest_in_queue(
                p_tcp_socket);

    if (!p_tcp_packet) {
        memset(
                p_tcp_packet__returned,
                0,
                sizeof(TCP_Packet));
        return false;
    }

    *p_tcp_packet__returned =
        *p_tcp_packet;

    memset(
            p_tcp_packet,
            0,
            sizeof(TCP_Packet));

    return true;
}

