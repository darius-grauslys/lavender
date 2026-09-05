#include <SDL2/SDL_video.h>
#include <defines_weak.h>
#include <game.h>
#include <platform.h>
#include <rendering/opengl/gl_defines.h>
#include <debug/opengl/gl_debug_screen.h>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include <rendering/stb_image_write.h>

bool _gl_debug_screencap(Game *p_game, u64 framebuffer__u64) {
    ///
    /// GL content of this function was AI generated.
    ///

    // 1. Save the currently bound read-framebuffer to restore state afterward
    GLint previous_fbo = 0;
    glGetIntegerv(GL_READ_FRAMEBUFFER_BINDING, &previous_fbo);

    // 2. Bind the target FBO handle exclusively for reading
    glBindFramebuffer(GL_READ_FRAMEBUFFER, framebuffer__u64);

    // 3. Query the width and height of the attached color object dynamically
    GLint width = 0;
    GLint height = 0;
    
    if (0 == framebuffer__u64) {
        SDL_GL_GetDrawableSize(
                get_p_PLATFORM_gfx_context_from__game(p_game)
                ->p_SDL_window, 
                &width, 
                &height);
    } else {
        // Check what type of object is attached to color 0 (Texture vs Renderbuffer)
        GLint attachment_type = GL_NONE;
        glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                          GL_FRAMEBUFFER_ATTACHMENT_OBJECT_TYPE, &attachment_type);
        if (attachment_type == GL_TEXTURE) {
            GLint texture_name = 0;
            glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                                  GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME, &texture_name);
            
            // Temporarily bind the texture to read its dimensions
            GLint previous_tex = 0;
            glGetIntegerv(GL_TEXTURE_BINDING_2D, &previous_tex);
            glBindTexture(GL_TEXTURE_2D, texture_name);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_WIDTH, &width);
            glGetTexLevelParameteriv(GL_TEXTURE_2D, 0, GL_TEXTURE_HEIGHT, &height);
            glBindTexture(GL_TEXTURE_2D, previous_tex); // Restore texture state
        } else if (attachment_type == GL_RENDERBUFFER) {
            GLint rbo_name = 0;
            glGetFramebufferAttachmentParameteriv(GL_READ_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, 
                                                  GL_FRAMEBUFFER_ATTACHMENT_OBJECT_NAME, &rbo_name);
            
            // Temporarily bind the renderbuffer to read its dimensions
            GLint previous_rbo = 0;
            glGetIntegerv(GL_RENDERBUFFER_BINDING, &previous_rbo);
            glBindRenderbuffer(GL_RENDERBUFFER, rbo_name);
            glGetRenderbufferParameteriv(GL_RENDERBUFFER, GL_RENDERBUFFER_WIDTH, &width);
            glGetRenderbufferParameteriv(GL_RENDERBUFFER, GL_RENDERBUFFER_HEIGHT, &height);
            glBindRenderbuffer(GL_RENDERBUFFER, previous_rbo); // Restore renderbuffer state
        } else {
            // Fallback: If it's the default window framebuffer (handle == 0)
            // You can pass the window size using SDL_GL_GetDrawableSize
            debug_error("_gl_debug_screencap, Color attachment 0 is empty or invalid.");
            glBindFramebuffer(GL_READ_FRAMEBUFFER, previous_fbo);
            return NULL;
        }
    }

    // 4. Force byte alignment to 1 to guarantee dense arrays without padding lines
    GLint previous_alignment = 4;
    glGetIntegerv(GL_PACK_ALIGNMENT, &previous_alignment);
    glPixelStorei(GL_PACK_ALIGNMENT, 1);

    if (0 == framebuffer__u64) {
        // 5. Read from main buffer
        glReadBuffer(GL_BACK);
    } else {
        // 5. Specify that we are pulling from the primary color attachment
        glReadBuffer(GL_COLOR_ATTACHMENT0);
    }

    // 6. Allocate memory for the raw RGBA pixel data (Width * Height * 4 bytes)
    size_t buffer_size = (size_t)width * (size_t)height * 4;
    unsigned char* pixel_data = (unsigned char*)malloc(buffer_size);

    if (pixel_data) {
        // Read directly out of the GPU backbuffer to CPU client memory
        glReadPixels(0, 0, width, height, GL_RGBA, GL_UNSIGNED_BYTE, pixel_data);
    }

    // 7. Cleanup and seamlessly restore original OpenGL pipeline states
    glPixelStorei(GL_PACK_ALIGNMENT, previous_alignment);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, previous_fbo);

    IO_path dir_path;
    memset(dir_path, 0, sizeof(IO_path));

    Quantity__u32 size_of__path = PLATFORM_get_base_directory(dir_path);

    const char *p_sub_path = "/screen.png";
    Quantity__u32 length_of__sub_path = strnlen(p_sub_path, MAX_LENGTH_OF__IO_PATH - size_of__path);
    if (size_of__path + length_of__sub_path
            > MAX_LENGTH_OF__IO_PATH) {
        free(pixel_data);
        debug_warning("[DEBUG] _gl_debug_screencap, output path exceeds MAX_LENGTH_OF__IO_PATH.");
        return false;
    }
    u8 offset = 0;
    if (dir_path[size_of__path-1] == '/') {
        offset = 1;
    }

    strncpy(dir_path + size_of__path, p_sub_path + offset, length_of__sub_path - offset);

    Quantity__u32 safe_size__u32 = sizeof(IO_path)+1;
    char *p_safe_path = malloc(safe_size__u32);
    memset(p_safe_path, 0, safe_size__u32);

    strncpy(p_safe_path, dir_path, sizeof(IO_path));

    stbi_flip_vertically_on_write(1);

    bool success = stbi_write_png(
            p_safe_path, 
            width, 
            height, 
            4, 
            pixel_data, 
            width * 4);

    free(pixel_data);

    if (!success) {
        debug_warning("[DEBUG] Note file was writing to:");
        debug_warning(p_safe_path);
        debug_warning("[DEBUG] _gl_debug_screencap, failed to write to file.");
    } else {
        debug_info("[DEBUG] _gl_debug_screencap, wrote file:");
        debug_info(p_safe_path);
    }

    return success;
}

bool gl_debug_screencap(Game *p_game) {
    return _gl_debug_screencap(
            p_game, 
            0);
}

bool gl_debug_screencap__framebuffer(
        Game *p_game, 
        GL_Framebuffer *p_gl_framebuffer) {
    if (!p_gl_framebuffer) {
        debug_warning("[DEBUG] gl_debug_screencap__framebuffer, p_gl_framebuffer == 0.");
        return false;
    }

    return _gl_debug_screencap(
            p_game, 
            p_gl_framebuffer->GL_framebuffer_handle);
}
