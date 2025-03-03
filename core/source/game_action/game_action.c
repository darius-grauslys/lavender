#include "defines.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include <game_action/game_action.h>
#include <serialization/serialized_field.h>

void initialize_game_action(
        Game_Action *p_game_action){
    memset(p_game_action, 0, sizeof(Game_Action));
    initialize_serialization_header_for__deallocated_struct(
            &p_game_action->_serialiation_header, 
            sizeof(Game_Action));
}        
