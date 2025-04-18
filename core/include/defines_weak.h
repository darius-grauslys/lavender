#ifndef DEFINE_WEAK_H
#define DEFINE_WEAK_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/// Forward declarations to various types
/// within define.h

///
/// SECTION_default
///

#define _STRING(x) #x
#define STRING(x) _STRING(x)
#define BIT(n) (1 << (n))
#define NEXT_BIT(symbol) (symbol << 1)
#define MASK(n) ((u32)BIT(n) - 1)


typedef int32_t     i32;
typedef int16_t     i16;
typedef int8_t      i8;
typedef uint64_t    u64;
typedef uint32_t    u32;
typedef uint16_t    u16;
typedef uint8_t     u8;

typedef int32_t     i32F4;
typedef int16_t     i16F4;
typedef int8_t      i8F4;
typedef uint32_t    u32F4;
typedef uint16_t    u16F4;
typedef uint8_t     u8F4;

typedef int32_t     i32F20;
typedef int16_t     i16F8;
typedef int8_t      i8F8;

typedef uint32_t     u32F20;

typedef uint32_t    Texture_Flags;
typedef uint8_t     Sprite_Flags;
typedef uint8_t     Quantity__u8;
typedef uint16_t    Quantity__u16;
typedef uint32_t    Quantity__u32;

typedef uint8_t Index__u8;
typedef uint16_t Index__u16;
typedef uint32_t Index__u32;

typedef int32_t Signed_Index__i32;
typedef int16_t Signed_Index__i16;
typedef int8_t  Signed_Index__i8;

typedef uint64_t Identifier__u64;
typedef uint32_t Identifier__u32;
typedef uint16_t Identifier__u16;
typedef uint8_t Identifier__u8;

typedef int32_t     Fractional_with__4bit__i32;

typedef struct Vector__3i32F4_t Vector__3i32F4;
typedef struct Vector__3i32_t Vector__3i32;
typedef struct Vector__3i32_t Chunk_Vector__3i32;
typedef struct Vector__3i32_t Tile_Vector__3i32;

typedef struct Timer__u32_t Timer__u32;
typedef struct Timer__u16_t Timer__u16;
typedef struct Timer__u8_t Timer__u8;

typedef struct Date_Time_t Date_Time;

///
/// SECTION_audio
///

typedef u8 Audio_Flags__u8;
typedef struct Audio_Effect_t Audio_Effect;

#include <types/implemented/audio_effect_kind.h>
#ifndef DEFINE_AUDIO_EFFECT_KIND
enum Audio_Effect_Kind {
    Audio_Effect_Kind__None,
    Audio_Effect_Kind__Unknown,
};
#endif

#include <types/implemented/audio_stream_kind.h>
#ifndef DEFINE_AUDIO_STREAM_KIND
enum Audio_Stream_Kind {
    Audio_Stream_Kind__None,
    Audio_Stream_Kind__Unknown
};
#endif

///
/// SECTION_collisions
///

///
/// SECTION_debug
///

///
/// SECTION_entity
///

#include <types/implemented/entity_kind.h>
#ifndef DEFINE_ENTITY_KIND
typedef enum Entity_Kind {
    Entity_Kind__None,
    Entity_Kind__Unknown
} Entity_Kind;
#endif

typedef struct Entity_t Entity;
typedef struct Game_t Game;
typedef struct World_t World;

typedef void (*m_Entity_Handler)(
        Entity *p_entity_self, 
        Game *p_game,
        World *p_world);

typedef struct PLATFORM_File_System_Context_t PLATFORM_File_System_Context;
typedef struct Serialization_Request_t Serialization_Request;

typedef void (*m_Entity_Serialization_Handler)(
        Entity *p_entity_self, 
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Serialization_Request *p_serialization_request);

///
/// SECTION_input
///

typedef struct Input_t Input;

///
/// SECTION_process
///

typedef enum Process_Status_Kind {
    Process_Status_Kind__None = 0,
    Process_Status_Kind__Stopped,
    Process_Status_Kind__Idle,
    Process_Status_Kind__Busy,
    Process_Status_Kind__Stopping,
    Process_Status_Kind__Enqueued,
    Process_Status_Kind__Complete,
    Process_Status_Kind__Fail,
    Process_Status_Kind__Unknown
} Process_Status_Kind;

typedef enum Process_Kind {
    Process_Kind__None,
    Process_Kind__Generic,
    Process_Kind__Serialized,
    Process_Kind__Game_Action,
    Process_Kind__Unknown
} Process_Kind;

typedef struct Process_t Process;
typedef struct Process_Manager_t Process_Manager;

///
/// SECTION_inventory
///

typedef struct Item_t Item;
typedef struct Item_Stack_t Item_Stack;
typedef struct Inventory_t Inventory;

#include <types/implemented/item_kind.h>
#ifndef DEIFNE_ITEM_KIND
typedef enum Item_Kind {
    Item_Kind__None = 0,
    Item_Kind__Unknown
} Item_Kind;
#endif

/// 
/// SECTION_multiplayer
///

typedef struct IPv4_Address_t IPv4_Address;
typedef struct PLATFORM_TCP_Context_t PLATFORM_TCP_Context;
typedef struct PLATFORM_TCP_Socket_t PLATFORM_TCP_Socket;

typedef enum TCP_Socket_State {
    TCP_Socket_State__None = 0,
    TCP_Socket_State__Disconnected,
    TCP_Socket_State__Connecting,
    TCP_Socket_State__Connected,
    TCP_Socket_State__Authenticating,
    TCP_Socket_State__Authenticated,
    TCP_Socket_State__Unknown
} TCP_Socket_State;

typedef struct TCP_Socket_t TCP_Socket;
typedef struct TCP_Socket_Manager_t TCP_Socket_Manager;

/// 
/// SECTION_rendering
///

typedef struct Font_Letter_t Font_Letter;
typedef struct Font_t Font;
typedef struct Typer_t Typer;

///
/// This is an abstraction for a "sub-context" for graphics.
///
typedef struct PLATFORM_Graphics_Window_t PLATFORM_Graphics_Window;
typedef struct Graphics_Window_t Graphics_Window;

#include <types/implemented/graphics_window_kind.h>
#ifndef DEFINE_GRAPHICS_WINDOW_KIND
typedef enum Graphics_Window_Kind {
    Graphics_Window_Kind__None,
    Graphics_Window_Kind__Unknown
} Graphics_Window_Kind;
#endif

#include <types/implemented/sprite_animation_kind.h>
#ifndef DEFINE_SPRITE_ANIMATION_KIND
enum Sprite_Animation_Kind {
    Sprite_Animation_Kind__None,
    Sprite_Animation_Kind__Unknown
};
#endif

#include "types/implemented/sprite_kind.h"
#ifndef DEFINE_SPRITE_KIND
typedef enum Sprite_Kind {
    Sprite_Kind__None = 0,
    Sprite_Kind__Unknown
} Sprite_Kind;
#endif

typedef struct Sprite_t Sprite;
typedef struct Sprite_Allocation_Specification_t 
               Sprite_Allocation_Specification;
typedef struct Texture_Allocation_Specification_t
               Texture_Allocation_Specification;

///
/// SECTION_scene
///

#include <types/implemented/scene_kind.h>
#ifndef DEFINE_SCENE_KIND
typedef enum Scene_Kind {
    Scene_Kind__None,
    Scene_Kind__Test = Scene_Kind__None,
    Scene_Kind__Unknown
} Scene_Kind;
#endif

typedef struct Scene_t Scene;
typedef struct Scene_Manager_t Scene_Manager;

///
/// SECTION_serialization
///

typedef struct Serialized_Field_t Serialized_Field;
typedef struct Serialized_Field_t Serialized_Item_Stack_Ptr;
typedef struct Serialized_Field_t Serialized_Inventory_Ptr;
typedef struct Serialized_Field_t Serialized_Entity_Ptr;
typedef struct Serialized_Field_t Serialized_Chunk_Ptr;
typedef struct Serialization_Request_t Serialization_Request;

typedef enum IO_Access_Kind {
    IO_Access_Kind__None,
    IO_Access_Kind__File,
    IO_Access_Kind__Unknown,
} IO_Access_Kind;

typedef struct PLATFORM_Directory_t PLATFORM_Directory;

///
/// SECTION_sort
///

///
/// SECTION_ui
///

typedef uint8_t UI_Tile_Map__Flags;
typedef struct UI_Tile_Map__Wrapper_t UI_Tile_Map__Wrapper;
typedef struct UI_Tile_Span_t UI_Tile_Span;
typedef struct UI_Tile_Map__Small_t UI_Tile_Map__Small;
typedef struct UI_Tile_Map__Medium_t UI_Tile_Map__Medium;
typedef struct UI_Tile_Map__Large_t UI_Tile_Map__Large;

typedef enum UI_Tile_Map_Size {
    UI_Tile_Map_Size__None = 0,
    UI_Tile_Map_Size__Small,
    UI_Tile_Map_Size__Medium,
    UI_Tile_Map_Size__Large,
    UI_Tile_Map_Size__Unknown
} UI_Tile_Map_Size;

#include <types/implemented/ui_tile_kind.h>
#ifndef DEFINE_UI_TILE_KIND
typedef enum UI_Tile_Kind {
    UI_Tile_Kind__None = 0,
    UI_Tile_Kind__Unknown
} UI_Tile_Kind;
#endif

#include <types/implemented/ui_sprite_kind.h>
#ifndef DEFINE_UI_SPRITE_KIND
typedef enum UI_Sprite_Kind {
    UI_Sprite_Kind__None = 0,
    UI_Sprite_Kind__8x8,
    UI_Sprite_Kind__16x16 
        = UI_Sprite_Kind__8x8,
    UI_Sprite_Kind__32x32 
        = UI_Sprite_Kind__16x16,
    UI_Sprite_Kind__Unknown = UI_Sprite_Kind__32x32
} UI_Sprite_Kind;
#endif

typedef struct UI_Element_t UI_Element;
typedef struct UI_Manager_t UI_Manager;

#include <types/implemented/ui_element_kind.h>
#ifndef DEFINE_UI_ELEMENT_KIND
enum UI_Element_Kind {
    UI_Element_Kind__None,
    UI_Element_Kind__Button,
    UI_Element_Kind__Draggable,
    UI_Element_Kind__Slider,
    UI_Element_Kind__Drop_Zone,
    UI_Element_Kind__Logical,
    UI_Element_Kind__Unknown
};
#endif

///
/// SECTION_world
///

typedef struct World_t World;

typedef struct Global_Space_t Global_Space;
typedef struct Local_Space_t Local_Space;
typedef struct Local_Space_Manager_t Local_Space_Manager;

#include <types/implemented/tile_kind.h>
#ifndef DEFINE_TILE_KIND
typedef enum Tile_Kind {
    Tile_Kind__None = 0,
    Tile_Kind__Unknown
} Tile_Kind;
#endif

///
/// These specify the various kinds of Game_Actions
/// which can exist. m_Game_Action_Handler will
/// manage the game actions. 
///
/// See m_Game_Action_Handler for how you should
/// implement such a handler.
///
/// Extending:
/// You can add new kinds, but it must be of value greater
/// than or equal to Game_Action_Kind__Custom, and less than 
/// the value of Game_Action_Kind__Unknown.
///
#include <types/implemented/game_action_kind.h>
#ifndef DEFINE_GAME_ACTION_KIND
typedef enum Game_Action_Kind {
    Game_Action_Kind__None = 0,
    Game_Action_Kind__Bad_Request,
    Game_Action_Kind__TCP_Connect__Begin,
    Game_Action_Kind__TCP_Connect,
    Game_Action_Kind__TCP_Connect__Reject,
    Game_Action_Kind__TCP_Connect__Accept,
    Game_Action_Kind__TCP_Disconnect,
    Game_Action_Kind__TCP_Delivery,
    Game_Action_Kind__Global_Space__Request,
    Game_Action_Kind__Global_Space__Resolve,
    Game_Action_Kind__Global_Space__Store,
    Game_Action_Kind__Inventory__Request,
    Game_Action_Kind__Inventory__Resolve,
    Game_Action_Kind__Entity__Spawn,
    Game_Action_Kind__Entity__Set_Flag,
    Game_Action_Kind__Entity__Action,
    Game_Action_Kind__Hitbox__Set_Position,
    Game_Action_Kind__Hitbox__Apply_Velocity,
    Game_Action_Kind__Custom,

    ///
    /// Custom Game Actions YOU define for YOUR GAME go here.
    ///

    Game_Action_Kind__Unknown
} Game_Action_Kind;
#endif

typedef struct Camera_t Camera;
typedef struct Chunk_Manager_t Chunk_Manager;
typedef struct Chunk_t Chunk;
typedef struct Chunk_Manager__Chunk_Map_Node_t Chunk_Manager__Chunk_Map_Node;
typedef struct Tile_t Tile;

typedef struct Tile_Render_Kernel_Result_t Tile_Render_Kernel_Result;

///
/// Examines area local, possibly changing the tile to be rendered.
///
typedef void (*f_Tile_Render_Kernel)(
        Local_Space *p_local_space,
        Tile_Render_Kernel_Result *p_tile_kernel_render_results,
        Quantity__u32 quantity_of__tile_kernel_render_results,
        u8 x__local,
        u8 y__local,
        u8 z__local);

///
/// SECTION_core
///

///
/// This is mainly used to perform UUID branding, but some types
/// listed here do not undergo uuid branding.
///
typedef enum Lavender_Type {
    Lavender_Type__None = 0,
    Lavender_Type__Aliased_Texture,
    Lavender_Type__Sprite,
    Lavender_Type__Hitbox,
    Lavender_Type__UI_Element,
    Lavender_Type__Entity,
    Lavender_Type__Game_Action,
    Lavender_Type__Inventory,

    // no uuid branding:
    Lavender_Type__Chunk,
    Lavender_Type__Collision_Node,
    Lavender_Type__Global_Space,

    Lavender_Type__Unknown = 0b111111 // not expecting more than 63 types.
} Lavneder_Type;

typedef struct Game_t Game;
typedef struct Game_Action_t Game_Action;

///
/// SECTION_platform
///

typedef struct PLATFORM_File_System_Context_t PLATFORM_File_System_Context;
typedef struct PLATFORM_Audio_Context_t PLATFORM_Audio_Context;
typedef struct PLATFORM_Gfx_Context_t PLATFORM_Gfx_Context;
typedef struct PLATFORM_Texture_t PLATFORM_Texture;
typedef struct PLATFORM_Sprite_t PLATFORM_Sprite;
typedef struct PLATFORM_Sprite_Data_t PLATFORM_Sprite_Data;

typedef struct Gfx_Context_t Gfx_Context;

#endif
