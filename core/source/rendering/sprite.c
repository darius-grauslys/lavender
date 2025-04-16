#include "debug/debug.h"
#include "defines_weak.h"
#include "serialization/serialization_header.h"
#include <rendering/sprite.h>
#include <defines.h>

void initialize_sprite(
        Sprite *sprite,
        Texture_Flags texture_flags_for__sprite) {
    memset(sprite,
            0,
            sizeof(Sprite));
    initialize_serialization_header_for__deallocated_struct(
            (Serialization_Header *)sprite, 
            sizeof(Sprite));
}
