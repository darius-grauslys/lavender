#ifndef GL_CHUNK_TEXTURE_MANAGER_H
#define GL_CHUNK_TEXTURE_MANAGER_H

#include "defines_weak.h"
#include "rendering/opengl/gl_defines.h"

void GL_initialize_chunk_texture_manager(
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager);

///
/// Returns true if any errors occur.
///
bool GL_allocate_textures_in__chunk_texture_manager(
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
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
        Gfx_Context *p_gfx_context,
        Graphics_Window **p_ptr_array_of__gfx_windows,
        GL_Chunk_Texture_Manager *p_GL_chunk_texture_manager,
        Local_Space *p_local_space,
        Texture *ptr_array_OUT_textures_for__chunk);

#endif
