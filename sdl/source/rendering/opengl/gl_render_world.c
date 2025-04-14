#include "rendering/opengl/gl_render_world.h"
#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer.h"
#include "rendering/opengl/gl_gfx_sub_context.h"
#include "rendering/opengl/gl_shader.h"
#include "rendering/opengl/gl_shader_manager.h"
#include "rendering/opengl/gl_vertex_object.h"
#include "rendering/opengl/gl_viewport.h"
#include "vectors.h"
#include "world/global_space.h"
#include "world/local_space.h"
#include "world/world.h"
#include "sdl_defines.h"

void GL_compose_chunk(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space *p_local_space,
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context);

    GL_Shader_2D *p_GL_shader__chunk =
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context),
                shader_string__chunk);

    if (!p_GL_shader__chunk) {
        debug_warning("Did you forget to attach a chunk shader?");
        debug_error("SDL::GL::GL_update_chunk, p_GL_chunk_texture_manager has p_GL_shader__chunk == 0.");
        return;
    }

    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context);

    Tile_Render_Kernel_Result tile_render_kernel_results[
        quantity_of__gfx_windows];

    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context);

    use_shader_2d(
            p_GL_shader__chunk);
    use_vertex_object(
            &p_GL_gfx_sub_context
            ->GL_vertex_object__unit_square);

    // TODO: magic numbers
    Vector__3i32F4 chunk_pos_in__world__3i32f4 =
        vector_3i32_to__vector_3i32F4(
                p_local_space->global_space__vector__3i32);

    chunk_pos_in__world__3i32f4.x__i32F4 *= 1<<6;
    chunk_pos_in__world__3i32f4.y__i32F4 *= 1<<6;
    // chunk_pos_in__world__3i32f4.x__i32F4 += i32_to__i32F4(32);
    // chunk_pos_in__world__3i32f4.y__i32F4 += i32_to__i32F4(28);
    chunk_pos_in__world__3i32f4.z__i32F4 = 
        i32_to__i32F4(10);

    for (Index__u8 index_of__y_tile = 0;
            index_of__y_tile < CHUNK_WIDTH__IN_TILES;
            index_of__y_tile++) {
        for (Index__u8 index_of__x_tile = 0;
                index_of__x_tile < CHUNK_WIDTH__IN_TILES;
                index_of__x_tile++) {

            f_tile_render_kernel(
                    p_local_space,
                    tile_render_kernel_results,
                    quantity_of__gfx_windows,
                    index_of__x_tile,
                    index_of__y_tile,
                    0);

            for (Index__u32 index_of__gfx_window = 0;
                    index_of__gfx_window
                    < quantity_of__gfx_windows;
                    index_of__gfx_window++) {
                Tile_Render_Kernel_Result *p_tile_render_kernel_result =
                    &tile_render_kernel_results[index_of__gfx_window];
                
                if (!p_tile_render_kernel_result->index_of__texture) {
                    continue;
                }
                p_tile_render_kernel_result->index_of__texture--;

                Graphics_Window *p_gfx_window =
                    p_ptr_array_of__gfx_windows[
                        index_of__gfx_window];

                GL_Framebuffer *p_GL_framebuffer =
                    (GL_Framebuffer*)p_gfx_window
                    ->p_PLATFORM_gfx_window
                    ->p_SDL_graphics_window__data;
                GL_use_framebuffer_as__target(
                        p_GL_framebuffer);
                GL_bind_texture_to__framebuffer(
                        p_GL_framebuffer, 
                        p_gfx_window
                        ->p_PLATFORM_gfx_window
                        ->p_SDL_graphics_window__texture);

                GL_push_viewport(
                        p_GL_viewport_stack, 
                        0, 
                        0, 
                        p_gfx_window
                        ->p_PLATFORM_gfx_window
                        ->p_SDL_graphics_window__texture
                        ->width, 
                        p_gfx_window
                        ->p_PLATFORM_gfx_window
                        ->p_SDL_graphics_window__texture
                        ->height);

                Camera *p_camera =
                    p_gfx_window
                    ->p_camera;

                Vector__3i32F4 tile_pos_in__world__3i32F4 =
                    add_vectors__3i32F4(
                            chunk_pos_in__world__3i32f4, 
                            get_vector__3i32F4_using__i32(
                                index_of__x_tile << 3, 
                                index_of__y_tile << 3, 
                                0));

                GL_link_data_to__shader(
                        p_PLATFORM_gfx_context,
                        p_GL_shader__chunk,
                        p_camera,
                        tile_pos_in__world__3i32F4,
                        0b1000);
                
                PLATFORM_use_texture(
                        p_PLATFORM_gfx_context, 
                        p_ptr_array_of__PLATFORM_textures[
                            index_of__gfx_window]);

                float index_x, index_y;
                float width, height;
                float flip_x, flip_y;

                index_x =
                    tile_render_kernel_results[index_of__gfx_window]
                        .index_of__texture % TILE_SHEET_WIDTH__IN_TILES;
                index_y =
                    (int)(TILE_SHEET_WIDTH__IN_TILES-1)
                        - (int)(tile_render_kernel_results[
                                index_of__gfx_window]
                            .index_of__texture 
                            / (int)TILE_SHEET_WIDTH__IN_TILES);

                glUniform2f(
                        p_GL_shader__chunk
                            ->location_of__general_uniform_0,
                        index_x,
                        index_y
                        );
                width =
                    1.0f / (int)TILE_SHEET_WIDTH__IN_TILES;
                height =
                    1.0f / (int)TILE_SHEET_WIDTH__IN_TILES;
                glUniform2f(
                        p_GL_shader__chunk
                            ->location_of__general_uniform_1,
                        width,
                        height);
                glUniform2f(
                        p_GL_shader__chunk
                            ->location_of__general_uniform_2,
                        tile_render_kernel_results[
                            index_of__gfx_window]
                            .is_flipped__y
                        ? 1.0
                        : 0.0, 
                        0.0);

                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);

                GL_pop_viewport(
                        p_GL_viewport_stack);

                GL_unbind_framebuffer();
            }
            // break;
        }
        // break;
    }
}

void GL_compose_world(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space_Manager *p_local_space_manager,
        PLATFORM_Texture **p_ptr_array_of__PLATFORM_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {

    // debug_error("GL_compose_world, impl");

    Local_Space *p_local_space__current =
        p_local_space_manager->p_local_space__north_west;
    Local_Space *p_local_space__current_sub;

    float clear_color[4];
    glGetFloatv(GL_COLOR_CLEAR_VALUE, clear_color);

    glClearColor(1.0f, 0.0f, 1.0f, 0.0f);
    for (Index__u32 index_of__gfx_window = 0;
            index_of__gfx_window
            < quantity_of__gfx_windows;
            index_of__gfx_window++) {
        Graphics_Window *p_gfx_window =
            p_ptr_array_of__gfx_windows[
                index_of__gfx_window];
        GL_Framebuffer *p_GL_framebuffer =
            (GL_Framebuffer*)p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__data;
        GL_use_framebuffer_as__target(
                p_GL_framebuffer);
        GL_bind_texture_to__framebuffer(
                p_GL_framebuffer, 
                p_gfx_window
                ->p_PLATFORM_gfx_window
                ->p_SDL_graphics_window__texture);
        glClear(GL_COLOR_BUFFER_BIT);
    }
    glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3]);

    for (uint8_t y=0; 
            y 
            < GFX_CONTEXT__RENDERING_HEIGHT__IN_CHUNKS;
            y++) {
        p_local_space__current_sub =
            p_local_space__current;
        for (uint8_t x=0; 
                x 
                < GFX_CONTEXT__RENDERING_WIDTH__IN_CHUNKS;
                x++) {
#warning TODO: TODO: why does this segfault
            // TODO: this causes seg fault
            // if (!is_local_space__active(
            //             p_local_space__current)) {
            //     continue;
            // }
            GL_compose_chunk(
                    p_gfx_context, 
                    p_ptr_array_of__gfx_windows, 
                    p_local_space__current_sub, 
                    p_ptr_array_of__PLATFORM_textures, 
                    quantity_of__gfx_windows, 
                    f_tile_render_kernel);

            p_local_space__current_sub =
                p_local_space__current_sub->p_local_space__east;
            // break;
        }
        p_local_space__current =
            p_local_space__current->p_local_space__south;
        // break;
    }
}
