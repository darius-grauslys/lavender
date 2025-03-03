#ifndef TCP_SOCKET_MANAGER_H
#define TCP_SOCKET_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "platform_defaults.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"

void initialize_tcp_socket_manager(
        TCP_Socket_Manager *p_tcp_socket_manager,
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager);

TCP_Socket *accept_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32);

TCP_Socket *open_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32);

TCP_Socket *open_server_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid_of__tcp_socket__u32,
        Index__u16 port);

void close_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        TCP_Socket *p_tcp_socket);

///
/// Returns a PLATFORM_TCP_Socket if a connection
/// is received.
///
PLATFORM_TCP_Socket *poll_tcp_socket_manager_for__pending_connections(
        TCP_Socket_Manager *p_tcp_socket_manager,
        TCP_Socket *p_tcp_socket__server,
        IPv4_Address *p_ipv4);

void reject_pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager);

///
/// Returns false if acceptance failed.
///
TCP_Socket *accept_pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid__u32);

static inline
TCP_Socket *get_p_tcp_socket_for__this_uuid(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid) {
    TCP_Socket *p_tcp_socket =
        (TCP_Socket*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)&p_tcp_socket_manager->tcp_sockets, 
            MAX_QUANTITY_OF__TCP_SOCKETS, 
            uuid);
    if (is_serialized_struct__deallocated(
                (Serialization_Header*)p_tcp_socket)) {
        return 0;
    }

    return p_tcp_socket;
}

static inline
PLATFORM_TCP_Context *get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
        TCP_Socket_Manager *p_tcp_socket_manager) {
    return p_tcp_socket_manager->p_PLATFORM_tcp_context;
}

static inline
Quantity__u32 get_quantity_of__active_tcp_sockets(
        TCP_Socket_Manager *p_tcp_socket_manager) {
    return p_tcp_socket_manager->quantity_of__connections;
}

#endif
