#include "rendering/opengl/gl_shader.h"
#include "rendering/opengl/gl_vertex_object.h"
#include <rendering/opengl/gl_shader_sprite.h>
#include <sdl_defines.h>

const char *_source_shader_sprite__vertex = "\n\
#version 330 core\n\
layout(location = 0) in vec3 position;\n\
layout(location = 1) in vec2 uv;\n\
uniform vec2 spriteframe_row_col;\n\
uniform vec2 spriteframe_width_height;\n\
uniform vec2 sprite_flip;\n\
uniform mat4 projection;\n\
uniform mat4 translation;\n\
uniform mat4 model;\n\
\n\
out vec2 TexCoord;\n\
\n\
void main()\n\
{\n\
    gl_Position = (projection * translation * model) * (vec4(position, 1));\n\
    TexCoord = vec2(spriteframe_width_height.x * \n\
            (abs(sprite_flip.x-uv.x) + spriteframe_row_col.x),\n\
            spriteframe_width_height.y * \n\
            (abs(sprite_flip.y-uv.y) + spriteframe_row_col.y));\n\
}";

const char *_source_shader_sprite__fragment = " \n\
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
        color.a = 0.0;\n\
    }\n\
}";

void initialize_shader_2d_as__shader_sprite(
        GL_Shader_2D *shader) {
    initialize_shader_2d(
            shader, 
            _source_shader_sprite__vertex,
            _source_shader_sprite__fragment);

    shader->location_of__general_uniform_0 =
        glGetUniformLocation(
                shader->handle, 
                "spriteframe_row_col");
    shader->location_of__general_uniform_1 = 
        glGetUniformLocation(
                shader->handle, 
                "spriteframe_width_height");
    shader->location_of__general_uniform_2 =
        glGetUniformLocation(
                shader->handle, 
                "sprite_flip");
}
