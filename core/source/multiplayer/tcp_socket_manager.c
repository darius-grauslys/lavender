#include "multiplayer/tcp_socket_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "multiplayer/tcp_socket.h"
#include "platform_defaults.h"
#include "serialization/hashing.h"
#include "serialization/serialization_header.h"

static inline
TCP_Socket **get_p_ptr_of__tcp_socket_by__index_from__ptr_array(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Index__u32 index_of__tcp_socket) {
    return &p_tcp_socket_manager->ptr_array_of__tcp_sockets[
        index_of__tcp_socket];
}

void initialize_tcp_socket_manager(
        TCP_Socket_Manager *p_tcp_socket_manager,
        m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager) {
    initialize_serialization_header__contiguous_array(
            (Serialization_Header*)&p_tcp_socket_manager
            ->tcp_sockets, 
            MAX_QUANTITY_OF__TCP_SOCKETS, 
            sizeof(TCP_Socket));
    memset(p_tcp_socket_manager->ptr_array_of__tcp_sockets,
            0,
            sizeof(TCP_Socket*) * MAX_QUANTITY_OF__TCP_SOCKETS);

    p_tcp_socket_manager->m_poll_tcp_socket_manager = 
        m_poll_tcp_socket_manager;
}

TCP_Socket *open_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32) {
    TCP_Socket *p_tcp_socket =
        (TCP_Socket*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)&p_tcp_socket_manager
                    ->tcp_sockets, 
                MAX_QUANTITY_OF__TCP_SOCKETS, 
                uuid_of__tcp_socket__u32);

    if (!p_tcp_socket)
        return 0;

    initialize_tcp_socket(
            p_tcp_socket, 
            ipv4_address, 
            uuid_of__tcp_socket__u32);

    for (Index__u32 index_of__tcp_socket = 0;
            index_of__tcp_socket < MAX_QUANTITY_OF__TCP_SOCKETS;
            index_of__tcp_socket++) {
        TCP_Socket **p_ptr_of__tcp_socket =
            get_p_ptr_of__tcp_socket_by__index_from__ptr_array(
                    p_tcp_socket_manager, 
                    index_of__tcp_socket);

        if (!*p_ptr_of__tcp_socket) {
            *p_ptr_of__tcp_socket = p_tcp_socket;
            break;
        }
    }

    return p_tcp_socket;
}

void close_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        TCP_Socket *p_tcp_socket) {
#ifndef NDEBUG
    unsigned long index = p_tcp_socket
        - p_tcp_socket_manager->tcp_sockets;
    if (index >= MAX_QUANTITY_OF__TCP_SOCKETS) {
        debug_error("close_socket_on__tcp_socket_manager__ipv4, this socket was not allocated with this manager.");
        return;
    }
#endif

    TCP_Socket **p_ptr_tcp_socket__being_release;
    TCP_Socket **p_ptr_tcp_socket__last;
    for (Index__u32 index_of__tcp_socket = 0;
            index_of__tcp_socket < MAX_QUANTITY_OF__TCP_SOCKETS;
            index_of__tcp_socket++) {
        TCP_Socket **p_ptr_of__tcp_socket =
            get_p_ptr_of__tcp_socket_by__index_from__ptr_array(
                    p_tcp_socket_manager, 
                    index_of__tcp_socket);

        if (*p_ptr_of__tcp_socket == p_tcp_socket) {
            p_ptr_tcp_socket__being_release = p_ptr_of__tcp_socket;
            continue;
        } else if (*p_ptr_of__tcp_socket) {
            p_ptr_tcp_socket__last = p_ptr_of__tcp_socket;
        } else {
            break;
        }
    }

    if (p_ptr_tcp_socket__being_release
            != p_ptr_tcp_socket__last) {
        *p_ptr_tcp_socket__being_release =
            *p_ptr_tcp_socket__last;
    }
    *p_ptr_tcp_socket__last = 0;

    initialize_tcp_socket_as__deallocated(p_tcp_socket);
}
