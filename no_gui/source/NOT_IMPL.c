///
/// This file includes everything from platform.h
/// which is NOT implemented.
///

#include "defines.h"

void PLATFORM_pre_render(Game *p_game) {}
void PLATFORM_post_render(Game *p_game) {}

void PLATFORM_compose_world(
        Gfx_Context *p_gfx_context, 
        Graphics_Window **p_ptr_array_of__gfx_windows, 
        Local_Space_Manager *p_local_space_manager, 
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures, 
        Quantity__u32 quantity_of__gfx_windows, 
        f_Tile_Render_Kernel f_tile_render_kernel) {}

PLATFORM_Texture *PLATFORM_allocate_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context, 
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window, 
        Texture_Flags texture_flags) { return 0; }

PLATFORM_Texture *PLATFORM_allocate_texture_with__path(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window,
        Texture_Flags texture_flags,
        const char *c_str__path) { return 0; }

void PLATFORM_release_texture(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Texture *texture) {}

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
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
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
        PLATFORM_Texture *p_PLATFORM_texture_to__sample_by__sprite,
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
        Sprite_Wrapper *sprite,
        Vector__3i32F4 position_of__sprite__3i32F4) {}

void PLATFORM_poll_input(
        Game *p_game,
        Input *p_input) {}
