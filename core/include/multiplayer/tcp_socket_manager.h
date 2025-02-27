#ifndef TCP_SOCKET_MANAGER_H
#define TCP_SOCKET_MANAGER_H

#include "defines.h"
#include "defines_weak.h"
#include "platform_defaults.h"
#include "serialization/hashing.h"

void initialize_tcp_socket_manager(
        TCP_Socket_Manager *p_tcp_socket_manager,
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager);

TCP_Socket *open_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32);

void close_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        TCP_Socket *p_tcp_socket);

static inline
TCP_Socket *get_p_tcp_socket_for__this_client(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Client *p_client) {
    return (TCP_Socket*)dehash_identitier_u32_in__contigious_array(
            (Serialization_Header*)&p_tcp_socket_manager->tcp_sockets, 
            MAX_QUANTITY_OF__TCP_SOCKETS, 
            p_client->_serialization_header.uuid);
}


#endif
