#include "rendering/opengl/gl_render_world.h"
#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "numerics.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "rendering/aliased_texture_manager.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window_manager.h"
#include "rendering/opengl/gl_chunk_texture_manager.h"
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
#include "vectors.h"
#include "world/camera.h"
#include "world/chunk.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/local_space.h"
#include "world/local_space_manager.h"
#include "world/tile_vectors.h"
#include "world/world.h"
#include "sdl_defines.h"

void GL_compose_chunk(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        Local_Space *p_local_space,
        Texture *array_of__textures,
        Texture *array_of__sample_textures,
        Quantity__u32 quantity_of__gfx_windows,
        f_Tile_Render_Kernel f_tile_render_kernel) {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context);

    GL_Shader_2D *p_GL_shader__passthrough =
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context),
                shader_string__passthrough);

    if (!p_GL_shader__passthrough) {
        debug_warning("Did you forget to attach a passthrough shader?");
        debug_error("SDL::GL::GL_update_chunk, p_GL_chunk_texture_manager has p_GL_shader__passthrough == 0.");
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

    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                p_PLATFORM_gfx_context);

    float clear_color[4];
    glGetFloatv(GL_COLOR_CLEAR_VALUE, clear_color);

    glClearColor(1.0f, 0.0f, 1.0f, 0.0f);

    for (Index__u32 index_of__gfx_window = 0;
            index_of__gfx_window
            < quantity_of__gfx_windows;
            index_of__gfx_window++) {
        GL_Framebuffer *p_GL_framebuffer =
            GL_get_p_chunk_texture_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context)
            ->p_GL_framebuffer__chunk_compose;
        GL_push_framebuffer_onto__framebuffer_manager(
                p_GL_framebuffer_manager,
                p_GL_framebuffer);
        GL_bind_texture_to__framebuffer(
                p_GL_framebuffer, 
                array_of__textures[index_of__gfx_window]
                .p_PLATFORM_texture);
        glClear(GL_COLOR_BUFFER_BIT);
        GL_pop_framebuffer_off_of__framebuffer_manager(
                p_GL_framebuffer_manager);
    }

    glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3]);

    use_shader_2d(
            p_GL_shader__passthrough);

    // TODO: magic numbers
    Vector__3i32F4 chunk_pos_in__world__3i32f4 =
        chunk_vector_3i32_to__vector_3i32F4(
                p_local_space->global_space__vector__3i32);

    chunk_pos_in__world__3i32f4.x__i32F4 += 
        i32_to__i32F4(BIT(LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT) >> 1);
    chunk_pos_in__world__3i32f4.y__i32F4 += 
        i32_to__i32F4(BIT(LOCAL_SPACE__WIDTH_AND__HEIGHT_IN__PIXELS__BIT_SHIFT) >> 1);
    chunk_pos_in__world__3i32f4.z__i32F4 -= 0b0100;

    Camera *p_camera =
        p_ptr_array_of__gfx_windows[0]
        ->p_camera;

    i32 index_of__z_tile = (ARITHMETRIC_R_SHIFT(
            i32F4_to__i32(p_camera->position.z__i32F4),
            TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)
            + ((p_camera->position.z__i32F4 < 0) ? -1 : 0))
            & MASK(CHUNK__DEPTH__BIT_SHIFT);

    GL_Framebuffer *p_GL_framebuffer__chunk_compose =
        GL_get_p_chunk_texture_manager_from__gfx_context(
                p_gfx_context)
        ->p_GL_framebuffer__chunk_compose;
    GL_push_framebuffer_onto__framebuffer_manager(
            p_GL_framebuffer_manager, 
            p_GL_framebuffer__chunk_compose);

    for (Index__u8 index_of__y_tile = 0;
            index_of__y_tile < CHUNK__HEIGHT;
            index_of__y_tile++) {
        for (Index__u8 index_of__x_tile = 0;
                index_of__x_tile < CHUNK__WIDTH;
                index_of__x_tile++) {

            f_tile_render_kernel(
                    p_local_space,
                    tile_render_kernel_results,
                    quantity_of__gfx_windows,
                    index_of__x_tile,
                    index_of__y_tile,
                    index_of__z_tile);

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

                GL_bind_texture_to__framebuffer(
                        p_GL_framebuffer__chunk_compose, 
                        array_of__textures[index_of__gfx_window]
                        .p_PLATFORM_texture);

                GL_push_viewport(
                        p_GL_viewport_stack, 
                        index_of__x_tile
                        * TILE__WIDTH_AND__HEIGHT_IN__PIXELS, 
                        index_of__y_tile
                        * TILE__WIDTH_AND__HEIGHT_IN__PIXELS, 
                        TILE__WIDTH_AND__HEIGHT_IN__PIXELS,
                        TILE__WIDTH_AND__HEIGHT_IN__PIXELS);

                Tile_Vector__3i32 tile_vector__3i32 =
                    get_tile_vector(
                            index_of__x_tile, 
                            index_of__y_tile, 
                            index_of__z_tile);
                Vector__3i32F4 tile_pos_in__world__3i32F4 =
                    add_vectors__3i32F4(
                            chunk_pos_in__world__3i32f4, 
                            tile_vector_3i32_to__vector_3i32F4(tile_vector__3i32));
                
                PLATFORM_use_texture(
                        p_PLATFORM_gfx_context, 
                        array_of__sample_textures[
                            index_of__gfx_window]);

                float index_x, index_y;
                float width, height;
                float flip_x, flip_y;

                Quantity__u32 tilesheet__width_in__tiles =
                    array_of__sample_textures[
                    index_of__gfx_window]
                        .p_PLATFORM_texture
                        ->width
                        / TILE__WIDTH_AND__HEIGHT_IN__PIXELS;

                Quantity__u32 tilesheet__height_in__tiles =
                    array_of__sample_textures[
                    index_of__gfx_window]
                        .p_PLATFORM_texture
                        ->height
                        / TILE__WIDTH_AND__HEIGHT_IN__PIXELS;

                index_x =
                    tile_render_kernel_results[index_of__gfx_window]
                        .index_of__texture % tilesheet__width_in__tiles;
                index_y =
                    (int)(tile_render_kernel_results[
                            index_of__gfx_window]
                        .index_of__texture 
                        / (int)tilesheet__width_in__tiles);

                width =
                    (1.0f / (int)tilesheet__width_in__tiles) - 0.00005f;
                height =
                    (1.0f / (int)tilesheet__height_in__tiles) - 0.00005f;

                GL_render_with__shader__passthrough_using__index_sampling(
                        p_GL_shader__passthrough, 
                        index_x, 
                        index_y, 
                        width, 
                        height, 
                        p_tile_render_kernel_result
                        ->is_flipped__y, 
                        p_tile_render_kernel_result
                        ->is_flipped__x); // TODO: x,y flips are backwards

                GL_pop_viewport(
                        p_GL_viewport_stack);
            }
        }
    }
    GL_pop_framebuffer_off_of__framebuffer_manager(
            p_GL_framebuffer_manager);
}

void GL_compose_world(
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Gfx_Context *p_gfx_context = 
        get_p_gfx_context_from__game(p_game);

    Graphics_Window_Manager *p_graphics_window_manager =
        get_p_graphics_window_manager_from__gfx_context(
                get_p_gfx_context_from__game(p_game));

    Local_Space_Manager *p_local_space_manager =
        get_p_local_space_manager_from__client(
                get_p_local_client_by__from__game(p_game));

    f_Tile_Render_Kernel f_tile_render_kernel =
        get_f_tile_render_kernel_of__world(get_p_world_from__game(p_game));

    Quantity__u32 quantity_of__child_windows = 0;
    Index__u32 index_of__graphics_window_in_ptr_array = 
        get_index_in_ptr_array_of__gfx_window_and__quantity_of__descendants(
                p_graphics_window_manager, 
                p_graphics_window, 
                &quantity_of__child_windows);
    if (index_of__graphics_window_in_ptr_array
            == MAX_QUANTITY_OF__GRAPHICS_WINDOWS) {
        debug_abort("GL::GL_compose_world, could not find graphics window in manager pointer array.");
        return;
    }

    Graphics_Window **p_ptr_array_of__gfx_windows =
        &p_graphics_window_manager
        ->ptr_array_of__sorted_graphic_windows[
            index_of__graphics_window_in_ptr_array];

    Camera *p_camera =
        p_ptr_array_of__gfx_windows[0]
        ->p_camera;

    Texture array_of__sample_textures[quantity_of__child_windows + 1];
    for (Index__u32 subindex_of__gfx_window 
            = 0;
            subindex_of__gfx_window
            <= quantity_of__child_windows;
            subindex_of__gfx_window++) {
        Graphics_Window *p_graphics_window =
            p_ptr_array_of__gfx_windows[subindex_of__gfx_window];
        get_texture_by__uuid(
                get_p_aliased_texture_manager_from__gfx_context(
                    p_gfx_context), 
                p_graphics_window
                ->tile_map__texture__uuid, 
                &array_of__sample_textures[
                    subindex_of__gfx_window]);
    }

    Chunk_Vector__3i32 chunk_vector__3i32 =
        vector_3i32F4_to__chunk_vector_3i32(
                get_position_3i32F4_of__camera(
                    p_camera));

    Local_Space *p_local_space__north_west =
        p_local_space_manager
        ->p_local_space__north_west;
    chunk_vector__3i32.x__i32 = 
        p_local_space__north_west
        ->p_local_space__south
        ->p_local_space__east
        ->global_space__vector__3i32
        .x__i32
        ;
    chunk_vector__3i32.y__i32 = 
        p_local_space__north_west
        ->p_local_space__south
        ->p_local_space__east
        ->global_space__vector__3i32
        .y__i32
        ;

    Local_Space *p_local_space__begin =
        get_p_local_space_from__local_space_manager(
                p_local_space_manager, 
                chunk_vector__3i32);
    Local_Space *p_local_space__current =
        p_local_space__begin;
    if (!p_local_space__current) {
        return;
    }
    Local_Space *p_local_space__current_sub;

    float clear_color[4];
    glGetFloatv(GL_COLOR_CLEAR_VALUE, clear_color);

    glClearColor(1.0f, 0.0f, 1.0f, 0.0f);

    GL_Framebuffer_Manager *p_GL_framebuffer_manager =
        GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context));

    for (Index__u32 subindex_of__gfx_window 
            = 0;
            subindex_of__gfx_window
            <= quantity_of__child_windows;
            subindex_of__gfx_window++) {
        Graphics_Window *p_gfx_window =
            p_ptr_array_of__gfx_windows[
                subindex_of__gfx_window];
        GL_Framebuffer *p_GL_framebuffer =
            (GL_Framebuffer*)p_gfx_window
            ->p_PLATFORM_gfx_window
            ->p_SDL_graphics_window__data;
        GL_push_framebuffer_onto__framebuffer_manager(
                p_GL_framebuffer_manager,
                p_GL_framebuffer);
        GL_bind_texture_to__framebuffer(
                p_GL_framebuffer, 
                p_gfx_window
                ->p_PLATFORM_gfx_window
                ->SDL_graphics_window__texture
                .p_PLATFORM_texture);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        GL_pop_framebuffer_off_of__framebuffer_manager(
                p_GL_framebuffer_manager);
    }
    glClearColor(
            clear_color[0],
            clear_color[1],
            clear_color[2],
            clear_color[3]);

    GL_Viewport_Stack *p_GL_viewport_stack =
        GL_get_p_viewport_stack_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context));

    GL_Shader_2D *p_GL_shader__chunk =
        GL_get_shader_from__shader_manager(
                GL_get_p_shader_manager_from__PLATFORM_gfx_context(
                    get_p_PLATFORM_gfx_context_from__gfx_context(
                        p_gfx_context)),
                shader_string__chunk);
    GL_Gfx_Sub_Context *p_GL_gfx_sub_context =
        GL_get_p_gfx_sub_context_from__PLATFORM_gfx_context(
                get_p_PLATFORM_gfx_context_from__gfx_context(
                    p_gfx_context));
    use_vertex_object(
            &p_GL_gfx_sub_context
            ->GL_vertex_object__unit_square);
    
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
            if (!is_local_space__active(
                        p_local_space__current_sub)) {
                goto next_local_space;
            }
            Texture array_of__textures[GL_MAX_QUANTITY_OF__CHUNK_TEXTURES];
            bool is_local_space_with__chunk = 
                get_p_chunk_from__local_space(
                        p_local_space__current_sub);
            bool is_chunk__needing_graphics_update = false;
            if (GL_poll_textures_for__chunk_in__chunk_texture_manager(
                        p_gfx_context, 
                        p_ptr_array_of__gfx_windows, 
                        GL_get_p_chunk_texture_manager_from__PLATFORM_gfx_context(
                            get_p_PLATFORM_gfx_context_from__gfx_context(
                                p_gfx_context)),
                        p_local_space__current_sub, 
                        array_of__textures,
                        &is_chunk__needing_graphics_update)) {
                // TODO: error handle here.
                debug_error("SDL::GL_compose_world, error polling chunk textures.");
                continue;
            }
            if (is_local_space_with__chunk
                    && (is_chunk__needing_graphics_update
                    || (is_chunk__visually_updated(
                        get_p_chunk_from__local_space(
                            p_local_space__current_sub))
                        || is_global_space__dirty( // TODO: two source of truth, chunk dirty, and global dirty
                            get_p_global_space_from__local_space(p_local_space__current_sub))))) {
                GL_compose_chunk(
                        p_gfx_context, 
                        p_ptr_array_of__gfx_windows, 
                        p_local_space__current_sub, 
                        array_of__textures, 
                        array_of__sample_textures, 
                        quantity_of__child_windows + 1,  // including parent!
                        f_tile_render_kernel);
                set_chunk_as__visually_committed( // TODO change dog shit name
                        get_p_chunk_from__local_space(
                            p_local_space__current_sub));
                set_global_space_as__NOT_dirty(
                        get_p_global_space_from__local_space(
                            p_local_space__current_sub));
            }

            use_shader_2d(p_GL_shader__chunk);

            Vector__3i32F4 chunk_pos_in__world__3i32f4 =
                chunk_vector_3i32_to__vector_3i32F4(
                        p_local_space__current_sub
                        ->p_global_space
                        ->chunk_vector__3i32);

            for (Index__u16 subindex_of__gfx_window 
                    = 0;
                    subindex_of__gfx_window 
                    <= quantity_of__child_windows;
                    subindex_of__gfx_window++) {
                PLATFORM_use_texture(
                        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context),
                        array_of__textures[subindex_of__gfx_window]);

                GL_Framebuffer *p_GL_framebuffer =
                    (GL_Framebuffer*)p_ptr_array_of__gfx_windows[
                        subindex_of__gfx_window]
                    ->p_PLATFORM_gfx_window
                    ->p_SDL_graphics_window__data;
                GL_push_framebuffer_onto__framebuffer_manager(
                        p_GL_framebuffer_manager, 
                        p_GL_framebuffer);
                GL_bind_texture_to__framebuffer(
                        p_GL_framebuffer, 
                        p_ptr_array_of__gfx_windows[
                            subindex_of__gfx_window]
                        ->p_PLATFORM_gfx_window
                        ->SDL_graphics_window__texture
                        .p_PLATFORM_texture);

                GL_link_data_to__shader(
                        get_p_PLATFORM_gfx_context_from__gfx_context(
                            p_gfx_context), 
                        p_GL_shader__chunk, 
                        p_camera, 
                        add_vectors__3i32F4(
                            chunk_pos_in__world__3i32f4,
                            get_vector__3i32F4_using__i32(
                                ((CHUNK__WIDTH << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT) >> 1)
                                - (TILE__WIDTH_AND__HEIGHT_IN__PIXELS >> 1),
                                + (((CHUNK__HEIGHT << TILE__WIDTH_AND__HEIGHT__BIT_SHIFT) >> 1)
                                - (TILE__WIDTH_AND__HEIGHT_IN__PIXELS >> 1)),
                                0)),
                        (0b1000
                        << (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT - 3))
                        << CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT);

                GL_push_viewport(
                        p_GL_viewport_stack, 
                        0,
                        0,
                        p_ptr_array_of__gfx_windows[
                            subindex_of__gfx_window]
                        ->p_PLATFORM_gfx_window
                        ->SDL_graphics_window__texture
                        .p_PLATFORM_texture
                        ->width,
                        p_ptr_array_of__gfx_windows[
                            subindex_of__gfx_window]
                        ->p_PLATFORM_gfx_window
                        ->SDL_graphics_window__texture
                        .p_PLATFORM_texture
                        ->height);

                glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, 0);

                GL_pop_viewport(
                        p_GL_viewport_stack);

                GL_pop_framebuffer_off_of__framebuffer_manager(
                        p_GL_framebuffer_manager);
            }

next_local_space:
            p_local_space__current_sub =
                p_local_space__current_sub->p_local_space__east;
        }
        p_local_space__current =
            p_local_space__current->p_local_space__south;
    }
}
