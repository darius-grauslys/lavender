#include "rendering/opengl/gl_shader.h"
#include <rendering/opengl/gl_shader_chunk.h>

const char *_source_shader_chunk__vertex = "\n\
#version 330 core\n\
layout(location = 0) in vec3 position;\n\
layout(location = 1) in vec2 uv;\n\
uniform vec2 tileframe_row_col;\n\
uniform vec2 tileframe_width_height;\n\
uniform vec2 tile_flip;\n\
uniform mat4 projection;\n\
uniform mat4 translation;\n\
uniform mat4 model;\n\
\n\
out vec2 TexCoord;\n\
\n\
void main()\n\
{\n\
    gl_Position = (projection * translation * model) * (vec4(position, 1));\n\
    TexCoord = vec2(tileframe_width_height.x * \n\
            (abs(tile_flip.x-uv.x) + tileframe_row_col.x),\n\
            tileframe_width_height.y * \n\
            (abs(tile_flip.y-uv.y) + tileframe_row_col.y));\n\
}";

const char *_source_shader_chunk__fragment = " \n\
#version 330 core\n\
uniform sampler2D _sample;\n\
\n\
in vec2 TexCoord;\n\
out vec4 color;\n\
\n\
void main()\n\
{\n\
    color = texture(_sample, TexCoord);\n\
    if (color.r == 1.0 && color.g == 0.0 && color.b == 1.0) {\n\
        discard;\n\
    }\n\
}";

void initialize_shader_2d_as__shader_chunk(
        GL_Shader_2D *p_GL_shader) {
    initialize_shader_2d(
            p_GL_shader, 
            _source_shader_chunk__vertex,
            _source_shader_chunk__fragment);
    p_GL_shader->location_of__general_uniform_0
        = glGetUniformLocation(
                p_GL_shader->handle, 
                "tileframe_row_col");
    p_GL_shader->location_of__general_uniform_1
        = glGetUniformLocation(
                p_GL_shader->handle, 
                "tileframe_width_height");
    p_GL_shader->location_of__general_uniform_2
        = glGetUniformLocation(
                p_GL_shader->handle, 
                "tile_flip");
}

