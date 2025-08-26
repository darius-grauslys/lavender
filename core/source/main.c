#include "platform.h"
#include <defines.h>
#include <game.h>

Game game;

int main(void) {
#warning [***] hook default game action handler here.
    initialize_game(&game);
    int return_code = run_game(&game);
    PLATFORM_close_game(&game);
    return return_code;
}
