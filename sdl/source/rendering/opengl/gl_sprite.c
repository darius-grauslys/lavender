#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "numerics.h"
#include "platform.h"
#include "rendering/gfx_context.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer.h"
#include "rendering/opengl/gl_framebuffer_manager.h"
#include "rendering/opengl/gl_numerics.h"
#include "rendering/opengl/gl_shader.h"
#include "rendering/opengl/gl_shader_manager.h"
#include "rendering/opengl/gl_shader_passthrough.h"
#include "rendering/opengl/gl_shader_sprite.h"
#include "rendering/opengl/gl_vertex_object.h"
#include "rendering/opengl/gl_viewport.h"
#include "rendering/opengl/glad/glad.h"
#include "rendering/sprite.h"
#include "types/implemented/graphics_window_kind.h"
#include "vectors.h"
#include <rendering/opengl/gl_sprite.h>
#include <rendering/opengl/gl_gfx_sub_context.h>
#include <sdl_defines.h>

void GL_initialize_sprite(
        Gfx_Context *p_gfx_context,
        PLATFORM_Sprite *p_PLATFORM_sprite,
        Quantity__u32 width,
        Quantity__u32 height) {
    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .p_SDL_gfx_sub_context
        ;
    GL_Sprite *p_GL_sprite =
        (GL_Sprite*)p_PLATFORM_sprite
        ->p_SDL_sprite
        ;
    initialize_vertex_object(
            &p_GL_sprite->GL_vertex_object,
            width,
            height);
}

void GL_update_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite *p_sprite) {
    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context));
    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context));
    GL_Framebuffer *p_GL_framebuffer =
        (GL_Framebuffer*)p_gfx_window
        ->p_PLATFORM_gfx_window
        ->p_SDL_graphics_window__data
        ;
    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                p_gfx_context
                ->p_PLATFORM_gfx_context);
    GL_Shader_2D *p_GL_shader__passthrough=
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    get_p_PLATFORM_gfx_context_from__gfx_context(
                        p_gfx_context)), 
                shader_string__passthrough);
    GL_push_framebuffer_onto__framebuffer_manager(
            p_GL_framebuffer_manager,
            p_GL_framebuffer);
    GL_bind_texture_to__framebuffer(
            p_GL_framebuffer, 
            p_sprite
            ->p_PLATFORM_texture_of__sprite
            );

    float clear_color[4];
    glGetFloatv(GL_COLOR_CLEAR_VALUE, clear_color);

    glClearColor(1.0, 0.0, 1.0, 0.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3]);

    use_shader_2d(
            p_GL_shader__passthrough);
    use_vertex_object(&p_GL_gfx_sub_context->GL_vertex_object__unit_square);
    PLATFORM_use_texture(
            p_gfx_context
            ->p_PLATFORM_gfx_context,
            p_sprite
            ->p_PLATFORM_texture_for__sprite_to__sample);

    float width__f = 
        (float)((float)p_sprite
                ->p_PLATFORM_texture_for__sprite_to__sample
        ->width
        / p_sprite
        ->p_PLATFORM_texture_of__sprite
        ->width);
        ;
    float height__f = 
        (float)((float)p_sprite
                ->p_PLATFORM_texture_for__sprite_to__sample
        ->height
        / p_sprite
        ->p_PLATFORM_texture_of__sprite
        ->height);
        ;

    float width_of__uv  = 1.0 / (width__f);
    float height_of__uv = 1.0 / (height__f);

    u32 quantity_of__sprite_frame__columns = 
        p_sprite
        ->p_PLATFORM_texture_for__sprite_to__sample
        ->width
        / p_sprite
        ->p_PLATFORM_texture_of__sprite
        ->width;
    u32 quantity_of__sprite_frame__rows =
        p_sprite
        ->p_PLATFORM_texture_for__sprite_to__sample
        ->height
        / p_sprite
        ->p_PLATFORM_texture_of__sprite
        ->height;

    Index__u16 sprite__index_of__frame = 0;
    // TODO: add Texture type, and re-implement animation groups.
    // if (p_sprite->animation_group
    //         .quantity_of__columns_in__sprite_animation_group__u4
    //         != 0) {
    //     Index__u16 sprite__index_of__frame__x =
    //         (p_sprite->index_of__sprite_frame
    //          % p_sprite->animation_group
    //          .quantity_of__columns_in__sprite_animation_group__u4)
    //         + (p_sprite->animation_group
    //                 .quantity_of__columns_in__sprite_animation_group__u4
    //                 * p_sprite->index_of__sprite_animation_sub_group__u8)
    //         ;
    //     Index__u16 sprite__index_of__frame__y =
    //         (p_sprite->index_of__sprite_frame
    //          / p_sprite->animation_group
    //          .quantity_of__columns_in__sprite_animation_group__u4)
    //         ;

    //     sprite__index_of__frame =
    //         (sprite__index_of__frame__x
    //         % quantity_of__sprite_frame__columns)
    //         + (p_sprite->animation_group
    //                 .quantity_of__rows_in__sprite_animation_group__u4
    //             * quantity_of__sprite_frame__columns
    //                 * (sprite__index_of__frame__x
    //                     / (p_sprite->animation_group
    //                         .quantity_of__rows_in__sprite_animation_group__u4
    //                         * quantity_of__sprite_frame__columns)))
    //         + (quantity_of__sprite_frame__columns
    //                 * sprite__index_of__frame__y)
    //         ;
    // } else {
        sprite__index_of__frame =
            p_sprite->index_of__sprite_frame;
    // }

    Index__u8 index_of__frame__column =
        sprite__index_of__frame
        % quantity_of__sprite_frame__columns;
    Index__u8 index_of__frame__row =
        sprite__index_of__frame
        / quantity_of__sprite_frame__columns;

    GL_push_viewport(
            p_GL_viewport_stack, 
            0, 0,
            p_sprite
            ->p_PLATFORM_texture_of__sprite
            ->width,
            p_sprite
            ->p_PLATFORM_texture_of__sprite
            ->height);

    glDisable(GL_DEPTH_TEST);
    GL_render_with__shader__passthrough_using__index_sampling(
            p_GL_shader__passthrough, 
            index_of__frame__column,
            index_of__frame__row,
            width_of__uv, 
            height_of__uv,
            false,
            false);
    glEnable(GL_DEPTH_TEST);

    GL_pop_viewport(p_GL_viewport_stack);
    GL_pop_framebuffer_off_of__framebuffer_manager(
            p_GL_framebuffer_manager);

    set_sprite_as__NOT_needing_graphics_update(p_sprite);
}

void GL_release_sprite_vertext_object(
        GL_Sprite *p_GL_sprite) {
    release_vertex_object(
            &p_GL_sprite->GL_vertex_object);
}

GL_Sprite *GL_get_p_sprite_from__PLATFORM_sprite(
        PLATFORM_Sprite *p_PLATFORM_sprite) {
    return (GL_Sprite*)
        p_PLATFORM_sprite
        ->p_SDL_sprite
        ;
}

GL_Sprite *GL_get_p_sprite_from__sprite(
        Sprite *p_sprite) {
    return (GL_Sprite*)
        p_sprite
        ->p_PLATFORM_sprite
        ->p_SDL_sprite
        ;
}

void GL_render_sprite(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite *p_sprite,
        Vector__3i32F4 position__3i32F4) {
    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context));
    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context));
    PLATFORM_Sprite *p_PLATFORM_sprite =
        p_sprite
        ->p_PLATFORM_sprite
        ;
    GL_Shader_2D *p_GL_shader__sprite =
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    get_p_PLATFORM_gfx_context_from__gfx_context(
                        p_gfx_context)), 
                shader_string__sprite);

    Camera *p_SDL_camera__active =
        p_gfx_window
        ->p_camera;

    GL_Framebuffer *p_GL_framebuffer =
        (GL_Framebuffer*)p_gfx_window
        ->p_PLATFORM_gfx_window
        ->p_SDL_graphics_window__data
        ;
    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                p_gfx_context
                ->p_PLATFORM_gfx_context);

    if (is_sprite__needing_graphics_update(
                p_sprite)) {
        GL_update_sprite(
                p_gfx_context, 
                p_gfx_window, 
                p_sprite);
    }

    GL_push_viewport(
            p_GL_viewport_stack, 
            0, 0,
            p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__texture
            ->width,
            p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__texture
            ->height);

    GL_push_framebuffer_onto__framebuffer_manager(
            p_GL_framebuffer_manager,
            p_GL_framebuffer);
    GL_bind_texture_to__framebuffer(
            p_GL_framebuffer, 
            p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__texture
            );

    use_shader_2d(p_GL_shader__sprite);
    GL_link_data_to__shader(
            p_gfx_context
            ->p_PLATFORM_gfx_context,
            p_GL_shader__sprite, 
            p_SDL_camera__active, 
            position__3i32F4,
            0b1000
            << (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT - 3));

    use_vertex_object(
            &((GL_Sprite*)p_PLATFORM_sprite
            ->p_SDL_sprite)
            ->GL_vertex_object);
    PLATFORM_use_texture(
            p_gfx_context
            ->p_PLATFORM_gfx_context,
            p_sprite
            ->p_PLATFORM_texture_of__sprite);
    glUniform2f(
            p_GL_shader__sprite
            ->location_of__general_uniform_0,
            0, 0
            );
    glUniform2f(
            p_GL_shader__sprite
            ->location_of__general_uniform_1,
            1.0, 1.0
            );
    glUniform2f(
            p_GL_shader__sprite
            ->location_of__general_uniform_2,
            is_sprite__flipped_x(p_sprite),
            is_sprite__flipped_y(p_sprite));
    glDisable(GL_DEPTH_TEST);
    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
    glEnable(GL_DEPTH_TEST);

    GL_pop_viewport(p_GL_viewport_stack);
    GL_pop_framebuffer_off_of__framebuffer_manager(
            p_GL_framebuffer_manager);
}
