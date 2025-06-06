#ifndef GL_FRAMEBUFFER_H
#define GL_FRAMEBUFFER_H

#include "sdl_defines.h"
#include <rendering/opengl/gl_defines.h>

void GL_initialize_framebuffer_as__deallocated(
        GL_Framebuffer *p_GL_framebuffer);

void GL_initialize_framebuffer(
        GL_Framebuffer *p_GL_framebuffer,
        PLATFORM_Texture *p_PLATFORM_texture);

void GL_bind_texture_to__framebuffer(
        GL_Framebuffer *p_GL_framebuffer,
        PLATFORM_Texture *p_PLATFORM_texture);

static inline
bool GL_is_framebuffer_allocated(
        GL_Framebuffer *p_GL_framebuffer) {
    return p_GL_framebuffer->is_allocated;
}

static inline
void GL_set_framebuffer_as__allocated(
        GL_Framebuffer *p_GL_framebuffer) {
    p_GL_framebuffer->is_allocated = true;
}

static inline
void GL_set_framebuffer_as__deallocated(
        GL_Framebuffer *p_GL_framebuffer) {
    p_GL_framebuffer->is_allocated = false;
}

static inline
GLuint GL_get_framebuffer__handle(
        GL_Framebuffer *p_GL_framebuffer) {
    return p_GL_framebuffer
        ->GL_framebuffer_handle
        ;
}

#endif
