#include "rendering/implemented/sprite_animation_registrar.h"
#include "debug/debug.h"
#include "defines.h"
#include "rendering/sprite_context.h"
#include "types/implemented/rendering/sprite_animation_group_kind.h"
#include "types/implemented/rendering/sprite_animation_kind.h"

// GEN-GROUPS-BEGIN
Sprite_Animation_Group_Set sprite_animation_group__humanoid = {
    6, // columns in group
    4, // rows in group
    10 // number of sub groups
};
// GEN-GROUPS-END

// GEN-ANIMATIONS-BEGIN
Sprite_Animation sprite_animation__humanoid__idle = {
    Sprite_Animation_Kind__Humanoid_Idle,
    (Timer__u8){0,8},
    0, // init frame on row
    1, // quantity of frames
    8, // ticks per frame
    SPRITE_ANIMATION_FLAGS__NONE
};

Sprite_Animation sprite_animation__humanoid__walk = {
    Sprite_Animation_Kind__Humanoid_Walk,
    (Timer__u8){0,8},
    1, // init frame on row
    2, // quantity of frames
    8, // ticks per frame
    SPRITE_ANIMATION_FLAGS__NONE
};

Sprite_Animation sprite_animation__humanoid__use = {
    Sprite_Animation_Kind__Humanoid_Use,
    (Timer__u8){0,8},
    3, // init frame on row
    3, // quantity of frames
    8, // ticks per frame
    SPRITE_ANIMATION_FLAGS__NONE
};

Sprite_Animation sprite_animation__humanoid__die = {
    Sprite_Animation_Kind__Humanoid_Die,
    (Timer__u8){0,8},
    18,// init frame on row
    3, // quantity of frames
    8,  // ticks per frame
    SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING
};

Sprite_Animation sprite_animation__humanoid__sleep = {
    Sprite_Animation_Kind__Humanoid_Sleep,
    (Timer__u8){0,8},
    21,// init frame on row
    1, // quantity of frames
    8,  // ticks per frame
    SPRITE_ANIMATION_FLAG__IS_NOT_LOOPING
};
// GEN-ANIMATIONS-END

void register_sprite_animations(
        Sprite_Context *p_sprite_context) {
    //GEN-REGISTER-GROUPS-BEGIN
    register_sprite_animation_group_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Group_Kind__Humanoid, 
            sprite_animation_group__humanoid);
    //GEN-REGISTER-GROUPS-END

    //GEN-REGISTER-ANIMATIONS-BEGIN
    register_sprite_animation_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Kind__Humanoid_Walk, 
            sprite_animation__humanoid__walk);
    
    register_sprite_animation_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Kind__Humanoid_Idle, 
            sprite_animation__humanoid__idle);

    register_sprite_animation_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Kind__Humanoid_Use, 
            sprite_animation__humanoid__use);

    register_sprite_animation_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Kind__Humanoid_Die, 
            sprite_animation__humanoid__die);

    register_sprite_animation_into__sprite_context(
            p_sprite_context, 
            Sprite_Animation_Kind__Humanoid_Sleep, 
            sprite_animation__humanoid__sleep);
    //GEN-REGISTER-ANIMATIONS-END
}

