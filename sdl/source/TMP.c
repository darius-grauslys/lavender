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
#include "platform_defines.h"
#include "rendering/sdl_gfx_window.h"
#include "sdl_defines.h"
#include "rendering/texture.h"

///
/// SECTION_audio
///

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
    return false;
}

///
/// SECTION_game_actions
///

void m_PLATFORM_game_action_handler_for__multiplayer(
        Game *p_this_game,
        Game_Action *p_game_action) {}

///
/// SECTION_rendering
///

PLATFORM_Graphics_Window 
*PLATFORM_get_p_graphics_window_with__graphics_window_kind(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        enum Graphics_Window_Kind the_kind_of__graphics_window,
        Identifier__u32 identifier_of__graphics_window) {
    return 0;
}

Sprite_Flags *PLATFORM_get_p_sprite_flags__from_PLATFORM_sprite(
        PLATFORM_Sprite *p_PLATFORM_sprite) {
    return 0;
}

void PLATFORM_release_all__sprites(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {}

void PLATFORM_release_all__sprites_using__this_graphics_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window) {}

void PLATFORM_update_sprite_gfx__to_current_frame(
        Sprite *sprite) {}

void PLATFORM_update_sprite(
        PLATFORM_Sprite *p_PLATFORM_sprite) {}

void PLATFORM_set_sprite__position(
        PLATFORM_Sprite *p_PLATFORM_sprite,
        Index__u16 x, Index__u16 y) {}

Quantity__u32 PLATFORM_get_quantity_of__allocated_sprites(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {
    return 0;
}

Quantity__u32 PLATFORM_get_max_quantity_of__allocated_sprites(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context) {
    return 0;
}

///
/// On NDS, this will init both main and sub.
///
void PLATFORM_initialize_rendering__menu(PLATFORM_Gfx_Context *gfx_context) {}

void PLATFORM_allocate_texture__with_size(PLATFORM_Texture *texture, 
        Texture_Flags flags,
        uint32_t width, uint32_t height) {}

Texture_Flags *PLATFORM_get_p_texture_flags_from__PLATFORM_texture(
        PLATFORM_Texture *texture) { return 0;}

Quantity__u32 PLATFORM_get_max_quantity_of__allocations_for__texture_flags(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return 0;
}

Quantity__u32 PLATFORM_get_quantity_of__available_allocations_for__texture_flags(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return 0;
}

bool PLATFORM_has_support_for__texture_flag__render_method(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        Texture_Flags texture_flags) {
    return false;
}

///
/// SECTION_world
///

///
/// SECTION_core
///

// int abs(int x) {}
// void srand(unsigned int seed) {}
// int rand(void) {}

/// 
/// SECTION_ui
///

///
/// SECTION_scene
///

///
/// SECTION_serialization
///

///
/// SECTION_input
///

///
/// SECTION_inventory
///

///
/// SECTION_log
///
bool PLATFORM_update_log__global(Game *p_game) { return false; }
bool PLATFORM_update_log__local(Game *p_game) { return false; }
bool PLATFORM_update_log__system(Game *p_game) { return false; }

bool PLATFORM_clear_log__global(Game *p_game) { return false; }
bool PLATFORM_clear_log__local(Game *p_game) { return false; }
bool PLATFORM_clear_log__system(Game *p_game) { return false; }

///
/// SECTION_multiplayer
///

