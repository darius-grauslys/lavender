#include "rendering/opengl/gl_chunk_texture_manager.h"
#include "defines.h"
#include "rendering/gfx_context.h"
#include "rendering/opengl/gl_defines.h"
#include "defines_weak.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer_manager.h"
#include "world/global_space_manager.h"
#include "world/local_space_manager.h"

static inline
GL_Chunk_Texture_Entry 
*GL_get_p_chunk_texture_entry_by__index_from__chunk_texture_manager(
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Index__u32 index_of__chunk) {
#ifndef NDEBUG
    if (index_of__chunk > LOCAL_SPACE_MANAGER__HEIGHT
            * LOCAL_SPACE_MANAGER__WIDTH) {
        debug_error("SDL::GL_get_p_chunk_texture_entry_by__index_from__chunk_texture_manager, index out of bounds: %d", index_of__chunk);
        return 0;
    }
#endif
    return &p_GL_chunk_texture_manager->GL_chunk_textures_entries[
        index_of__chunk];
}

void GL_initialize_chunk_texture_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager) {
    memset(
            p_GL_chunk_texture_manager, 
            0, 
            sizeof(GL_Chunk_Texture_Manager));

    for (Index__u32 index_of__chunk = 0;
            index_of__chunk < 
            LOCAL_SPACE_MANAGER__WIDTH
            * LOCAL_SPACE_MANAGER__HEIGHT;
            index_of__chunk++) {
        GL_Chunk_Texture_Entry *p_GL_chunk_texture_entry =
            GL_get_p_chunk_texture_entry_by__index_from__chunk_texture_manager(
                    p_GL_chunk_texture_manager, 
                    index_of__chunk);

        if (!p_GL_chunk_texture_entry)
            continue;

        p_GL_chunk_texture_entry->uuid_of__chunk__u64 =
            IDENTIFIER__UNKNOWN__u64;
    }

    p_GL_chunk_texture_manager
        ->p_GL_framebuffer__chunk_compose =
        GL_allocate_framebuffer_with__framebuffer_manager(
                p_PLATFORM_gfx_context, 
                GL_get_p_framebuffer_manager_from__PLATFORM_gfx_context(
                    p_PLATFORM_gfx_context));

    u32 texture_size;
    switch (TILE__WIDTH_AND__HEIGHT_IN__PIXELS) {
        default:
            debug_abort("SDL::GL_initialize_chunk_texture_manager, tile width exceeds limit for chunk texture. Resulting texture size exceeds supported sizes.");
            return;
        case BIT(3): // 8x8     ->  64x 64
            texture_size =
                TEXTURE_FLAG__SIZE_64x64;
            break;
        case BIT(4): // 16x16   -> 128x128
            texture_size =
                TEXTURE_FLAG__SIZE_128x128;
            break;
        case BIT(5): // 32x32   -> 256x256
            texture_size =
                TEXTURE_FLAG__SIZE_256x256;
            break;
        case BIT(6): // 64x64   -> 512x512
            texture_size =
                TEXTURE_FLAG__SIZE_512x512;
            break;
    }

    p_GL_chunk_texture_manager
        ->texture_flags_for__chunks =
        TEXTURE_FLAGS(
                texture_size, 
                0,
                TEXTURE_FLAG__FORMAT__RGBA8888);
}

///
/// Returns true if any errors occur.
///
bool GL_allocate_textures_in__chunk_texture_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Local_Space_Manager *p_local_space_manager) {
    for (Index__u32 index_of__local_space = 0;
            index_of__local_space <
            LOCAL_SPACE_MANAGER__WIDTH
            * LOCAL_SPACE_MANAGER__HEIGHT;
            index_of__local_space++) {
        Local_Space *p_local_space =
            get_p_local_space_by__index_from__local_space_manager(
                    p_local_space_manager, 
                    index_of__local_space);

        if (!p_local_space)
            continue;

        if (!GL_poll_textures_for__chunk_in__chunk_texture_manager(
                    p_gfx_context,
                    p_ptr_array_of__gfx_windows,
                    p_GL_chunk_texture_manager, 
                    p_local_space, 
                    0,
                    0)) {
            return true;
        }
    }

    return false;
}

///
/// Returns true if any errors occur.
///
/// Will look in the chunk_texture_manager for the corresponding
/// chunk texture, and if it is not present, it will discard
/// the conflicted correspondence and allocate in it's place
/// the proper texture for the given chunk.
///
bool GL_poll_textures_for__chunk_in__chunk_texture_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Local_Space *p_local_space,
        Texture *ptr_array_OUT_textures_for__chunk,
        bool *p_OUT_is_chunk__needing_graphics_update) {
    Texture _tmp[GL_MAX_QUANTITY_OF__CHUNK_TEXTURES];
    if (!ptr_array_OUT_textures_for__chunk)
        ptr_array_OUT_textures_for__chunk = _tmp;

    Identifier__u64 uuid__u64 =
        get_uuid_for__global_space(
                p_local_space
                ->p_global_space
                ->chunk_vector__3i32);

    // TODO: this acquision of camera is hacky
    // and the chunk_texture_manager performing this check
    // may be overloading its responsibilities.
    Camera *p_camera = p_ptr_array_of__gfx_windows[0]
        ->p_camera;
    u32 local__z_index =
        abs(i32F4_to__i32(p_camera->position.z__i32F4))
        % CHUNK__DEPTH;

    Index__u32 column_in__manager =
        ((p_local_space
          ->p_global_space
          ->chunk_vector__3i32.x__i32
        % LOCAL_SPACE_MANAGER__WIDTH)
        + LOCAL_SPACE_MANAGER__WIDTH)
        % LOCAL_SPACE_MANAGER__WIDTH;

    Index__u32 row_in__manager =
        ((p_local_space
          ->p_global_space
          ->chunk_vector__3i32.y__i32
        % LOCAL_SPACE_MANAGER__HEIGHT)
        + LOCAL_SPACE_MANAGER__HEIGHT)
        % LOCAL_SPACE_MANAGER__HEIGHT;

    Index__u32 index_in__manager =
        column_in__manager
        + (LOCAL_SPACE_MANAGER__WIDTH
                * row_in__manager);
    
    GL_Chunk_Texture_Entry *p_GL_chunk_texture_entry =
        GL_get_p_chunk_texture_entry_by__index_from__chunk_texture_manager(
                p_GL_chunk_texture_manager, 
                index_in__manager);

#ifndef NDEBUG
    if (!p_GL_chunk_texture_entry) {
        return true;
    }
#endif

    if (p_GL_chunk_texture_entry
            ->uuid_of__chunk__u64
            == uuid__u64
            && p_GL_chunk_texture_entry
            ->local__z_index
            == local__z_index) {
        goto yield_textures;
    }

    if (p_GL_chunk_texture_entry->uuid_of__chunk__u64
             == IDENTIFIER__UNKNOWN__u64) {
        for (Index__u32 index_of__chunk_texture = 0;
                index_of__chunk_texture 
                < GL_MAX_QUANTITY_OF__CHUNK_TEXTURES;
                index_of__chunk_texture++) {
            if (PLATFORM_allocate_texture(
                        get_p_PLATFORM_gfx_context_from__gfx_context(p_gfx_context), 
                        p_ptr_array_of__gfx_windows[index_of__chunk_texture]
                        ->p_PLATFORM_gfx_window, 
                        p_GL_chunk_texture_manager
                        ->texture_flags_for__chunks, 
                        &p_GL_chunk_texture_entry
                        ->chunk_textures[index_of__chunk_texture])) {
                return true;
            }
        }
    }

    if (p_OUT_is_chunk__needing_graphics_update)
        *p_OUT_is_chunk__needing_graphics_update = true;
    p_GL_chunk_texture_entry->uuid_of__chunk__u64 =
        uuid__u64;
    p_GL_chunk_texture_entry->local__z_index =
        local__z_index;
yield_textures:
    for (Index__u32 index_of__chunk_texture = 0;
            index_of__chunk_texture 
            < GL_MAX_QUANTITY_OF__CHUNK_TEXTURES;
            index_of__chunk_texture++) {
        ptr_array_OUT_textures_for__chunk[index_of__chunk_texture]
            = p_GL_chunk_texture_entry
            ->chunk_textures[index_of__chunk_texture];
    }
    return false;
}
