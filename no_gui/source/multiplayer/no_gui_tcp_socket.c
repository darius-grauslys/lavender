#include "multiplayer/no_gui_tcp_socket.h"

void NO_GUI_initialize_PLATFORM_tcp_socket(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u32 socket_handle) {
    p_PLATFORM_tcp_socket->socket_handle = socket_handle;
}
