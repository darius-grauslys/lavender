#ifndef GL_SPRITE_MANAGER_H
#define GL_SPRITE_MANAGER_H

#include <rendering/opengl/gl_defines.h>

void GL_initialize_sprite_manager(
        GL_Sprite_Manager *p_GL_sprite_manager);

GL_Sprite *GL_allocate_sprite_with__sprite_manager(
        GL_Sprite_Manager *p_GL_sprite_manager);

void GL_allocate_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_graphics_window,
        Sprite *p_sprite,
        Quantity__u32 width,
        Quantity__u32 height);

void GL_release_sprite_from__sprite_manager(
        GL_Sprite_Manager *p_GL_sprite_manager,
        GL_Sprite *p_GL_sprite);

void GL_release_sprite(
        Gfx_Context *p_gfx_context,
        PLATFORM_Sprite *p_PLATFORM_sprite);

void GL_dispose_sprite_manager(
        GL_Sprite_Manager *p_GL_sprite_manager);

#endif
