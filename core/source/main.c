#include <defines.h>
#include <game.h>

Game game;

int main(void) {
#warning [***] hook default game action handler here.
    initialize_game(&game);
    return PLATFORM_main(&game);
}
