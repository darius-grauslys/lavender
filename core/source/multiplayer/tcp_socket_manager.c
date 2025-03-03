#include "multiplayer/tcp_socket_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game_action/game_action.h"
#include "multiplayer/tcp_socket.h"
#include "platform.h"
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

static inline
PLATFORM_TCP_Socket *get_p_PLATFORM_tcp_socket__pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager) {
    return p_tcp_socket_manager
        ->p_PLATFORM_tcp_socket__pending_connection;
}

static inline
IPv4_Address *get_p_ipv4__pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager) {
    return &p_tcp_socket_manager
        ->ipv4__pending_connection;
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
    p_tcp_socket_manager
        ->p_PLATFORM_tcp_socket__pending_connection = 0;
    p_tcp_socket_manager->quantity_of__connections = 0;
}

TCP_Socket *allocate_tcp_socket_from__tcp_socket_manager(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid_of__tcp_socket__u32) {
    TCP_Socket *p_tcp_socket =
        (TCP_Socket*)dehash_identitier_u32_in__contigious_array(
                (Serialization_Header*)&p_tcp_socket_manager
                    ->tcp_sockets, 
                MAX_QUANTITY_OF__TCP_SOCKETS, 
                uuid_of__tcp_socket__u32);

    if (!p_tcp_socket)
        return 0;

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

    p_tcp_socket_manager->quantity_of__connections++;

    return p_tcp_socket;
}

TCP_Socket *accept_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32) {
    TCP_Socket *p_tcp_socket =
        allocate_tcp_socket_from__tcp_socket_manager(
                p_tcp_socket_manager, 
                uuid_of__tcp_socket__u32);

    initialize_tcp_socket(
            p_tcp_socket, 
            ipv4_address, 
            uuid_of__tcp_socket__u32);

    p_tcp_socket->p_PLATFORM_tcp_socket = p_PLATFORM_tcp_socket;

    return p_tcp_socket;
}

TCP_Socket *open_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        IPv4_Address ipv4_address,
        Identifier__u32 uuid_of__tcp_socket__u32) {
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        PLATFORM_tcp_connect(
                get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
                    p_tcp_socket_manager), 
                &ipv4_address);

    if (!p_PLATFORM_tcp_socket) {
        debug_error("open_socket_on__tcp_socket_manager__ipv4, failed to open socket.");
        return 0;
    }

    TCP_Socket *p_tcp_socket =
        allocate_tcp_socket_from__tcp_socket_manager(
                p_tcp_socket_manager, 
                uuid_of__tcp_socket__u32);

    initialize_tcp_socket(
            p_tcp_socket, 
            ipv4_address, 
            uuid_of__tcp_socket__u32);

    p_tcp_socket->p_PLATFORM_tcp_socket = p_PLATFORM_tcp_socket;

    return p_tcp_socket;
}

TCP_Socket *open_server_socket_on__tcp_socket_manager__ipv4(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid_of__tcp_socket__u32,
        Index__u16 port) {
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        PLATFORM_tcp_server(
                get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
                    p_tcp_socket_manager),
                port);

    if (!p_PLATFORM_tcp_socket) {
        debug_error("open_server_socket_on__tcp_socket_manager__ipv4, failed to open socket.");
        return 0;
    }

    TCP_Socket *p_tcp_socket =
        allocate_tcp_socket_from__tcp_socket_manager(
                p_tcp_socket_manager, 
                uuid_of__tcp_socket__u32);

    // TODO: server init
    // initialize_tcp_socket(
    //         p_tcp_socket, 
    //         ipv4_address, 
    //         uuid_of__tcp_socket__u32);

    initialize_serialization_header(
            &p_tcp_socket->_serialization_header, 
            uuid_of__tcp_socket__u32, 
            sizeof(TCP_Socket));
    memset(&p_tcp_socket->queue_of__tcp_packet,
            0,
            sizeof(TCP_Packet)
            * MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET);
    p_tcp_socket->index_of__enqueue_begin = 0;
    p_tcp_socket->index_of__enqueue_end = 
        MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET - 1;
    
    // TODO: to here.

    p_tcp_socket->p_PLATFORM_tcp_socket = p_PLATFORM_tcp_socket;

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

    p_tcp_socket_manager->quantity_of__connections--;
}

PLATFORM_TCP_Socket *poll_tcp_socket_manager_for__pending_connections(
        TCP_Socket_Manager *p_tcp_socket_manager,
        TCP_Socket *p_tcp_socket__server,
        IPv4_Address *p_ipv4) {
    if (get_quantity_of__active_tcp_sockets(
                p_tcp_socket_manager)
            >= MAX_QUANTITY_OF__TCP_SOCKETS) {
        return 0;
    }

    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__pending_connection =
        get_p_PLATFORM_tcp_socket__pending_connection(
                p_tcp_socket_manager);

    if (p_PLATFORM_tcp_socket__pending_connection) {
        if (p_ipv4) {
            *p_ipv4 =
                *get_p_ipv4__pending_connection(p_tcp_socket_manager);
        }
        return p_PLATFORM_tcp_socket__pending_connection;
    }

    p_tcp_socket_manager->p_PLATFORM_tcp_socket__pending_connection =
        PLATFORM_tcp_poll_accept(
                get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
                    p_tcp_socket_manager), 
                get_p_PLATFORM_tcp_socket_from__tcp_socket(
                    p_tcp_socket__server),
                get_p_ipv4__pending_connection(p_tcp_socket_manager));
    if (p_ipv4) {
        *p_ipv4 =
            *get_p_ipv4__pending_connection(p_tcp_socket_manager);
    }
    return get_p_PLATFORM_tcp_socket__pending_connection(
            p_tcp_socket_manager);
}

void reject_pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager) {
    PLATFORM_tcp_close_socket(
            get_p_PLATFORM_tcp_context_from__tcp_socket_manager(
                p_tcp_socket_manager), 
            get_p_PLATFORM_tcp_socket__pending_connection(
                p_tcp_socket_manager));
    p_tcp_socket_manager->p_PLATFORM_tcp_socket__pending_connection = 0;
}

TCP_Socket *accept_pending_connection(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Identifier__u32 uuid__u32) {
    TCP_Socket *p_tcp_socket =
        accept_socket_on__tcp_socket_manager__ipv4(
                p_tcp_socket_manager, 
                get_p_PLATFORM_tcp_socket__pending_connection(
                    p_tcp_socket_manager), 
                *get_p_ipv4__pending_connection(
                    p_tcp_socket_manager), 
                uuid__u32);
    if (!p_tcp_socket) {
        debug_error("accept_pending_connection, p_tcp_socket == 0.");
        return 0;
    }
    p_tcp_socket_manager->p_PLATFORM_tcp_socket__pending_connection = 0;
    return p_tcp_socket;
}
