#include "rendering/opengl/gl_typer.h"
#include "collisions/hitbox_aabb.h"
#include "defines_weak.h"
#include "rendering/font/typer.h"
#include "rendering/gfx_context.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer.h"
#include "rendering/opengl/gl_framebuffer_manager.h"
#include "rendering/opengl/gl_gfx_sub_context.h"
#include "rendering/opengl/gl_shader_manager.h"
#include "rendering/opengl/gl_shader_passthrough.h"
#include "rendering/opengl/gl_texture.h"
#include "rendering/opengl/gl_vertex_object.h"
#include "rendering/opengl/gl_viewport.h"

static void GL_put_char_in__typer_for__texture(
        Gfx_Context *p_gfx_context,
        PLATFORM_Texture *p_PLATFORM_texture,
        Typer *p_typer,
        unsigned char letter) {

    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context));

    GL_Shader_2D *p_GL_shader__passthrough=
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context)), 
                shader_string__passthrough);

    if (!p_GL_shader__passthrough) {
        debug_error("SDL::GL::GL_put_char_in__typer_for__texture, p_GL_shader__passthrough == 0.");
        return;
    }

    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context));

    Font_Letter *p_font_letter =
        get_p_font_letter_from__typer(
                p_typer, 
                letter);

    float width__f = 
        (float)p_typer
        ->p_font
        ->p_PLATFORM_texture_of__font
        ->width
        / p_font_letter
            ->width_of__font_letter
        ;
    float height__f = 
        (float)p_typer
        ->p_font
        ->p_PLATFORM_texture_of__font
        ->height
        / p_font_letter
            ->height_of__font_letter
        ;

    float width_of__uv  = 1.0f / (width__f);
    float height_of__uv = 1.0f / (height__f);

    use_shader_2d(
            p_GL_shader__passthrough);

    use_vertex_object(
            &p_GL_gfx_sub_context
            ->GL_vertex_object__unit_square);

    GL_use_texture(
            p_typer->p_font->p_PLATFORM_texture_of__font);

    float max_width__f = 
        (float)p_typer
        ->p_font
        ->p_PLATFORM_texture_of__font
        ->width
        / p_typer
            ->p_font
            ->max_width_of__font_letter
        ;
    float max_height__f = 
        (float)p_typer
        ->p_font
        ->p_PLATFORM_texture_of__font
        ->height
        / p_typer
            ->p_font
            ->max_height_of__font_letter
        ;

    float x__uv = 
        (p_font_letter->index_of__character__in_font
         & MASK(5))
        * (1.0f / max_width__f);
    float y__uv =
        (p_font_letter->index_of__character__in_font
         >> 5)
        * (1.0f / max_height__f);

    GL_push_viewport(
            p_GL_viewport_stack, 
            get_x_i32_from__hitbox(
                &p_typer->text_bounding_box)
            + p_typer->cursor_position__3i32.x__i32
            + p_font_letter->x__offset_of__font_letter
            - (get_width_u32_of__hitbox_aabb(
                    &p_typer->text_bounding_box) >> 1),
            get_y_i32_from__hitbox(
                &p_typer->text_bounding_box)
            - p_typer->cursor_position__3i32.y__i32
            - p_font_letter->y__offset_of__font_letter
            - p_typer->p_font->max_height_of__font_letter
            + (get_height_u32_of__hitbox_aabb(
                    &p_typer->text_bounding_box) >> 1),
            p_font_letter->width_of__font_letter, 
            p_font_letter->height_of__font_letter);

    glDisable(GL_DEPTH_TEST);

    GL_render_with__shader__passthrough_using__coordinate_sampling(
            p_GL_shader__passthrough, 
            x__uv, y__uv,
            width_of__uv, 
            height_of__uv,
            false,
            false);

    glEnable(GL_DEPTH_TEST);

    GL_pop_viewport(p_GL_viewport_stack);
}

void GL_put_char_in__typer(
        Gfx_Context *p_gfx_context,
        Typer *p_typer,
        unsigned char letter) {

    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context));

    GL_Framebuffer *p_GL_framebuffer;

    if (is_typer_targetting__PLATFORM_texture(p_typer)) {

        p_GL_framebuffer =
            &p_GL_framebuffer_manager
            ->GL_framebuffer__post_processing;

        GL_push_framebuffer_onto__framebuffer_manager(
                p_GL_framebuffer_manager,
                p_GL_framebuffer);
        GL_bind_texture_to__framebuffer(
                p_GL_framebuffer, 
                p_typer->p_PLATFORM_texture__typer_target);

        GL_put_char_in__typer_for__texture(
                p_gfx_context, 
                p_typer->p_PLATFORM_texture__typer_target,
                p_typer, 
                letter);

        GL_pop_framebuffer_off_of__framebuffer_manager(
                p_GL_framebuffer_manager);
        return;
    }

    PLATFORM_Graphics_Window *p_PLATFORM_graphics_window =
        p_typer->p_PLATFORM_graphics_window__typer_target;

    p_GL_framebuffer =
        p_PLATFORM_graphics_window
        ->p_SDL_graphics_window__data;

    GL_push_framebuffer_onto__framebuffer_manager(
            p_GL_framebuffer_manager,
            p_GL_framebuffer);
    GL_bind_texture_to__framebuffer(
            p_GL_framebuffer, 
            p_PLATFORM_graphics_window
            ->p_SDL_graphics_window__texture);

    GL_put_char_in__typer_for__texture(
            p_gfx_context, 
            p_typer
            ->p_PLATFORM_graphics_window__typer_target
            ->p_SDL_graphics_window__texture,
            p_typer, 
            letter);

    GL_pop_framebuffer_off_of__framebuffer_manager(
            p_GL_framebuffer_manager);
}
