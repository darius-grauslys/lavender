#ifndef IMPL_GAME_ACTION_KIND_H
#define IMPL_GAME_ACTION_KIND_H

#define DEFINE_GAME_ACTION_KIND

//
// All Game_Action_Kinds present in this file must
// remain under modification.
//
// In otherwords, only add and remove added Game_Actions.
//

typedef enum Game_Action_Kind {
    Game_Action_Kind__None = 0,
    Game_Action_Kind__Bad_Request,
    Game_Action_Kind__TCP_Connect__Begin,
    Game_Action_Kind__TCP_Connect,
    Game_Action_Kind__TCP_Connect__Reject,
    Game_Action_Kind__TCP_Connect__Accept,
    Game_Action_Kind__TCP_Disconnect,
    Game_Action_Kind__TCP_Delivery,
    Game_Action_Kind__World__Load_World,
    Game_Action_Kind__World__Load_Client,
    Game_Action_Kind__World__Request_Client_Data,
    Game_Action_Kind__Global_Space__Request,
    Game_Action_Kind__Global_Space__Resolve,
    Game_Action_Kind__Global_Space__Store,
    Game_Action_Kind__Inventory__Request,
    Game_Action_Kind__Inventory__Resolve,
    Game_Action_Kind__Entity__Spawn,
    Game_Action_Kind__Entity__Get,
    Game_Action_Kind__Sprite,
    
    // Opaque pointer hitbox, abstracts to any other
    // hitbox. Least performant.
    Game_Action_Kind__Hitbox,
    // TODO: impl:
    // Game_Action_Kind__Hitbox__AABB,
    // Game_Action_Kind__Hitbox__AAABBB,
    // Game_Action_Kind__Hitbox__Ball,
    // Game_Action_Kind__Hitbox__Sphere,

    // Not a hitbox, delimits the enum end of hitboxes
    Game_Action_Kind__Hitbox__End,

    // Reuse enum end value
    Game_Action_Kind__Input = Game_Action_Kind__Hitbox__End,
    Game_Action_Kind__Custom,

    ///
    /// Custom Game Actions YOU define for YOUR GAME go here.
    ///

    Game_Action_Kind__Unknown
} Game_Action_Kind;

#endif
