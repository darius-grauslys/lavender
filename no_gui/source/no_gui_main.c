#include "defines.h"
#include "game.h"
#include "serialization/no_gui_filesystem.h"

int PLATFORM_main(Game *p_game) {
    NO_GUI_initialize_time();

    p_game->gfx_context.p_PLATFORM_gfx_context = 0;
    p_game->p_PLATFORM_file_system_context =
        &__NO_GUI_file_system_context;

    PLATFORM_initialize_file_system_context(
            p_game,
            p_game->p_PLATFORM_file_system_context);

    return run_game(p_game);
}
