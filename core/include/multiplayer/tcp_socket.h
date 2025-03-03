#ifndef TCP_SOCKET_H
#define TCP_SOCKET_H

#include "defines.h"
#include "defines_weak.h"

#define TCP_DELIVERY(type, name)\
    union {\
        type name;\
        TCP_Packet tcp_packet;\
    }

void initialize_tcp_socket(
        TCP_Socket *p_tcp_socket,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32);

void initialize_tcp_socket_as__deallocated(
        TCP_Socket *p_tcp_socket);

///
/// After opening the non-server socket, continue to
/// call this until a connection result is determined
/// via the return value.
///
TCP_Socket_State poll_tcp_socket_for__connection(
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

static inline
TCP_Socket_Flags__u8 get_tcp_socket_flags_from__tcp_socket(
        TCP_Socket *p_tcp_socket) {
    return p_tcp_socket->tcp_socket_flags__u8;
}

static inline
bool is_tcp_socket__manually_driven(
        TCP_Socket *p_tcp_socket) {
    return get_tcp_socket_flags_from__tcp_socket(p_tcp_socket)
        & TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN
        ;
}

static inline
void set_tcp_socket_as__manually_driven(
        TCP_Socket *p_tcp_socket) {
    p_tcp_socket->tcp_socket_flags__u8 |=
        TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN;
}

static inline
void set_tcp_socket_as__automatically_driven(
        TCP_Socket *p_tcp_socket) {
    p_tcp_socket->tcp_socket_flags__u8 &=
        ~TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN;
}

#endif
