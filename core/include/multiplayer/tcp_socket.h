#ifndef TCP_SOCKET_H
#define TCP_SOCKET_H

#include "defines.h"
#include "defines_weak.h"

void initialize_tcp_socket(
        TCP_Socket *p_tcp_socket,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32);

void initialize_tcp_socket_as__deallocated(
        TCP_Socket *p_tcp_socket);

void send_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of__bytes);

///
/// Returns the quantity of bytes received, or a TCP_ERROR__XXX.
///
i32 receive_bytes_over__tcp_socket(
        TCP_Socket *p_tcp_socket);

///
/// Note this removes the TCP_Packet from the socket.
/// Returns the number of packets sent, 0 if queue is empty.
/// Returns -1 if the destination buffer is smaller than
/// the delivery
///
bool get_latest__delivery_from__tcp_socket(
        TCP_Socket *p_tcp_socket,
        TCP_Packet *p_tcp_packet__returned);

void bind_tcp_socket(
        TCP_Socket *p_tcp_socket,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket);

void unbind_tcp_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        TCP_Socket *p_tcp_socket);

static inline
PLATFORM_TCP_Socket *get_p_PLATFORM_tcp_socket_from__tcp_socket(
        TCP_Socket *p_tcp_socket) {
    return p_tcp_socket->p_PLATFORM_tcp_socket;
}

static inline
TCP_Socket_State get_state_of__tcp_socket(
        TCP_Socket *p_tcp_socket) {
    return p_tcp_socket->tcp_socket__state_of;
}

static inline
void set_state_of__tcp_socket(
        TCP_Socket *p_tcp_socket,
        TCP_Socket_State state_of__tcp_socket) {
    p_tcp_socket->tcp_socket__state_of =
        state_of__tcp_socket;
}

#endif
