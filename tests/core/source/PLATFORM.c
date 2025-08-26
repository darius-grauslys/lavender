#ifndef PLATFORM
///
/// This file includes everything from platform.h
/// which is NOT implemented.
///

#include "defines.h"
#include "timer.h"

#ifdef __unix__
#include <stdlib.h>
#include <unistd.h>
#endif

#ifdef _WIN32

void PLATFORM_initialize_time(void) {
    return;
}

///
/// NOTE: Timer value is considered to be u32F20 seconds
///
#include <windows.h>
#include <mmsystem.h>
u32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    DWORD time__old = get_time_elapsed_from__timer_u32(
            p_timer__nanoseconds__u32);
    DWORD time__current = timeGetTime();

    if (time__old == time__current)
        return 0;

    u32 elapsed__miliseconds = 
        subtract_u32__no_overflow(
                time__current,
                time__old);
    if (!elapsed__miliseconds) {
        elapsed__miliseconds =
            time__current
            + (((uint32_t)-1)
                - time__old)
            ;
    }
    
    (void)progress_timer__u32(
                p_timer__nanoseconds__u32, 
                elapsed__miliseconds);

    return 
        ((elapsed__miliseconds
                & MASK(10))
                << 10)
        ;
}
#else

#include <time.h>

struct timespec _NO_GUI_timespec__initial;

void PLATFORM_initialize_time(void) {
    clock_gettime(
            CLOCK_MONOTONIC, 
            &_NO_GUI_timespec__initial);
}

///
/// NOTE: Timer value is considered to be u32F20 seconds
///
u32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    struct timespec timespec__current;
    clock_gettime(
            CLOCK_MONOTONIC, 
            &timespec__current);

    if (timespec__current.tv_nsec < _NO_GUI_timespec__initial.tv_nsec) {
        timespec__current.tv_sec--;
        timespec__current.tv_nsec = 
            _NO_GUI_timespec__initial.tv_nsec
            - timespec__current.tv_nsec;
    } else {
        timespec__current.tv_nsec -= _NO_GUI_timespec__initial.tv_nsec;
    }
    timespec__current.tv_sec = _NO_GUI_timespec__initial.tv_sec;

    u32 elapsed__seconds = 
        subtract_u32__no_overflow(
                timespec__current.tv_sec, 
                get_time_elapsed_from__timer_u32(
                    p_timer__seconds__u32));
    if (!elapsed__seconds) {
        elapsed__seconds=
            timespec__current.tv_sec
            + p_timer__seconds__u32->remaining__u32
            ;
    }

    u32 elapsed__nanoseconds =
        subtract_u32__no_overflow(
                timespec__current.tv_nsec, 
                get_time_elapsed_from__timer_u32(
                    p_timer__nanoseconds__u32));
    if (!elapsed__nanoseconds) {
        elapsed__nanoseconds=
            timespec__current.tv_nsec
            + p_timer__nanoseconds__u32->remaining__u32
            ;
    }

    (void)progress_timer__u32(
                p_timer__seconds__u32, 
                elapsed__seconds);
    if (progress_timer__u32(
                p_timer__nanoseconds__u32, 
                elapsed__nanoseconds)) {
        elapsed__seconds--;
    }

    return 
        (elapsed__seconds << 20)
        + ((elapsed__nanoseconds
                & MASK(30))
                >> 10)
        ;
}

void PLATFORM_get_date_time(Date_Time *p_date_time) {
    time_t time_raw;
    struct tm * p_time_local;

    time(&time_raw);
    p_time_local = localtime(&time_raw);

    p_date_time->seconds =
        p_time_local->tm_sec;
    p_date_time->minutes =
        p_time_local->tm_min;
    p_date_time->hours =
        p_time_local->tm_hour;
    p_date_time->days =
        p_time_local->tm_mday;
    p_date_time->months =
        p_time_local->tm_mon;
    p_date_time->years =
        p_time_local->tm_year;
}

#endif

void PLATFORM_coredump(void) {
#ifdef _WIN32
    // TODO: impl win32
#else
    if(!fork()) abort();
#endif
}

void PLATFORM_pre_abort(void) {
}

void PLATFORM_abort(void) {
    abort();
}

void PLATFORM_pre_render(Game *p_game) {}
void PLATFORM_post_render(Game *p_game) {}

void PLATFORM_compose_world(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space_Manager *p_local_space_manager,
        Texture *ptr_array_of__textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {}

bool PLATFORM_allocate_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        Texture *p_OUT_texture) { return 0; }

bool PLATFORM_allocate_texture_with__path(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        const char *c_str__path,
        Texture *p_OUT_texture) { return 0; }

void PLATFORM_release_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture texture) {}

PLATFORM_Graphics_Window *PLATFORM_allocate_gfx_window(
        Gfx_Context *p_gfx_context,
        Texture_Flags texture_flags_for__gfx_window) {
    return 0;
}

void PLATFORM_release_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window) {}

void PLATFORM_compose_gfx_window(
        Gfx_Context *p_gfx_context, 
        Graphics_Window *p_gfx_window) {}

void PLATFORM_render_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {}

void PLATFORM_put_char_in__typer(
        Gfx_Context *p_gfx_context,
        Typer *p_typer,
        unsigned char letter) {}

void PLATFORM_initialize_audio(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {}
Audio_Effect *PLATFORM_allocate_audio_effect(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) { return 0; }

void PLATFORM_play_audio_effect(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context,
        Audio_Effect *p_audio_effect) {}

void PLATFORM_poll_audio_effects(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {}

void PLATFORM_play_audio__stream(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context,
        enum Audio_Stream_Kind the_kind_of__audio_stream) {}

bool PLATFORM_is_audio__streaming(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) { return false; }

PLATFORM_Sprite *PLATFORM_allocate_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite *p_sprite,
        Texture_Flags texture_flags_for__sprite) { return 0; }

void PLATFORM_release_sprite(
        Gfx_Context *p_gfx_context,
        PLATFORM_Sprite *p_PLATFORM_sprite) {}

void PLATFORM_release_all__sprites(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {}

// TODO: use wrapper types
void PLATFORM_render_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite *sprite,
        Vector__3i32F4 position_of__sprite__3i32F4) {}

///
/// SECTION_serialization
///

void PLATFORM_initialize_file_system_context(
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context) {}

///
/// Returns length of the path
///
Quantity__u32 PLATFORM_get_base_directory(IO_path path) {
    return 0;
}

Quantity__u32 PLATFORM_get_directories(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        IO_path path,
        char *p_directory_name__buffer,
        Quantity__u32 size_of__directory_name__buffer,
        Quantity__u32 max_length_of__directory_name) {
    return 0;
}

int PLATFORM_access(const char *p_c_str, IO_Access_Kind io_access_kind) {
    return 0;
}
PLATFORM_Directory *PLATFORM_opendir(const char *p_c_str) {
    return 0;
}
void PLATFORM_closedir(PLATFORM_Directory *p_dir) {}
bool PLATFORM_mkdir(const char *p_c_str, uint32_t file_code) {
    return false;
}

void PLATFORM_append_base_directory_to__path(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        char *p_c_str_path,
        Index__u32 *p_index_of__path_end) {}

Quantity__u32 PLATFORM_get_quantity_of__active_serialization_requests(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context) {
    return 0;
}

Serialization_Request *PLATFORM_allocate_serialization_request(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context) {
    return 0;
}

void PLATFORM_release_serialization_request(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        Serialization_Request *p_serialization_request) {}

enum PLATFORM_Open_File_Error PLATFORM_open_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        const char *p_path,
        const char *p_flags,
        Serialization_Request *p_serialization_request) {
    return PLATFORM_Open_File_Error__Unknown;
}

void PLATFORM_close_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialization_request) {}

enum PLATFORM_Write_File_Error PLATFORM_write_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        u8 *source,
        Quantity__u32 length_of__data,
        Quantity__u32 quantity_of__writes,
        void *p_file_handler) {
    return PLATFORM_Write_File_Error__Unknown;
}

enum PLATFORM_Read_File_Error PLATFORM_read_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        u8 *destination,
        Quantity__u32 *p_length_of__data_to_read,
        Quantity__u32 quantity_of__reads,
        void *p_file_handler) {
    return PLATFORM_Read_File_Error__Unknown;
}

///
/// Returns -1 on error.
///
Index__u32 PLATFORM_get_position_in__file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        void *p_file_handler) {
    return -1;
}

bool PLATFORM_set_position_in__file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Index__u32 position_in__file_u32,
        void *p_file_handler) {
    return false;
}

///
/// SECTION_input
///
void PLATFORM_poll_input(
        Game *p_game,
        Input *p_input) {}

///
/// SECTION_inventory
///

///
/// SECTION_log
///

///
/// SECTION_multiplayer
///

PLATFORM_TCP_Context *PLATFORM_tcp_begin(
        Game *p_game) {
    return 0;
}

void PLATFORM_tcp_end(
        Game *p_game) {}

///
/// Returns null if failed to connect.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_connect(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        IPv4_Address *p_ipv4_address) {
    return 0;
}

///
/// To be called every loop following PLATFORM_tcp_connect
/// using the returned socket. Returns TCP_Socket_State
/// to describe the connect request status.
///
TCP_Socket_State PLATFORM_tcp_poll_connect(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    return TCP_Socket_State__Unknown;
}

///
/// Use to make a PLATFORM_TCP_Socket for accepting
/// server connections.
/// Returns null if failed.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_server(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        Index__u16 port) {
    return 0;
}

///
/// Returns true if the socket was closed.
///
bool PLATFORM_tcp_close_socket(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket) {
    return false;
}

///
/// Checks for new connections, and returns a
/// PLATFORM_TCP_Socket if one is found.
///
PLATFORM_TCP_Socket *PLATFORM_tcp_poll_accept(
        PLATFORM_TCP_Context *p_PLATFORM_tcp_context,
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__server,
        IPv4_Address *p_ipv4) {
    return 0;
}

///
/// Returns number of bytes sent, -1 if error.
///
i32 PLATFORM_tcp_send(
        PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket,
        u8 *p_bytes,
        Quantity__u32 length_of__bytes) {
    return -1;
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
    return 0;
}
#endif
