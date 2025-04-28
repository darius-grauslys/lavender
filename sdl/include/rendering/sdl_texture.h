#ifndef SDL_TEXTURE_H
#define SDL_TEXTURE_H

#include "defines_weak.h"
#include <sdl_defines.h>
#include "rendering/texture.h"

void SDL_initialize_texture_as__deallocated(
        PLATFORM_Texture *p_PLATFORM_texture);

void SDL_update_texture_format_and__access(
        PLATFORM_Texture *p_PLATFORM_texture,
        Texture_Flags texture_flags);

#endif
