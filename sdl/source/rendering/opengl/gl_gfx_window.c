#include "rendering/opengl/gl_gfx_window.h"
#include "defines.h"
#include "platform_defines.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/opengl/gl_gfx_sub_context.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer.h"
#include "rendering/opengl/gl_framebuffer_manager.h"
#include "rendering/opengl/gl_gfx_sub_context.h"
#include "rendering/opengl/gl_shader.h"
#include "rendering/opengl/gl_shader_manager.h"
#include "rendering/opengl/gl_shader_passthrough.h"
#include "rendering/opengl/gl_vertex_object.h"
#include "rendering/opengl/gl_viewport.h"
#include "rendering/opengl/glad/glad.h"
#include "rendering/sdl_gfx_context.h"
#include "rendering/sdl_gfx_window.h"
#include "rendering/sdl_render_world.h"
#include "rendering/sdl_texture_manager.h"
#include "rendering/texture.h"
#include "rendering/sdl_texture.h"
#include "serialization/serialization_header.h"
#include "ui/ui_manager.h"
#include "vectors.h"

void GL_allocate_gfx_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window,
        Texture_Flags texture_flags) {
    p_PLATFORM_graphics_window
        ->p_SDL_graphics_window__texture =
            PLATFORM_allocate_texture(
                    p_PLATFORM_gfx_context,
                    p_PLATFORM_graphics_window,
                    texture_flags);

    if (IS_DEALLOCATED_P(
                p_PLATFORM_graphics_window
                ->p_SDL_graphics_window__texture)) {
        debug_error("SDL::GL::GL_allocate_gfx_window, failed to allocate texture.");
        return;
    }

    GL_Framebuffer *p_GL_framebuffer =
        GL_allocate_framebuffer_with__depth_buffer_from__framebuffer_manager(
                p_PLATFORM_gfx_context, 
                GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context),
                texture_flags);

    if (!p_GL_framebuffer) {
        PLATFORM_release_texture(
                p_PLATFORM_gfx_context, 
                p_PLATFORM_graphics_window
                ->p_SDL_graphics_window__texture);
        debug_error("SDL::GL::GL_allocate_gfx_window, failed to allocate framebuffer");
        return;
    }

    p_PLATFORM_graphics_window
        ->p_SDL_graphics_window__data =
        p_GL_framebuffer
        ;

    SDL_set_gfx_window_as__allocated(
            p_PLATFORM_graphics_window);
}

void GL_compose_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {

    if (!is_graphics_window__enabled(p_gfx_window))
        return;

    GL_Framebuffer *p_GL_framebuffer =
        (GL_Framebuffer*)p_gfx_window
        ->p_PLATFORM_gfx_window
        ->p_SDL_graphics_window__data;

    if (!p_GL_framebuffer) {
        debug_error("SDL::GL::GL_compose_gfx_window, missing framebuffer.");
        set_graphics_window_as__disabled(p_gfx_window);
        debug_warning("p_gfx_window disabled.");
        return;
    }

    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context);
     
    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context);

    GL_Shader_2D *p_GL_shader__passthrough=
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context), 
                shader_string__passthrough);

    if (!p_GL_shader__passthrough) {
        debug_error("SDL::GL::GL_compose_gfx_window, p_GL_shader__passthrough == 0.");
        set_graphics_window_as__disabled(p_gfx_window);
        debug_warning("p_gfx_window disabled.");
        return;
    }

    UI_Tile_Map__Wrapper ui_tile_map__wrapper =
        p_gfx_window->ui_tile_map__wrapper;

    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context);

    PLATFORM_Texture *p_PLATFORM_texture__ui_tilesheet =
        get_p_PLATFORM_texture_by__uuid(
                get_p_aliased_texture_manager_from__gfx_context(
                    p_gfx_context), 
                get_uuid_of__ui_tile_map__texture_from__gfx_window(
                    p_gfx_window));

    if (!p_PLATFORM_texture__ui_tilesheet) {
        debug_error("SDL::GL::GL_compose_gfx_window, p_PLATFORM_texture__ui_tilesheet == 0.");
        set_graphics_window_as__disabled(p_gfx_window);
        debug_warning("p_gfx_window disabled.");
        return;
    }

    GL_push_framebuffer_onto__framebuffer_manager(
            p_GL_framebuffer_manager,
            p_GL_framebuffer);
    GL_bind_texture_to__framebuffer(
            p_GL_framebuffer, 
            p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__texture);

    float clear_color[4];
    glGetFloatv(GL_COLOR_CLEAR_VALUE, clear_color);

    glClearColor(1.0, 0.0, 1.0, 0.0);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3]);

    GL_Vertex_Object *p_GL_vertex_object =
        &GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context)
        ->GL_vertex_object__unit_square;

    use_shader_2d(
            p_GL_shader__passthrough);

    float width__f = 
        (float)(p_PLATFORM_texture__ui_tilesheet
        ->width
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT);
        ;
    float height__f = 
        (float)(p_PLATFORM_texture__ui_tilesheet
        ->height
        >> UI_TILE__WIDTH_AND__HEIGHT__BIT_SHIFT);
        ;

    float width_of__uv  = 1.0 / (width__f);
    float height_of__uv = 1.0 / (height__f);

    use_vertex_object(p_GL_vertex_object);

    PLATFORM_use_texture(
            p_PLATFORM_gfx_context, 
            p_PLATFORM_texture__ui_tilesheet);

    for (Index__u8 index_of__y_tile = 0;
            index_of__y_tile 
            < ui_tile_map__wrapper.height_of__ui_tile_map;
            index_of__y_tile++) {
        for (Index__u8 index_of__x_tile = 0;
                index_of__x_tile 
                < ui_tile_map__wrapper.width_of__ui_tile_map;
                index_of__x_tile++) {
            UI_Tile_Raw ui_tile_raw =
                ui_tile_map__wrapper
                .p_ui_tile_data[
                index_of__x_tile
                    + (ui_tile_map__wrapper.width_of__ui_tile_map 
                            - 1 - index_of__y_tile) 
                    * ui_tile_map__wrapper.width_of__ui_tile_map];
            if (!ui_tile_raw)
                continue;
            ui_tile_raw--;

            GL_push_viewport(
                    p_GL_viewport_stack, 
                    index_of__x_tile * UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS, 
                    index_of__y_tile * UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS, 
                    UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS, 
                    UI_TILE__WIDTH_AND__HEIGHT_IN__PIXELS);

            GL_render_with__shader__passthrough_using__index_sampling(
                    p_GL_shader__passthrough, 
                    ui_tile_raw % 32, 
                    (int)(ui_tile_raw / 32), 
                    width_of__uv, 
                    height_of__uv,
                    false,
                    false);

            GL_pop_viewport(p_GL_viewport_stack);
        }
    }

    GL_pop_framebuffer_off_of__framebuffer_manager(
            p_GL_framebuffer_manager);
}

void GL_render_gfx_window(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window) {

    if (!is_graphics_window__enabled(p_gfx_window))
        return;

    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context);

    GL_Shader_2D *p_GL_shader__graphics_window =
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context),
                shader_string__graphics_window);

    if (!p_GL_shader__graphics_window) {
        debug_error("SDL::GL::GL_render_gfx_window, p_GL_shader__graphics_window == 0.");
        set_graphics_window_as__disabled(p_gfx_window);
        debug_warning("p_gfx_window disabled.");
        return;
    }

    PLATFORM_Graphics_Window *p_PLATFORM_graphics_window =
        p_gfx_window->p_PLATFORM_gfx_window;

    use_vertex_object(
            &GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context)
            ->GL_vertex_object__unit_square);

    use_shader_2d(p_GL_shader__graphics_window);
    PLATFORM_use_texture(
            p_PLATFORM_gfx_context,
            p_PLATFORM_graphics_window
            ->p_SDL_graphics_window__texture);

    float width_of__uv = 1.0f;
    float height_of__uv = 1.0f;

    float x = 0, y = 0;

    if (!GL_is_viewport_stack__only_the_base(
                GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context))) {
        GL_Viewport *p_GL_viewport =
            GL_peek_viewport_stack(
                    GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                        p_PLATFORM_gfx_context));

        x = 
            (p_PLATFORM_graphics_window
                ->p_SDL_graphics_window__texture
                ->width / 2.0f)
            + (subtract_u32__clamped(
                    p_GL_viewport->width,
                    p_PLATFORM_graphics_window
                    ->p_SDL_graphics_window__texture
                    ->width,
                    0) / 2.0f)
            + p_GL_viewport->x
            ;
        y = 
            (p_PLATFORM_graphics_window
                ->p_SDL_graphics_window__texture
                ->height / 2.0f)
            + (subtract_u32__clamped(
                    p_GL_viewport->height,
                    p_PLATFORM_graphics_window
                    ->p_SDL_graphics_window__texture
                    ->height,
                    0) / 2.0f)
            + p_GL_viewport->y
            ;
    }

    GL_link_data_to__shader_with__scale(
            get_p_PLATFORM_gfx_context_from__gfx_context(
                p_gfx_context), 
            p_GL_shader__graphics_window, 
            0, 
            vector_3i32_to__vector_3i32F4(
                get_position_3i32_of__graphics_window(
                    p_gfx_window)),
            CAMERA_FULCRUM__WIDTH,
            CAMERA_FULCRUM__HEIGHT);

    glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);
}

void GL_release_gfx_window(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        PLATFORM_Graphics_Window *p_PLATFORM_graphics_window) {
    PLATFORM_release_texture(
            p_PLATFORM_gfx_context, 
            p_PLATFORM_graphics_window
            ->p_SDL_graphics_window__texture);

    GL_Framebuffer *p_GL_framebuffer =
        (GL_Framebuffer*)p_PLATFORM_graphics_window
        ->p_SDL_graphics_window__data
        ;

    if (!p_GL_framebuffer) {
        return;
    }

    p_PLATFORM_graphics_window
        ->p_SDL_graphics_window__data = 0;

    GL_release_framebuffer_from__framebuffer_manager(
            p_PLATFORM_gfx_context, 
            GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context), 
            p_GL_framebuffer);

    SDL_set_gfx_window_as__deallocated(
            p_PLATFORM_graphics_window);
}

