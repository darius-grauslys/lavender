#include "multiplayer/no_gui_tcp_context.h"
#include "debug/debug.h"
#include "defines_weak.h"
#include "game.h"
#include "multiplayer/no_gui_tcp_socket.h"
#include "platform.h"
#include "platform_defaults.h"

#include <asm-generic/errno-base.h>
#include <asm-generic/errno.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/fcntl.h>
#include <netinet/in.h>
#include <errno.h>
#include <unistd.h>

static inline
PLATFORM_TCP_Socket *get_p_PLATFORM_tcp_socket_by__index_from__context(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        Index__u32 index_of__PLATFORM_tcp_socket) {
#ifndef NDEBUG
    if (index_of__PLATFORM_tcp_socket >
            MAX_QUANTITY_OF__TCP_SOCKETS) {
        debug_error("NO_GUI::get_p_PLATFORM_tcp_socket_by__index_from__context, index out of bounds, %d/%d", index_of__PLATFORM_tcp_socket, MAX_QUANTITY_OF__TCP_SOCKETS);
        return 0;
    }
#endif
    return &p_PLATFORM_tcp_context->PLATFORM_tcp_sockets[
        index_of__PLATFORM_tcp_socket];
}

void NO_GUI_initialize_PLATFORM_tcp_context(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context) {
    memset(p_PLATFORM_tcp_context,
            0,
            sizeof(PLATFORM_TCP_Context));
}

PLATFORM_TCP_Context *PLATFORM_tcp_begin(
        Game *p_game) {
    PLATFORM_TCP_Context *pM_PLATFORM_tcp_context =
        malloc(sizeof(PLATFORM_TCP_Context));
    if (!pM_PLATFORM_tcp_context) {
        debug_error("NO_GUI::PLATFORM_tcp_being, failed to allocate pM_PLATFORM_tcp_context.");
        return 0;
    }
    NO_GUI_initialize_PLATFORM_tcp_context(
            pM_PLATFORM_tcp_context);

    return pM_PLATFORM_tcp_context;
}

void PLATFORM_tcp_end(
        Game *p_game) {
    if (!p_game->pM_tcp_socket_manager)
        return;

    PLATFORM_TCP_Context *p_PLATFORM_tcp_context =
        get_p_PLATFORM_tcp_context_from__game(p_game);

    p_game->pM_tcp_socket_manager->p_PLATFORM_tcp_context = 0;

    free(p_PLATFORM_tcp_context);
}

PLATFORM_TCP_Socket *NO_GUI_allocate_PLATFORM_TCP_Socket_from__context(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context) {
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__available = 0;
    for (Index__u32 index_of__PLATFORM_tcp_socket = 0;
            index_of__PLATFORM_tcp_socket
            < MAX_QUANTITY_OF__TCP_SOCKETS;
            index_of__PLATFORM_tcp_socket++) {
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__current =
            get_p_PLATFORM_tcp_socket_by__index_from__context(
                    p_PLATFORM_tcp_context, 
                    index_of__PLATFORM_tcp_socket);

        if (NO_GUI_is_PLATFORM_tcp_socket__in_use(
                    p_PLATFORM_tcp_socket__current)) {
            continue;
        }

        p_PLATFORM_tcp_socket__available =
            p_PLATFORM_tcp_socket__current;
        break;
    }

    if (!p_PLATFORM_tcp_socket__available) {
        debug_error("NO_GUI_allocate_PLATFORM_TCP_Socket_from__context, too many active connections.");
        return 0;
    }

    u32 socket_handle =
        socket(PF_INET, SOCK_STREAM, 0);

    if (socket_handle == (u32)-1) {
        debug_error("NO_GUI_allocate_PLATFORM_TCP_Socket_from__context, failed to acquire socket.");
        return 0;
    }

    NO_GUI_initialize_PLATFORM_tcp_socket(
            p_PLATFORM_tcp_socket__available, 
            socket_handle);

    return p_PLATFORM_tcp_socket__available;
}

///
/// Returns null if failed to connect.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_connect(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        IPv4_Address *p_ipv4_address) {
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        NO_GUI_allocate_PLATFORM_TCP_Socket_from__context(
                p_PLATFORM_tcp_context);

    if (!p_PLATFORM_tcp_socket) {
        debug_error("NO_GUI::PLATFORM_tcp_connect, failed to get socket.");
        return 0;
    }

    struct sockaddr_in *p_addr_in =
        &p_PLATFORM_tcp_socket->addr_in;
    p_addr_in->sin_family = AF_INET;
    p_addr_in->sin_addr.s_addr =
        htonl(
                (p_ipv4_address->ip_bytes[0] << 24)
                | (p_ipv4_address->ip_bytes[1] << 16)
                | (p_ipv4_address->ip_bytes[2] << 8)
                | (p_ipv4_address->ip_bytes[3])
                );
    p_addr_in->sin_port = 
        htons(p_ipv4_address->port);

    int flags = 
        fcntl(p_PLATFORM_tcp_socket->socket_handle,
                F_GETFL,
                0);
    if (flags == -1 
            || fcntl(p_PLATFORM_tcp_socket->socket_handle,
                F_SETFL,
                flags | O_NONBLOCK) == -1) {
        debug_error("NO_GUI::PLATFORM_tcp_connect, failed to set non-blocking mode.");
        if (close(p_PLATFORM_tcp_socket->socket_handle)) {
            debug_error("NO_GUI::PLATFORM_tcp_connect, failed to close socket.");
            return 0;
        }
        NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive(
                p_PLATFORM_tcp_socket);
        return 0;
    }

    debug_info("NO_GUI::PLATFORM_tcp_connect: %d.%d.%d.%d:%hu",
            p_ipv4_address->ip_bytes[0],
            p_ipv4_address->ip_bytes[1],
            p_ipv4_address->ip_bytes[2],
            p_ipv4_address->ip_bytes[3],
            p_ipv4_address->port
            );

    return p_PLATFORM_tcp_socket;
}

TCP_Socket_State PLATFORM_tcp_poll_connect(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    if (connect(p_PLATFORM_tcp_socket->socket_handle,
                (struct sockaddr*)&p_PLATFORM_tcp_socket->addr_in,
                sizeof(struct sockaddr_in))) {
        switch (errno) {
            case EWOULDBLOCK:
            case EINPROGRESS:
                return TCP_Socket_State__Connecting;
            default:
                debug_error("NO_GUI::PLATFORM_tcp_connect, failed to connect.");
                return TCP_Socket_State__Disconnected;
        }
    }

    debug_info("NO_GUI::PLATFORM_tcp_poll_connect, connection succeeded.");
    return TCP_Socket_State__Connected;
}

///
/// Use to make a PLATFORM_TCP_Socket for accepting
/// server connections.
/// Returns null if failed.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_server(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        Index__u16 port) {
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket =
        NO_GUI_allocate_PLATFORM_TCP_Socket_from__context(
                p_PLATFORM_tcp_context);

    if (!p_PLATFORM_tcp_socket) {
        debug_error("NO_GUI::PLATFORM_tcp_server, failed to get socket.");
        return 0;
    }

    struct sockaddr_in addr_in;
    memset(&addr_in, 0, sizeof(addr_in));
    addr_in.sin_port = htons(port);
    addr_in.sin_addr.s_addr = htonl(INADDR_ANY);
    addr_in.sin_family = AF_INET;
    
    int flags = 
        fcntl(p_PLATFORM_tcp_socket->socket_handle,
                F_GETFL,
                0);
    if (flags == -1 
            || fcntl(p_PLATFORM_tcp_socket->socket_handle,
                F_SETFL,
                flags | O_NONBLOCK) == -1) {
        debug_error("NO_GUI::PLATFORM_tcp_server, failed to set non-blocking mode.");
        if (close(p_PLATFORM_tcp_socket->socket_handle)) {
            debug_error("NO_GUI::PLATFORM_tcp_server, failed to close socket.");
            return 0;
        }
        NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive(
                p_PLATFORM_tcp_socket);
        return 0;
    }

    if (bind(p_PLATFORM_tcp_socket->socket_handle,
                (struct sockaddr*)&addr_in,
                sizeof(addr_in))) {
        PLATFORM_tcp_close_socket(
                p_PLATFORM_tcp_context, 
                p_PLATFORM_tcp_socket);
        return 0;
    }

    if (listen(p_PLATFORM_tcp_socket->socket_handle,
                MAX_QUANTITY_OF__TCP_SOCKETS - 1)) {
        debug_error("NO_GUI::PLATFORM_tcp_server, failed to listen.");
        return 0;
    }

    debug_info("NO_GUI::PLATFORM_tcp_server, listening...");

    return p_PLATFORM_tcp_socket;
}

///
/// Returns true if the socket was closed.
///
bool PLATFORM_tcp_close_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    if (close(p_PLATFORM_tcp_socket->socket_handle)) {
        debug_error("NO_GUI::PLATFORM_tcp_close_socket, failed to close socket.");
        return false;
    }
    NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive(
            p_PLATFORM_tcp_socket);

    return true;
}

///
/// Checks for new connections, and returns a
/// PLATFORM_TCP_Socket if one is found.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_poll_accept(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__server,
        IPv4_Address *p_ipv4) {
    struct sockaddr_in addr_in;
    socklen_t socket_length;
    errno = 0;
    int socket_handle__new_connection =
        accept(p_PLATFORM_tcp_socket__server->socket_handle,
                (struct sockaddr*)&addr_in,
                &socket_length);

    if (socket_handle__new_connection == -1) {
        if (errno != EWOULDBLOCK && errno != EAGAIN) {
            debug_error("NO_GUI::PLATFORM_tcp_poll_accept, error.");
            return 0;
        }
        return 0;
    }

    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__pending_connection =
        NO_GUI_allocate_PLATFORM_TCP_Socket_from__context(
                p_PLATFORM_tcp_context);

    if (!p_PLATFORM_tcp_socket__pending_connection) {
        close(socket_handle__new_connection);
        debug_error("NO_GUI::PLATFORM_tcp_poll_accept, cannot accept new connections.");
        return 0;
    }

    if (p_ipv4) {
        u32 ipv4_addr__u32 = ntohl(addr_in.sin_addr.s_addr);
        p_ipv4->port = ntohs(addr_in.sin_port);

        p_ipv4->ip_bytes[0] =
            (ipv4_addr__u32 >> 24) & MASK(8);
        p_ipv4->ip_bytes[1] =
            (ipv4_addr__u32 >> 16) & MASK(8);
        p_ipv4->ip_bytes[2] =
            (ipv4_addr__u32 >> 8) & MASK(8);
        p_ipv4->ip_bytes[3] =
            (ipv4_addr__u32) & MASK(8);
    }

    NO_GUI_initialize_PLATFORM_tcp_socket(
            p_PLATFORM_tcp_socket__pending_connection,
            socket_handle__new_connection);

    int flags =
        fcntl(p_PLATFORM_tcp_socket__pending_connection->socket_handle,
                F_GETFL,
                0);
    if (flags == -1 
            || fcntl(p_PLATFORM_tcp_socket__pending_connection->socket_handle,
                F_SETFL,
                flags | O_NONBLOCK) == -1) {
        debug_error("NO_GUI::PLATFORM_tcp_connect, failed to set non-blocking mode.");
        if (close(p_PLATFORM_tcp_socket__pending_connection->socket_handle)) {
            debug_error("NO_GUI::PLATFORM_tcp_connect, failed to close socket.");
            return 0;
        }
        NO_GUI_initialize_PLATFORM_tcp_socket_as__inactive(
                p_PLATFORM_tcp_socket__pending_connection);
        return 0;
    }

    return p_PLATFORM_tcp_socket__pending_connection;
}

///
/// Returns number of bytes sent, -1 if error.
///
i32 PLATFORM_tcp_send(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of__bytes) {
    return send(
            p_PLATFORM_tcp_socket->socket_handle,
            p_bytes,
            length_of__bytes,
            0);
}

///
/// Returns number of bytes received.
/// Returns a TCP_ERROR__XXX otherwise.
/// handling a new delivery.
///
i32 PLATFORM_tcp_recieve(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of_bytes_in__destination) {
    errno = 0;
    i32 recieved =
        recv(
                p_PLATFORM_tcp_socket->socket_handle, 
                p_bytes, 
                length_of_bytes_in__destination, 
                0);
    if (recieved == -1) {
        if (errno == EWOULDBLOCK) {
            return 0;
        }
    }
    
    return recieved;
}
