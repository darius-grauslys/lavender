///
/// !!THIS FILE IS TO BE REMOVED COMPLETELY IN THE FUTURE!!
///

///
/// We are temporarily storing platform specific definitions here.
/// Specifically those which are not yet implemented in the SDL
/// backend.
///

#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/texture.h"

void PLATFORM_initialize_audio(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {}

/// 
/// Returns false if fails to allocate audio effect.
///
Audio_Effect *PLATFORM_allocate_audio_effect(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {
    return 0;
}

void PLATFORM_play_audio_effect(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context,
        Audio_Effect *p_audio_effect) {}

void PLATFORM_poll_audio_effects(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {}

void PLATFORM_play_audio__stream(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context,
        enum Audio_Stream_Kind the_kind_of__audio_stream) {}

bool PLATFORM_is_audio__streaming(
        PLATFORM_Audio_Context *p_PLATFORM_audio_context) {
    return 0;
}

///
/// SECTION_debug
///

void PLATFORM_coredump(void) {}
void PLATFORM_pre_abort(void) {}
void PLATFORM_abort(void) {}

///
/// SECTION_entity
///
// TODO: remove
void PLATFORM_render_entity(
        Entity *entity,
        Game *game) {}

///
/// SECTION_game_actions
///

// TODO: remove, make PLATFORM_tcp PLATFORM_udp
void m_PLATFORM_game_action_handler_for__multiplayer(
        Game *p_this_game,
        Game_Action *p_game_action) {}

///
/// SECTION_rendering
///

void PLATFORM_put_char_in__typer(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Typer *p_typer,
        unsigned char letter) {}

PLATFORM_Sprite *PLATFORM_allocate_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        PLATFORM_Texture *p_PLATFORM_texture_to__sample_by__sprite,
        Texture_Flags texture_flags_for__sprite) {
    return 0;
}


void PLATFORM_release_sprite(
        Gfx_Context *p_gfx_context,
        PLATFORM_Sprite *p_PLATFORM_sprite) {}

void PLATFORM_release_all__sprites(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {}

// TODO: use wrapper types
void PLATFORM_render_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite_Wrapper *sprite,
        Vector__3i32F4 position_of__sprite__3i32F4) {}

// TODO: remove
void PLATFORM_update_sprite_gfx__to_current_frame(
        Sprite_Wrapper *sprite_wrapper) {}

void PLATFORM_update_sprite(
        PLATFORM_Sprite *p_PLATFORM_sprite) {}

/// 
/// On NDS, this will init both main and sub.
///
// TODO: remove
void PLATFORM_initialize_rendering__game(PLATFORM_Gfx_Context *gfx_context) {}

void PLATFORM_initialize_gfx_context(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {}

PLATFORM_Texture *PLATFORM_allocate_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags) {
    return 0;
}


PLATFORM_Texture *PLATFORM_allocate_texture_with__path(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        const char *c_str__path) {
    return 0;
}


// TODO: update to take Texture__Wrapper *p_
void PLATFORM_update_texture(
        PLATFORM_Texture *texture) {}

// TODO: remove
void PLATFORM_use_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Texture *texture) {}

void PLATFORM_release_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Texture *texture) {}

// TODO: remove
Texture_Flags *PLATFORM_get_p_texture_flags_from__PLATFORM_texture(
        PLATFORM_Texture *texture) {
    return 0;
}


// TODO: remove
Quantity__u32 PLATFORM_get_max_quantity_of__allocations_for__texture_flags(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return 0;
}


// TODO: remove
Quantity__u32 PLATFORM_get_quantity_of__available_allocations_for__texture_flags(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return 0;
}


// TODO: remove, make a Profile_t struct, and populate
bool PLATFORM_has_support_for__texture_flag__render_method(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return 0;
}


///
/// SECTION_world
///

// TODO: remove
void PLATFORM_render_chunk(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Chunk_Manager__Chunk_Map_Node *p_chunk_map_node) {}

// TODO: remove
void PLATFORM_render_tile(
        PLATFORM_Gfx_Context *context,
        Tile *tile) {}

// TODO: remove
void PLATFORM_update_chunk(
        PLATFORM_Gfx_Context *p_gfx_context,
        Chunk_Manager *p_chunk_manager,
        Chunk_Manager__Chunk_Map_Node *p_chunk_map_node) {}

// TODO: remove
void PLATFORM_update_chunks(
        PLATFORM_Gfx_Context *gfx_context,
        Chunk_Manager *chunk_manager) {}

///
/// SECTION_core
///

i32F20 PLATFORM_get_time_elapsed(
        Timer__u32 *p_timer__seconds__u32,
        Timer__u32 *p_timer__nanoseconds__u32) {
    return 0;
}

int PLATFORM_main(Game *p_game) {
    return 0;
}

void PLATFORM_pre_render(Game *game) {}

void PLATFORM_post_render(Game *game) {}

/// 
/// SECTION_ui
///

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

void PLATFORM_compose_world(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space_Manager *p_local_space_manager,
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {}

void PLATFORM_render_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {}

///
/// SECTION_scene
///

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

/// 
/// SECTION_defines
///
