#include "defines_weak.h"
#include "platform.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_framebuffer.h"
#include "rendering/opengl/glad/glad.h"
#include "rendering/texture.h"
#include <rendering/opengl/gl_framebuffer_manager.h>

static inline
GL_Framebuffer *GL_get_p_framebuffer_by__index_from__framebuffer_manager(
        GL_Framebuffer_Manager *p_GL_framebuffer_manager,
        Index__u32 index_of__GL_framebuffer) {
    return &p_GL_framebuffer_manager
        ->GL_framebuffers[index_of__GL_framebuffer];
}

void GL_initialize_framebuffer_manager(
        GL_Framebuffer_Manager *p_GL_framebuffer_manager) {
    p_GL_framebuffer_manager
        ->index_of__framebuffer_on__stack = 0;
    for (Index__u16 index_of__GL_framebuffer = 0;
            index_of__GL_framebuffer < MAX_QUANTITY_OF__FRAMEBUFFERS;
            index_of__GL_framebuffer++) {
        GL_Framebuffer *p_GL_framebuffer =
            GL_get_p_framebuffer_by__index_from__framebuffer_manager(
                    p_GL_framebuffer_manager, 
                    index_of__GL_framebuffer);

        GL_set_framebuffer_as__deallocated(
                p_GL_framebuffer);

        GL_Framebuffer **p_ptr_GL_framebuffer =
            GL_get_p_ptr_framebuffer_by__index_from__stack_of__manager(
                    p_GL_framebuffer_manager, 
                    index_of__GL_framebuffer);

        *p_ptr_GL_framebuffer = 0;
    }

    glCreateFramebuffers(
            1,
            &p_GL_framebuffer_manager
            ->GL_framebuffer__post_processing
            .GL_framebuffer_handle);
}

GL_Framebuffer *GL_allocate_framebuffer_with__framebuffer_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Framebuffer_Manager *p_GL_framebuffer_manager) {
    for (Index__u16 index_of__GL_framebuffer = 0;
            index_of__GL_framebuffer < MAX_QUANTITY_OF__FRAMEBUFFERS;
            index_of__GL_framebuffer++) {
        GL_Framebuffer *p_GL_framebuffer =
            &p_GL_framebuffer_manager
            ->GL_framebuffers[index_of__GL_framebuffer];
        if (GL_is_framebuffer_allocated(p_GL_framebuffer))
            continue;

        glCreateFramebuffers(
                1,
                &p_GL_framebuffer->GL_framebuffer_handle);

        if (!p_GL_framebuffer->GL_framebuffer_handle) {
            debug_error("SDL::GL::GL_allocate_framebuffer_with__framebuffer_manager, failed to create framebuffer.");
            return 0;
        }
        
        GL_set_framebuffer_as__allocated(
                p_GL_framebuffer);

        return p_GL_framebuffer;
    }
    return 0;
}

GL_Framebuffer 
*GL_allocate_framebuffer_with__depth_buffer_from__framebuffer_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Framebuffer_Manager *p_GL_framebuffer_manager,
        Texture_Flags depth_buffer_size) {
    GL_Framebuffer *p_GL_framebuffer =
        GL_allocate_framebuffer_with__framebuffer_manager(
                p_PLATFORM_gfx_context,
                p_GL_framebuffer_manager);

    if (!p_GL_framebuffer) {
        return 0;
    }

    GLint framebuffer_handle__previous;
    glGetIntegerv(
            GL_FRAMEBUFFER_BINDING, 
            &framebuffer_handle__previous);

    glBindFramebuffer(
            GL_FRAMEBUFFER,
            GL_get_framebuffer__handle(
                p_GL_framebuffer));

    GLuint depth_render_buffer;
    glGenRenderbuffers(
            1, 
            &depth_render_buffer);
    glBindRenderbuffer(
            GL_RENDERBUFFER, 
            depth_render_buffer);
    glRenderbufferStorage(
            GL_RENDERBUFFER, 
            GL_DEPTH_COMPONENT24, 
            get_length_of__texture_flag__width(depth_buffer_size), 
            get_length_of__texture_flag__height(depth_buffer_size));
    glFramebufferRenderbuffer(
            GL_FRAMEBUFFER, 
            GL_DEPTH_ATTACHMENT, 
            GL_RENDERBUFFER, 
            depth_render_buffer);

    glBindFramebuffer(
            GL_FRAMEBUFFER,
            framebuffer_handle__previous);

    return p_GL_framebuffer;
}

void GL_release_framebuffer_from__framebuffer_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Framebuffer_Manager *p_GL_framebuffer_manager,
        GL_Framebuffer *p_GL_framebuffer) {
#ifndef NDEBUG
    int index = p_GL_framebuffer
        - p_GL_framebuffer_manager->GL_framebuffers
        ;
    if (index < 0
            || index >= MAX_QUANTITY_OF__FRAMEBUFFERS) {
        debug_abort("SDL::GL::GL_release_framebuffer_from__framebuffer_manager, p_GL_framebuffer is not from this manager.");
        return;
    }
#endif

    glDeleteFramebuffers(
            1,
            &p_GL_framebuffer->GL_framebuffer_handle);

    GL_set_framebuffer_as__deallocated(
            p_GL_framebuffer);
}

void GL_push_framebuffer_onto__framebuffer_manager(
        GL_Framebuffer_Manager *p_GL_framebuffer_manager,
        GL_Framebuffer *p_GL_framebuffer) {
#ifndef NDEBUG
    uint32_t index = 
        p_GL_framebuffer
        - p_GL_framebuffer_manager
        ->GL_framebuffers
        ;
    if (p_GL_framebuffer
            != &p_GL_framebuffer_manager->GL_framebuffer__post_processing
            && index >=
            MAX_QUANTITY_OF__FRAMEBUFFERS) {
        debug_error("GL_push_framebuffer_onto__framebuffer_manager, p_GL_framebuffer is not allocated with this manager.");
        return;
    }
#endif

    if (GL_is_framebuffer_manager__stack__full(
                p_GL_framebuffer_manager)) {
        debug_error("GL_push_framebuffer_onto__framebuffer_manager, stack is full.");
        return;
    }

    p_GL_framebuffer_manager
        ->GL_ptr_array__framebuffer_stack[
        p_GL_framebuffer_manager
            ->index_of__framebuffer_on__stack++] =
            p_GL_framebuffer
            ;

    glBindFramebuffer(
            GL_FRAMEBUFFER,
            GL_peek_framebuffer_stack_of__framebuffer_manager(
                p_GL_framebuffer_manager)
            ->GL_framebuffer_handle);
}

void GL_pop_framebuffer_off_of__framebuffer_manager(
        GL_Framebuffer_Manager *p_GL_framebuffer_manager) {
    if (GL_is_framebuffer_manager__stack__empty(
                p_GL_framebuffer_manager)) {
        debug_error("GL_pop_frameubffer_off_of__frameubffer_manager, stack is empty.");
        return;
    }

    Index__u32 *p_index_of__stack =
        GL_get_p_index_of__framebuffer_on__stack(
                p_GL_framebuffer_manager);

    p_GL_framebuffer_manager
        ->GL_ptr_array__framebuffer_stack[
        --(*p_index_of__stack)] = 0;

    if (*p_index_of__stack == 0) {
        glBindFramebuffer(
                GL_FRAMEBUFFER,
                0);
    } else {
        glBindFramebuffer(
                GL_FRAMEBUFFER,
                GL_peek_framebuffer_stack_of__framebuffer_manager(
                    p_GL_framebuffer_manager)
                ->GL_framebuffer_handle);
    }
}

GL_Framebuffer *GL_peek_framebuffer_stack_of__framebuffer_manager(
        GL_Framebuffer_Manager *p_GL_framebuffer_manager) {
#ifndef NDEBUG
    if (GL_is_framebuffer_manager__stack__empty(
                p_GL_framebuffer_manager)) {
        debug_error("GL_peek_framebuffer_stack_of__framebuffer_manager, stack is empty.");
        return 0;
    }
#endif
    return *GL_get_p_ptr_framebuffer_by__index_from__stack_of__manager(
            p_GL_framebuffer_manager, 
            *GL_get_p_index_of__framebuffer_on__stack(
                p_GL_framebuffer_manager) - 1);
}

void GL_dispose_framebuffer_manager(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Framebuffer_Manager *p_GL_framebuffer_manager) {
    for (Index__u16 index_of__GL_framebuffer = 0;
            index_of__GL_framebuffer < MAX_QUANTITY_OF__FRAMEBUFFERS;
            index_of__GL_framebuffer++) {
        GL_Framebuffer **p_ptr_GL_framebuffer =
            GL_get_p_ptr_framebuffer_by__index_from__stack_of__manager(
                    p_GL_framebuffer_manager, 
                    index_of__GL_framebuffer);
        *p_ptr_GL_framebuffer = 0;

        GL_Framebuffer *p_GL_framebuffer =
            GL_get_p_framebuffer_by__index_from__framebuffer_manager(
                    p_GL_framebuffer_manager, 
                    index_of__GL_framebuffer);
        if (GL_is_framebuffer_allocated(
                    p_GL_framebuffer)) {
            GL_release_framebuffer_from__framebuffer_manager(
                    p_PLATFORM_gfx_context, 
                    p_GL_framebuffer_manager, 
                    p_GL_framebuffer);
        }
    }
}
