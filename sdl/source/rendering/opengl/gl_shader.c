#include "align.h"
#include "defines.h"
#include "numerics.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "rendering/opengl/gl_defines.h"
#include "rendering/opengl/gl_numerics.h"
#include "rendering/opengl/gl_viewport.h"
#include "rendering/opengl/glad/glad.h"
#include "sdl_numerics.h"
#include <cglm/clipspace/ortho_lh_no.h>
#include <cglm/mat4.h>
#include <cglm/types.h>
#include <rendering/opengl/gl_shader.h>
#include <debug/debug.h>
#include <stddef.h>
#include <cglm/affine.h>

void initialize_shader_2d_as__deallocated(
        GL_Shader_2D *p_GL_shader) {
    p_GL_shader->location_of__projection_mat_4_4 = -1;
    p_GL_shader->location_of__translation_mat_4_4 = -1;
    p_GL_shader->location_of__model_mat_4_4 = -1;
    p_GL_shader->is_shader__allocated = false;
}
int initialize_shader_2d(GL_Shader_2D *shader, const char *source_vertex,
        const char *source_fragment) {
    shader->handle = 0;
    shader->vertex_handle = 0;
    shader->fragment_handle = 0;

    shader->vertex_handle = 
        glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(shader->vertex_handle, 1, &source_vertex, NULL);
    glCompileShader(shader->vertex_handle);

    glGetShaderiv(shader->vertex_handle, GL_COMPILE_STATUS,
            &shader->success_code);
    if (!shader->success_code) {
        char log[512];
        glGetShaderInfoLog(shader->vertex_handle, 512, NULL, log);
        debug_error("SDL::GL::initialize_shader_2d, failed to load vertex shader: %s", log);
        glDeleteShader(shader->vertex_handle);
        return shader->success_code;
    }

    shader->fragment_handle = 
        glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(shader->fragment_handle, 1, &source_fragment, NULL);
    glCompileShader(shader->fragment_handle);

    glGetShaderiv(shader->fragment_handle, GL_COMPILE_STATUS,
            &shader->success_code);
    if (!shader->success_code) {
        char log[512];
        glGetShaderInfoLog(shader->fragment_handle, 512, NULL, log);
        debug_error("SDL::GL::initialize_shader_2d, ailed to load fragment shader: %s", log);
        glDeleteShader(shader->vertex_handle);
        glDeleteShader(shader->fragment_handle);
        return shader->success_code;
    }

    shader->handle = glCreateProgram();
    glAttachShader(shader->handle, shader->vertex_handle);
    glAttachShader(shader->handle, shader->fragment_handle);
    glLinkProgram(shader->handle);

    glGetProgramiv(shader->handle, GL_LINK_STATUS, &shader->success_code);
    if(!shader->success_code) {
        char log[512];
        glGetProgramInfoLog(shader->fragment_handle, 512, NULL, log);
        debug_error("SDL::GL::initialize_shader_2d, failed to link shader: %s", log);
        glDeleteShader(shader->vertex_handle);
        glDeleteShader(shader->fragment_handle);
        return shader->success_code;
    }

    shader->location_of__projection_mat_4_4
        = glGetUniformLocation(
                shader->handle, 
                "projection");
    shader->location_of__translation_mat_4_4
        = glGetUniformLocation(
                shader->handle, 
                "translation");
    shader->location_of__model_mat_4_4
        = glGetUniformLocation(
                shader->handle, 
                "model");

    shader->location_of__general_uniform_0 = -1;
    shader->location_of__general_uniform_1 = -1;
    shader->location_of__general_uniform_2 = -1;
    shader->location_of__general_uniform_3 = -1;

    glDeleteShader(shader->vertex_handle);
    glDeleteShader(shader->fragment_handle);
    return 0;
}

int use_shader_2d(GL_Shader_2D *shader) {
    glUseProgram(shader->handle);
    return 0;
}

int release_shader_2d(GL_Shader_2D *shader) {
    if (!shader->handle) return 1;
    glDeleteProgram(shader->handle);
    shader->handle = 0;
    return 0;
}

void GL_link_projection_to__shader(
        GL_Shader_2D *p_GL_shader,
        float _projection[16]) {
    ALIGN(16, mat4, projection);

    memcpy(
            *p_projection,
            _projection,
            16 * sizeof(float));

    glUniformMatrix4fv(
            p_GL_shader->location_of__projection_mat_4_4,
            1,
            false,
            (const GLfloat*)*p_projection);
}

void GL_link_translation_to__shader(
        GL_Shader_2D *p_GL_shader,
        Vector__3i32F4 _translation) {
    vec3 vec3__translation;

    vector_3i32F4_to__vec3(
            _translation, 
            vec3__translation);

    ALIGN(16, mat4, translation);

    vec3__translation[0] *= -(1.0/16);
    vec3__translation[1] *= -(1.0/16);
    vec3__translation[2] *= -(1.0/16);

    glm_translate_make(
            *p_translation, 
            vec3__translation);

    glUniformMatrix4fv(
            p_GL_shader->location_of__translation_mat_4_4,
            1,
            false,
            (const float*)*p_translation);
}

void GL_link_camera_projection_to__shader(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Shader_2D *p_GL_shader,
        Camera *p_camera) {

    ALIGN(16, mat4, projection);

    if (p_camera) {
        glm_ortho_lh_no(
                -(float)p_camera->width_of__fulcrum 
                    / (float)(TILE__WIDTH_AND__HEIGHT_IN__PIXELS<<1), 
                 (float)p_camera->width_of__fulcrum 
                    / (float)(TILE__WIDTH_AND__HEIGHT_IN__PIXELS<<1), 
                -(float)p_camera->height_of__fulcrum  
                    / (float)(TILE__WIDTH_AND__HEIGHT_IN__PIXELS<<1), 
                 (float)p_camera->height_of__fulcrum 
                    / (float)(TILE__WIDTH_AND__HEIGHT_IN__PIXELS<<1), 
                 i32F20_to__float(p_camera->z_near),
                 i32F20_to__float(p_camera->z_far),
                 *p_projection);
    } else {
        glm_ortho_lh_no(
                -(int)( CAMERA_FULCRUM__WIDTH
                    >> (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + 1)),
                (int)( CAMERA_FULCRUM__WIDTH
                    >> (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + 1)),
                -(int)( CAMERA_FULCRUM__HEIGHT
                    >> (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + 1)),
                (int)( CAMERA_FULCRUM__HEIGHT
                    >> (TILE__WIDTH_AND__HEIGHT__BIT_SHIFT + 1)),
                // TODO: magic numbers in no camera default projection
                -8.0f,
                 8.0f,
                 *p_projection);
    }

    glUniformMatrix4fv(
            p_GL_shader->location_of__projection_mat_4_4,
            1,
            false,
            (const GLfloat*)*p_projection);
}

void GL_link_camera_translation_to__shader(
        GL_Shader_2D *p_GL_shader,
        Camera *p_camera) {

    vec3 vec3__translation;

    ALIGN(16, mat4, translation);

    if (p_camera) {
        vector_3i32F4_to__vec3(
                p_camera->position, 
                vec3__translation);
            vec3__translation[0] *= 
                -(1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
            vec3__translation[1] *= 
                -(1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
            vec3__translation[2] *= 
                (1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));

        glm_translate_make(
                *p_translation, 
                vec3__translation);
    } else {
        glm_mat4_identity(*p_translation);
    }

    glUniformMatrix4fv(
            p_GL_shader->location_of__translation_mat_4_4,
            1,
            false,
            (const float*)*p_translation);
}

void GL_link_model_data_to__shader(
        GL_Shader_2D *p_GL_shader,
        Vector__3i32F4 position,
        i32F4 scale) {
    mat4 model;
    glm_mat4_identity(model);
    float scale__float = i32F4_to__float(scale);
    vec3 vector3_cglm;
    vector_3i32F4_to__vec3(
            position, 
            vector3_cglm);
    vector3_cglm[0] *= (1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    vector3_cglm[1] *= (1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    vector3_cglm[2] *= -(1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    glm_translate(
            model, 
            vector3_cglm);
    glm_scale_uni(model, scale__float);
    glUniformMatrix4fv(
            p_GL_shader->location_of__model_mat_4_4,
            1,
            false,
            (const GLfloat*)model);
}

void GL_link_model_data_to__shader_with__non_uniform_scale(
        GL_Shader_2D *p_GL_shader,
        Vector__3i32F4 position,
        i32F4 scale__x,
        i32F4 scale__y) {
    mat4 model;
    glm_mat4_identity(model);
    vec3 vector3_cglm;
    vector_3i32F4_to__vec3(
            position, 
            vector3_cglm);
    vector3_cglm[0] *= (1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    vector3_cglm[1] *= (1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    vector3_cglm[2] *= -(1.0/(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)));
    vec3 vector3_cglm__scale = {
        i32F4_to__float(scale__x),
        i32F4_to__float(scale__y),
        1
    };
    glm_translate(
            model, 
            vector3_cglm);
    glm_scale(model, vector3_cglm__scale);
    glUniformMatrix4fv(
            p_GL_shader->location_of__model_mat_4_4,
            1,
            false,
            (const GLfloat*)model);
}

void GL_link_data_to__shader(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Shader_2D *p_GL_shader,
        Camera *p_camera,
        Vector__3i32F4 position__3i32F4,
        i32F4 scale) {
    if (GL_does_shader_utilize__projection_mat_4_4(
                p_GL_shader)) {
        GL_link_camera_projection_to__shader(
                p_PLATFORM_gfx_context,
                p_GL_shader, 
                p_camera);
    }
    if (GL_does_shader_utilize__translation_mat_4_4(
                p_GL_shader)) {
        GL_link_camera_translation_to__shader(
                p_GL_shader, 
                p_camera);
    }
    if (GL_does_shader_utilize__model_mat_4_4(
                p_GL_shader)) {
        GL_link_model_data_to__shader(
                p_GL_shader, 
                position__3i32F4, 
                scale);
    }
}

void GL_link_data_to__shader_with__scale(
        PLATFORM_Gfx_Context *p_PLATFORM_gfx_context,
        GL_Shader_2D *p_GL_shader,
        Camera *p_camera,
        Vector__3i32F4 position__3i32F4,
        i32F4 scale__x,
        i32F4 scale__y) {
    if (GL_does_shader_utilize__projection_mat_4_4(
                p_GL_shader)) {
        GL_link_camera_projection_to__shader(
                p_PLATFORM_gfx_context,
                p_GL_shader, 
                p_camera);
    }
    if (GL_does_shader_utilize__translation_mat_4_4(
                p_GL_shader)) {
        GL_link_camera_translation_to__shader(
                p_GL_shader, 
                p_camera);
    }
    if (GL_does_shader_utilize__model_mat_4_4(
                p_GL_shader)) {
        GL_link_model_data_to__shader_with__non_uniform_scale(
                p_GL_shader, 
                position__3i32F4, 
                scale__x,
                scale__y);
    }
}
