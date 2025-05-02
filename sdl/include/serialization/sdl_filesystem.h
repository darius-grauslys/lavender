#ifndef SDL_FILESYSTEM
#define SDL_FILESYSTEM

#include <sdl_defines.h>
#include <serialization/sdl_filesystem_defines.h>

extern PLATFORM_File_System_Context __SDL_file_system_context;

bool SDL_get_path_to__the_game(char path[1024]);

void SDL_poll_serialization_requests(
        Game *p_game);

void m_SDL_process__serialization(
        Process *p_this_process,
        Game *p_game);

#endif
