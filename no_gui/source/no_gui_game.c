#include "defines.h"
#include "game.h"
#include "platform.h"
#include "serialization/no_gui_filesystem.h"
#include "time/no_gui_time.h"

void PLATFORM_initialize_game(Game *p_game) {
    PLATFORM_initialize_time();

    p_game->gfx_context.p_PLATFORM_gfx_context = 0;
    p_game->p_PLATFORM_file_system_context =
        &__NO_GUI_file_system_context;

    PLATFORM_initialize_file_system_context(
            p_game,
            p_game->p_PLATFORM_file_system_context);
}

void PLATFORM_close_game(Game *p_game) {}
