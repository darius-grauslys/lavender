#ifndef SDL_VERTEX_OBJECT_H
#define SDL_VERTEX_OBJECT_H

#include "platform_defines.h"
#include <defines.h>
#include <rendering/opengl/gl_defines.h>

void initialize_vertex_object(
        GL_Vertex_Object *vertex_object,
        float width,
        float height);

static inline
void initialize_vertex_object_as__unit_square(
        GL_Vertex_Object *vertex_object) {
    initialize_vertex_object(
            vertex_object,
            BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT), 
            BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT));
}

void buffer_vertex_object(GL_Vertex_Object *vertex_object,
        uint32_t size_in_bytes, uint32_t vertex_count, float *vertices);

void buffer_vertex_object__element_buffer(
        GL_Vertex_Object *vertex_object,
        uint32_t size_in_bytes__of_indices,
        uint32_t *indices);

void set_attribute_vertex_object(GL_Vertex_Object *vertex_object,
        uint32_t attribute_index,
        uint32_t attribute_size,
        uint32_t gl_attribute_type,
        uint32_t gl_bool_is_normalized,
        uint32_t size_in_bytes__of_attribute,
        void *offset);

void release_vertex_object(GL_Vertex_Object *vertex_object);

void use_vertex_object(GL_Vertex_Object *vertex_object);

void GL_set_vertex_object__unit_square__UVs_within__texture_atlas(
        GL_Vertex_Object *p_GL_vertex_object,
        PLATFORM_Texture *p_PLATFORM_texture,
        GLint col,
        GLint row,
        GLint quantity_of__columns,
        GLint quantity_of__rows);

#endif
