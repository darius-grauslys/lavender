#include "defines.h"
#include "defines_weak.h"
#include <game_action/game_action.h>
#include <serialization/serialized_field.h>

void initialize_p_game_action(
        Game_Action *p_game_action){
    memset(p_game_action, 0, sizeof(Game_Action));
}        
