#ifndef GL_CHUNK_TEXTURE_MANAGER_H
#define GL_CHUNK_TEXTURE_MANAGER_H

#include "defines_weak.h"
#include "rendering/opengl/gl_defines.h"

void GL_initialize_chunk_texture_manager(
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager);

void GL_allocate_textures_in__chunk_texture_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Local_Space_Manager *p_local_space_manager);

///
/// Returns true if any errors occur.
///
/// Will look in the chunk_texture_manager for the corresponding
/// chunk texture, and if it is not present, it will discard
/// the conflicted correspondence and allocate in it's place
/// the proper texture for the given chunk.
///
bool GL_poll_textures_for__chunk_in__chunk_texture_manager(
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Global_Space *p_global_space,
        Texture *p_OUT_texture);

#endif
