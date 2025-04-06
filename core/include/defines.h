#ifndef DEFINES_H
#define DEFINES_H

#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include "util/bitmap/bitmap.h"
#include <stdbool.h>
#include <stdint.h>
#ifndef NDEBUG
#include <debug/debug.h>
#endif

///
/// This file has the definition of EVERY struct
/// macro, and typedef used in core!
///
/// Need help finding something? Everything is
/// organized by PRIMARY usage within the ./include
/// and ./source folders. So, for example, if you wanted
/// to find structs primarily used in the "world" folder
/// you should search for SECTION_World.
///
/// For base level files, search for SECTION_core.
///
/// NOTE:
/// SECTION_defines is for definitions which only
/// have PRIMARY usage in defines.h .
///
/// NOTE:
/// Every single struct, macro, and typedef has a forward
/// declaration in defines_weak.h . If you add a new
/// struct, macro, or typedef you SHOULD include a forward
/// definition of that type in defines_weak.h
///

#include <defines_weak.h>
#include <platform.h>

///
/// SECTION_defines
///

typedef int32_t     i32;
typedef int16_t     i16;
typedef int8_t      i8;

#define FRACTIONAL_PERCISION_4__BIT_SIZE 4
#define FRACTIONAL_PERCISION_8__BIT_SIZE 8
#define FRACTIONAL_PERCISION_16__BIT_SIZE 16
#define FRACTIONAL_PERCISION_20__BIT_SIZE 20
/// FIXED POINT fractional, with 4 bits of percision.
typedef int32_t     i32F4;
typedef int16_t     i16F4;
typedef int8_t     i8F4;
typedef uint32_t    u32F4;
typedef uint16_t    u16F4;
typedef uint8_t    u8F4;

typedef int32_t     i32F20;

typedef uint32_t     u32F20;

#define I32F4_MAX ((uint32_t)BIT(31)-1)
#define I32F4_MIN BIT(31)

/// 
/// Vector__3i32F4 is a 3-tuple of 32 bit FIXED POINT
/// fractional integers with 4 bits of percision.
///
/// To get a whole number, use ENTITY_CHUNK_LOCAL_SPACE__BIT_MASK
/// and shift the result to the right by ENTITY_VELOCITY_FRACTIONAL__BIT_SIZE.
///
typedef struct Vector__3i32F4_t {
    i32F4 x__i32F4, y__i32F4, z__i32F4;
} Vector__3i32F4;

typedef struct Vector__3i32F20_t {
    i32F20 x__i32F20, y__i32F20, z__i32F20;
} Vector__3i32F20;

typedef int32_t Signed_Index__i32;
typedef int16_t Signed_Index__i16;
typedef int8_t  Signed_Index__i8;

///
/// Has three int32_t components.
///
typedef struct Vector__3i32_t {
    Signed_Index__i32 x__i32, 
                      y__i32, 
                      z__i32;
} Vector__3i32;

// TODO: remove
typedef struct Vector__3i32_t Chunk_Vector__3i32;

typedef struct Vector__3i32_t Global_Space_Vector__3i32;
typedef struct Vector__3i32_t Tile_Vector__3i32;

typedef uint32_t Psuedo_Random_Seed__u32;
typedef int32_t Psuedo_Random__i32;
typedef uint32_t Psuedo_Random__u32;

typedef struct Repeatable_Psuedo_Random_t {
    Psuedo_Random_Seed__u32 seed__initial;
    Psuedo_Random_Seed__u32 seed__current_random;
} Repeatable_Psuedo_Random;

typedef struct Timer__u32_t {
    uint32_t remaining__u32;
    uint32_t start__u32;
} Timer__u32;
typedef struct Timer__u16_t {
    uint16_t remaining__u16;
    uint16_t start__u16;
} Timer__u16;
typedef struct Timer__u8_t {
    uint8_t remaining__u8;
    uint8_t start__u8;
} Timer__u8;

typedef struct Date_Time_t {
    union {
        struct {
            u8  seconds      :6;
            u8  minutes      :6;
            u8  hours        :5;
            u8  days         :5;
            u8  months       :4;
            u8               :6;
            u32 years;
        };
        u32 date_time__sec_min_hour_day_month;
        u32 date_time__years;
    };
} Date_Time;

typedef uint8_t Direction__u8;
typedef uint16_t Degree__u9;

#define ANGLE__0        0
#define ANGLE__27_5     32
#define ANGLE__45       64
#define ANGLE__90       128
#define ANGLE__180      256
#define ANGLE__270      384
///
/// Use this for bounds checking only!
///
#define ANGLE__360  512
#define ANGLE__MASK MASK(5)
#define ANGLE__OUT_OF_BOUNDS (uint16_t)(-1)
#define LENGTH_OF_RAY__i32F20 0b11111111

typedef struct Ray__3i32F20_t {
    Vector__3i32F20 ray_starting_vector__3i32F20;
    Vector__3i32F20 ray_current_vector__3i32F20;
    Degree__u9 angle_of__ray;
} Ray__3i32F20;

#define INDEX__UNKNOWN__u32 (uint32_t)(-1)
#define INDEX__UNKNOWN__u16 (uint16_t)(-1)
#define INDEX__UNKNOWN__u8 (uint8_t)(-1)
typedef uint8_t Index__u8;
typedef uint16_t Index__u16;
typedef uint32_t Index__u32;

typedef struct Vector__3u8_t {
    Index__u8 x__u8, y__u8, z__u8;
} Vector__3u8;

#define QUANTITY__UNKNOWN__u32 (uint32_t)(-1)
#define QUANTITY__UNKNOWN__u16 (uint16_t)(-1)
#define QUANTITY__UNKNOWN__u8 (uint8_t)(-1)
typedef uint8_t Quantity__u8;
typedef uint16_t Quantity__u16;
typedef uint32_t Quantity__u32;

typedef int8_t  Signed_Quantity__i8;
typedef int16_t Signed_Quantity__i16;
typedef int32_t Signed_Quantity__i32;

#define IDENTIFIER__UNKNOWN__u64 (uint64_t)(-1)
#define IDENTIFIER__UNKNOWN__u32 (uint32_t)(-1)
#define IDENTIFIER__UNKNOWN__u16 (uint16_t)(-1)
#define IDENTIFIER__UNKNOWN__u8 (uint8_t)(-1)
typedef uint32_t Identifier__u32;
typedef uint16_t Identifier__u16;
typedef uint8_t Identifier__u8;

typedef struct Chunk_Identifier__u32_t {
    Identifier__u16     x__chunk_identifier__u16;
    Identifier__u16     y__chunk_identifier__u16;
} Chunk_Identifier__u32;

#define DIRECTION__NONE         0
#define DIRECTION__NORTH        BIT(0)
#define DIRECTION__EAST         BIT(1)
#define DIRECTION__SOUTH        BIT(2)
#define DIRECTION__WEST         BIT(3)
#define DIRECTION__UPWARDS      BIT(4)
#define DIRECTION__DOWNWARDS    BIT(5)

#define DIRECTION__ANY      MASK(6)
#define DIRECTION__NORTH_EAST (DIRECTION__NORTH \
        | DIRECTION__EAST)
#define DIRECTION__NORTH_WEST (DIRECTION__NORTH \
        | DIRECTION__WEST)
#define DIRECTION__SOUTH_EAST (DIRECTION__SOUTH \
        | DIRECTION__EAST)
#define DIRECTION__SOUTH_WEST (DIRECTION__SOUTH \
        | DIRECTION__WEST)

#define DIRECTION__NORTH_UPWARDS (DIRECTION__NORTH \
        | DIRECTION__UPWARDS)
#define DIRECTION__NORTH_UPWARDS (DIRECTION__NORTH \
        | DIRECTION__UPWARDS)
#define DIRECTION__SOUTH_UPWARDS (DIRECTION__SOUTH \
        | DIRECTION__UPWARDS)
#define DIRECTION__SOUTH_UPWARDS (DIRECTION__SOUTH \
        | DIRECTION__UPWARDS)

#define DIRECTION__NORTH_DOWNWARDS (DIRECTION__NORTH \
        | DIRECTION__DOWNWARDS)
#define DIRECTION__NORTH_DOWNWARDS (DIRECTION__NORTH \
        | DIRECTION__DOWNWARDS)
#define DIRECTION__SOUTH_DOWNWARDS (DIRECTION__SOUTH \
        | DIRECTION__DOWNWARDS)
#define DIRECTION__SOUTH_DOWNWARDS (DIRECTION__SOUTH \
        | DIRECTION__DOWNWARDS)

#define DIRECTION__NORTH_EAST_UPWARDS (DIRECTION__NORTH \
        | DIRECTION__EAST\
        | DIRECTION__UPWARDS)
#define DIRECTION__NORTH_WEST_UPWARDS (DIRECTION__NORTH \
        | DIRECTION__WEST\
        | DIRECTION__UPWARDS)
#define DIRECTION__SOUTH_EAST_UPWARDS (DIRECTION__SOUTH \
        | DIRECTION__EAST\
        | DIRECTION__UPWARDS)
#define DIRECTION__SOUTH_WEST_UPWARDS (DIRECTION__SOUTH \
        | DIRECTION__WEST\
        | DIRECTION__UPWARDS)

#define DIRECTION__NORTH_EAST_DOWNWARDS (DIRECTION__NORTH \
        | DIRECTION__EAST\
        | DIRECTION__DOWNWARDS)
#define DIRECTION__NORTH_WEST_DOWNWARDS (DIRECTION__NORTH \
        | DIRECTION__WEST\
        | DIRECTION__DOWNWARDS)
#define DIRECTION__SOUTH_EAST_DOWNWARDS (DIRECTION__SOUTH \
        | DIRECTION__EAST\
        | DIRECTION__DOWNWARDS)
#define DIRECTION__SOUTH_WEST_DOWNWARDS (DIRECTION__SOUTH \
        | DIRECTION__WEST\
        | DIRECTION__DOWNWARDS)

///
/// SECTION_serialization
///

///
/// This must be the FIRST field to appear
/// in a serialized struct.
///
typedef struct Serialization_Header_t {
    Quantity__u32       size_of__struct;
    Identifier__u32     uuid;
} Serialization_Header;

typedef struct Serialization_Header__UUID_64_t {
    Quantity__u32       size_of__struct;
    Identifier__u64     uuid;
} Serialization_Header__UUID_64;

typedef struct Serialization_Pool_t {
    Quantity__u32 quantity_of__pool_elements;
    Quantity__u32 size_of__element;
    Serialization_Header *p_headers;
} Serialization_Pool;

typedef struct Serialized_Field_t {
    union {
        struct {
            Serialization_Header _serialization_header;
        };
        struct {
            Identifier__u32 identifier_for__serialized_field;
            Quantity__u32   :32;
        };
    };
    union {
        struct {
            void *p_serialized_field__data;
        };
        struct {
            Serialization_Header *p_serialized_field__serialization_header;
        };
        struct {
            Entity *p_serialized_field__entity;
        };
        struct {
            Inventory *p_serialized_field__inventory;
        };
        struct {
            Item_Stack *p_serialized_field__item_stack;
        };
        struct {
            Chunk *p_serialized_field__chunk;
        };
    };
} Serialized_Field;

#define SERIALIZATION_REQUEST_FLAGS__NONE 0
#define SERIALZIATION_REQUEST_FLAG__IS_ALLOCATED BIT(0)
#define SERIALZIATION_REQUEST_FLAG__IS_ACTIVE BIT(1)
#define SERIALZIATION_REQUEST_FLAG__USE_SERIALIZER_OR_BUFFER BIT(2)
#define SERIALIZATION_REQUEST_FLAG__READ_OR_WRITE BIT(3)
#define SERIALIZATION_REQUEST_FLAG__KEEP_ALIVE BIT(4)
#define SERIALIZATION_REQUEST_FLAG__IS_TCP_OR_IO BIT(5)

typedef uint8_t Serialization_Request_Flags;

typedef struct Serialization_Request_t {
    void *p_data;
    Serialization_Header *p_serialization_header;
    union {
        void *p_file_handler;
        struct {
            u8 *p_tcp_packet_destination;
            u8 *pM_packet_bitmap;
            Quantity__u16 quantity_of__bytes_in__destination;
            Quantity__u16 quantity_of__tcp_packets__anticipated;
        };
    };
    Serialization_Request_Flags serialization_request_flags;
} Serialization_Request;

///
/// SECTION_audio
///

typedef u8 Audio_Flags__u8;

#define AUDIO_FLAGS__NONE 0
#define AUDIO_FLAG__IS_ACTIVE BIT(0)
#define AUDIO_FLAG__RELEASE_ON_COMPLETE BIT(1)
#define AUDIO_FLAG__IS_LOOPING BIT(2)

typedef struct Audio_Effect_t {
    void                    *p_audio_instance_handle;
    Timer__u32              timer_for__audio;
    enum Audio_Effect_Kind  the_kind_of__audio_effect;
    Audio_Flags__u8         audio_flags__u8;
} Audio_Effect;

///
/// SECTION_collisions
///

typedef struct Hitbox_AABB_t {
    Serialization_Header _serialization_header;
    Vector__3i32F4 position__3i32F4;
    Vector__3i32F4 velocity__3i32F4;
    Quantity__u32 width__quantity_u32;
    Quantity__u32 height__quantity_u32;
} Hitbox_AABB;

#define MAX_QUANTITY_OF__HITBOX_AABB 128

typedef struct Hitbox_AABB_Manager_t {
    Hitbox_AABB hitboxes[MAX_QUANTITY_OF__HITBOX_AABB];
} Hitbox_AABB_Manager;

/// When checking the distance between two collisions along each axis
/// anything equal to or less than this value is ignored when determining
/// displacement. This useful threshold is what allows a colliding player
/// to move up while an entity is moving into them from the right.
#define COLLISION_DELTA_THRESHOLD 4096
#define COLLISION_MANAGER__LAYER_TWO__CHUNK_CENTER_OFFSET \
    (CHUNK_MANAGER__QUANTITY_OF_CHUNKS__PER_ROW / 4)
#define COLLISION_MANAGER__LAYER_THREE__CHUNK_CENTER_OFFSET \
    (CHUNK_MANAGER__QUANTITY_OF_CHUNKS__PER_ROW / 8)

typedef struct Collision_Node_Record_t {
    Hitbox_AABB *p_hitbox;
    Serialized_Field s_data;
} Collision_Node_Record;

typedef void f_Collision_Handler(
        Game *p_game,
        Serialization_Header *p_source,
        Hitbox_AABB *p_hitbox__colliding,
        Serialized_Field *ps_record__collided,
        Hitbox_AABB *p_hitbox__collided,
        Direction__u8 direction_of__collision);

typedef void f_Foreach_Serialized_Field(
        Game *p_game,
        Serialized_Field *p_serialized_field,
        void *p_data);

///
/// This type is specific to Collision_Manager,
/// so there is no header files supporting it.
///
typedef struct Collision_Manager__Collision_Node_t {
    Collision_Node_Record collision_node_records[
        ENTITY_MAXIMUM_QUANTITY_OF__COLLIDABLE];

    struct Collision_Manager__Collision_Node_t *p_north__collision_node;
    struct Collision_Manager__Collision_Node_t *p_east__collision_node;
    struct Collision_Manager__Collision_Node_t *p_south__collision_node;
    struct Collision_Manager__Collision_Node_t *p_west__collision_node;

    Direction__u8 legal_directions;
} Collision_Manager__Collision_Node;

#define MAX_QUANTITY_OF__COLLISION_NODE__RECORD_POOLS

typedef struct Collision_Node_Entry_t {
    Serialized_Field s_hitbox;
    struct Collision_Node_Entry_t *p_previous_entry;
} Collision_Node_Entry;

typedef struct Collision_Node_t {
    Serialization_Header__UUID_64 _serialization_header;
    Collision_Node_Entry *p_linked_list__collision_node_entries__tail;
} Collision_Node;

typedef struct Collision_Node_Pool_t {
    Collision_Node collision_nodes[QUANTITY_OF__GLOBAL_SPACE];
    Collision_Node_Entry collision_node_entries[MAX_QUANTITY_OF__HITBOX_AABB];
} Collision_Node_Pool;

///
/// 4 Collision Nodes per layer 3 node.
///
typedef struct Collision_Manager__Layer_Three_t {
    Collision_Manager__Collision_Node *p_top_left__collision_node;
    Collision_Manager__Collision_Node *p_top_right__collision_node;
    Collision_Manager__Collision_Node *p_bottom_left__collision_node;
    Collision_Manager__Collision_Node *p_bottom_right__collision_node;

    Signed_Index__i32 
        x__center_chunk__signed_index_i32, 
        y__center_chunk__signed_index_i32;
} Collision_Manager__Layer_Three;

typedef struct Collision_Manager__Layer_Two_t {
    Collision_Manager__Layer_Three top_left__layer_three;
    Collision_Manager__Layer_Three top_right__layer_three;
    Collision_Manager__Layer_Three bottom_left__layer_three;
    Collision_Manager__Layer_Three bottom_right__layer_three;

    Signed_Index__i32 
        x__center_chunk__signed_index_i32, 
        y__center_chunk__signed_index_i32;
} Collision_Manager__Layer_Two;

typedef struct Collision_Manager__t {
    Collision_Manager__Collision_Node collision_nodes[
        CHUNK_MANAGER__QUANTITY_OF_CHUNKS];

    Collision_Manager__Layer_Two top_left__layer_two;
    Collision_Manager__Layer_Two top_right__layer_two;
    Collision_Manager__Layer_Two bottom_left__layer_two;
    Collision_Manager__Layer_Two bottom_right__layer_two;

    Collision_Manager__Collision_Node *p_most_north_western__collision_node;

    Signed_Index__i32 
        x__center_chunk__signed_index_i32, 
        y__center_chunk__signed_index_i32;
} Collision_Manager;

///
/// SECTION_debug
///

///
/// SECTION_rendering
///

typedef uint8_t Sprite_Frame_Index__u8;
typedef uint16_t Sprite_Frame_Index__u16;

#define ANIMATION_BIT_MASK__TICK_RATE MASK(4)

typedef struct Sprite_Wrapper_t {
    PLATFORM_Sprite *p_sprite;
    Timer__u32 animation_timer__u32;
    Direction__u8 direction;
    Direction__u8 direction__requested;
    Sprite_Frame_Index__u16 frame__initial;
    Sprite_Frame_Index__u16 frame__current;
    Sprite_Frame_Index__u16 frame__final;
    enum Sprite_Animation_Kind the_kind_of_animation__this_sprite_has;
} Sprite_Wrapper;

typedef bool (*f_Sprite_Gfx_Allocator)(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Sprite_Wrapper *p_sprite_wrapper,
        u32 enum_value);

typedef struct Sprite_Gfx_Allocation_Manager_t {
    f_Sprite_Gfx_Allocator F_sprite_gfx_allocators_for__entities[
        Entity_Kind__Unknown];
    f_Sprite_Gfx_Allocator F_sprite_gfx_allocators_for__ui[
        UI_Sprite_Kind__Unknown];
    f_Sprite_Gfx_Allocator F_sprite_gfx_allocators_for__items[
        Item_Kind__Unknown];
} Sprite_Gfx_Allocation_Manager;

#define SPRITE_FRAME__32x32__OFFSET (32 * 32)
#define SPRITE_FRAME__16x16__OFFSET (16 * 16)
#define SPRITE_FRAME__8x8__OFFSET (8 * 8)

#define SPRITE_FRAME_WIDTH__ENTITY_HUMANOID_ARMORED 16
#define SPRITE_FRAME_HEIGHT__ENTITY_HUMANOID_ARMORED 16

#define SPRITE_FRAME_WIDTH__ENTITY_HUMANOID_UNARMORED 6
#define SPRITE_FRAME_HEIGHT__ENTITY_HUMANOID_UNARMORED 4

#define SPRITE_FRAME_COL__ENTITY_HUMANOID__IDLE 0
#define SPRITE_FRAME_COL__ENTITY_HUMANOID__WALK 1
#define SPRITE_FRAME_COL__ENTITY_HUMANOID__USE 3
#define SPRITE_FRAME_COL__ENTITY_HUMANOID__HURT 0
#define SPRITE_FRAME_COL__ENTITY_HUMANOID__DIE 1
#define SPRITE_FRAME_COL__ENTITY_HUMANOID__SLEEP 3

#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__IDLE 0
#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__WALK 2
#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__USE 2
#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__HURT 1
#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__DIE 2
#define SPRITE_ANIMATION_FRAME_COUNT__ENTITY_HUMANOID__SLEEP 0

#define SPRITE_FRAME_ROW__ENTITY_HUMANOID__SIDE_FACING 0
#define SPRITE_FRAME_ROW__ENTITY_HUMANOID__FORWARD_FACING 1
#define SPRITE_FRAME_ROW__ENTITY_HUMANOID__BACK_FACING 2
#define SPRITE_FRAME_ROW__ENTITY_HUMANOID__FALLING 3

#define SPRITE_FRAME_COL_GROUP_OFFSET__ENTITY_HUMANOID 6
#define SPRITE_FRAME_ROW_GROUP_OFFSET__ENTITY_HUMANOID (3*16)

#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_CLOTH 1
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_IRON 2
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_IRON__RUSTED 3
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_STEEL 4
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_STEEL__DIAMOND 5
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_STEEL__AMETHYST 6
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_GOLD 7
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_GOLD__DIAMOND 8
#define SPRITE_FRAME_GROUP_INDEX__ENTITY_HUMANOID__ARMOR_GOLD__AMETHYST 9

///
/// The meaning of these flags is dependent on
/// platform_defines.h
///
typedef uint32_t Texture_Flags;

#define TEXTURE_FLAGS__NONE 0

///
/// TEXTURE_FLAGS:
/// Bit orderings, from most significant to least:
/// [32 <-> 14 bits,    PLATFORM specific flags]
/// [13th bit,          is hidden]
/// [12-10 bits,        format]
/// [9-7 bits,          render method] 
/// [6-4 bits,          width] 
/// [3-1 bits,          height]
///

// Just a width or height component of an image.
#define TEXTURE_FLAG__LENGTH__BIT_COUNT 3
#define TEXTURE_FLAG__LENGTH__MASK \
    MASK(TEXTURE_FLAG__LENGTH__BIT_COUNT)
// The width and height component of the image
#define TEXTURE_FLAG__SIZE__BIT_COUNT 6
#define TEXTURE_FLAG__SIZE__MASK \
    MASK(TEXTURE_FLAG__SIZE__BIT_COUNT)

// Texture length specifiers
#define TEXTURE_FLAG__LENGTH_x8       0b000
#define TEXTURE_FLAG__LENGTH_x16    (1+\
        TEXTURE_FLAG__LENGTH_x8)    //0b001
#define TEXTURE_FLAG__LENGTH_x32    (1+\
        TEXTURE_FLAG__LENGTH_x16)   //0b010
#define TEXTURE_FLAG__LENGTH_x64    (1+\
        TEXTURE_FLAG__LENGTH_x32)   //0b011
#define TEXTURE_FLAG__LENGTH_x128   (1+\
        TEXTURE_FLAG__LENGTH_x64)   //0b100
#define TEXTURE_FLAG__LENGTH_x256   (1+\
        TEXTURE_FLAG__LENGTH_x128)  //0b101
#define TEXTURE_FLAG__LENGTH_x512   (1+\
        TEXTURE_FLAG__LENGTH_x256)  //0b110

// Texture size specifiers
// Add these combinations in as needed:
#define TEXTURE_FLAG__SIZE_8x8 \
    TEXTURE_FLAG__LENGTH_x8 \
    | (TEXTURE_FLAG__LENGTH_x8 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_8x16 \
    TEXTURE_FLAG__LENGTH_x8 \
    | (TEXTURE_FLAG__LENGTH_x16 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_8x32 \
    TEXTURE_FLAG__LENGTH_x8 \
    | (TEXTURE_FLAG__LENGTH_x32 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_16x8 \
    TEXTURE_FLAG__LENGTH_x16 \
    | (TEXTURE_FLAG__LENGTH_x8 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_16x16 \
    TEXTURE_FLAG__LENGTH_x16 \
    | (TEXTURE_FLAG__LENGTH_x16 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_16x32 \
    TEXTURE_FLAG__LENGTH_x16 \
    | (TEXTURE_FLAG__LENGTH_x32 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_32x8 \
    TEXTURE_FLAG__LENGTH_x32 \
    | (TEXTURE_FLAG__LENGTH_x8 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_32x16 \
    TEXTURE_FLAG__LENGTH_x32 \
    | (TEXTURE_FLAG__LENGTH_x16 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_32x32 \
    TEXTURE_FLAG__LENGTH_x32 \
    | (TEXTURE_FLAG__LENGTH_x32 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_32x64 \
    TEXTURE_FLAG__LENGTH_x32 \
    | (TEXTURE_FLAG__LENGTH_x64 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_64x64 \
    TEXTURE_FLAG__LENGTH_x64 \
    | (TEXTURE_FLAG__LENGTH_x64 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_128x128 \
    TEXTURE_FLAG__LENGTH_x128 \
    | (TEXTURE_FLAG__LENGTH_x128 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_256x256 \
    TEXTURE_FLAG__LENGTH_x256 \
    | (TEXTURE_FLAG__LENGTH_x256 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_512x256 \
    TEXTURE_FLAG__LENGTH_x256 \
    | (TEXTURE_FLAG__LENGTH_x512 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_256x512 \
    TEXTURE_FLAG__LENGTH_x512 \
    | (TEXTURE_FLAG__LENGTH_x256 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)
#define TEXTURE_FLAG__SIZE_512x512 \
    TEXTURE_FLAG__LENGTH_x512 \
    | (TEXTURE_FLAG__LENGTH_x512 << \
            TEXTURE_FLAG__LENGTH__BIT_COUNT)

// We support up to 8 texture render methods 
// (on nds, this is oamMain, oamSub)
#define TEXTURE_FLAG__RENDER_METHOD__BIT_SHIFT (\
        TEXTURE_FLAG__LENGTH__BIT_COUNT << 1)
#define TEXTURE_FLAG__RENDER_METHOD__BIT_COUNT 3
#define TEXTURE_FLAG__RENDER_METHOD__MASK \
    MASK(TEXTURE_FLAG__RENDER_METHOD__BIT_COUNT)
#define TEXTURE_FLAG__RENDER_METHOD__0 0b000
#define TEXTURE_FLAG__RENDER_METHOD__1 0b001
#define TEXTURE_FLAG__RENDER_METHOD__2 0b010
#define TEXTURE_FLAG__RENDER_METHOD__3 0b011
#define TEXTURE_FLAG__RENDER_METHOD__4 0b100
#define TEXTURE_FLAG__RENDER_METHOD__5 0b101
#define TEXTURE_FLAG__RENDER_METHOD__6 0b110
#define TEXTURE_FLAG__RENDER_METHOD__7 0b111

// We support up to 8 texture formats 
// Replace 1-7 as needed.
#define TEXTURE_FLAG__FORMAT__BIT_SHIFT (\
        TEXTURE_FLAG__RENDER_METHOD__BIT_SHIFT\
        + TEXTURE_FLAG__RENDER_METHOD__BIT_COUNT)
#define TEXTURE_FLAG__FORMAT__BIT_COUNT 3
#define TEXTURE_FLAG__FORMAT__MASK \
    MASK(TEXTURE_FLAG__FORMAT__BIT_COUNT)
#define TEXTURE_FLAG__FORMAT__15_RGB 0b000
#define TEXTURE_FLAG__FORMAT__1 0b001
#define TEXTURE_FLAG__FORMAT__2 0b010
#define TEXTURE_FLAG__FORMAT__3 0b011
#define TEXTURE_FLAG__FORMAT__4 0b100
#define TEXTURE_FLAG__FORMAT__5 0b101
#define TEXTURE_FLAG__FORMAT__6 0b110
#define TEXTURE_FLAG__FORMAT__7 0b111

#define TEXTURE_FLAGS(size, method, format)\
    (\
        (\
            method << TEXTURE_FLAG__RENDER_METHOD__BIT_SHIFT\
        )\
        | (\
            format << TEXTURE_FLAG__FORMAT__BIT_SHIFT\
        )\
        | size\
    )

#define TEXTURE_FLAG__CORE_FLAGS__BIT_COUNT 8

#define TEXTURE_FLAG__BIT_SHIFT__CORE_FLAGS \
    (TEXTURE_FLAG__RENDER_METHOD__BIT_COUNT \
           + TEXTURE_FLAG__SIZE__BIT_COUNT \
           + TEXTURE_FLAG__FORMAT__BIT_COUNT)

#define TEXTURE_FLAG__IS_HIDDEN \
    BIT(TEXTURE_FLAG__BIT_SHIFT__CORE_FLAGS)
#define TEXTURE_FLAG__IS_ALLOCATED \
    BIT(TEXTURE_FLAG__BIT_SHIFT__CORE_FLAGS + 1)
#define TEXTURE_FLAG__IS_READONLY \
    BIT(TEXTURE_FLAG__BIT_SHIFT__CORE_FLAGS + 2)

#define TEXTURE_FLAG__BIT_SHIFT__GENERAL_FLAGS \
    (TEXTURE_FLAG__BIT_SHIFT__CORE_FLAGS \
     + TEXTURE_FLAG__CORE_FLAGS__BIT_COUNT)

#define GET_TEXTURE_FLAG__LENGTH__WIDTH(flags) \
    ((flags & (TEXTURE_FLAG__LENGTH__MASK \
              << TEXTURE_FLAG__LENGTH__BIT_COUNT)) \
              >> TEXTURE_FLAG__LENGTH__BIT_COUNT)

#define GET_TEXTURE_FLAG__LENGTH__HEIGHT(flags) \
    (flags & TEXTURE_FLAG__LENGTH__MASK)

typedef struct Texture_Allocation_Specification_t {
    PLATFORM_Graphics_Window *p_PLATFORM_graphics_window;
    void *p_texture_allocation_specification__data;
    Texture_Flags texture_flags;
} Texture_Allocation_Specification;

#define MAX_LENGTH_OF__TEXTURE_NAME 32
typedef char Texture_Name__c_str[MAX_LENGTH_OF__TEXTURE_NAME];

typedef struct Aliased_Texture_t {
    Texture_Name__c_str name_of__texture__c_str;
    PLATFORM_Texture *P_PLATFORM_texture;
} Aliased_Texture;

#define MAX_QUANTITY_OF__ALIASED_TEXTURES 128

///
/// Takes ownership of named textures.
///
typedef struct Aliased_Texture_Manager_t {
    Aliased_Texture aliased_textures[MAX_QUANTITY_OF__ALIASED_TEXTURES];
} Aliased_Texture_Manager;

typedef uint8_t Sprite_Flags;

#define SPRITE_FLAGS__NONE 0

#define SPRITE_FLAG__BIT_SHIFT_IS_ALLOCATED 0
#define SPRITE_FLAG__BIT_IS_ALLOCATED BIT(\
        SPRITE_FLAG__BIT_SHIFT_IS_ALLOCATED)

typedef struct Sprite_Allocation_Specification_t {
    enum Sprite_Allocation_Kind the_kind_of__sprite_allocation;
    Texture_Allocation_Specification texture_allocation_specification;
    union {
        struct { // Sprite_Allocation_Kind__Entity
            enum Entity_Kind the_kind_of__entity_this__sprite_is;
        };
        struct { // Sprite_Allocation_Kind__Item
            enum Item_Kind the_kind_of__item_this__sprite_is;
        };
        struct { // Sprite_Allocation_Kind__UI
            enum UI_Sprite_Kind the_kind_of__ui__this_sprite_is;
        };
        struct { // Sprite_Allocation_Kind__Graphics_Pointer
            void *p_gfx;
        };
    };
} Sprite_Allocation_Specification;

typedef struct Font_Letter_t {
    Quantity__u8 width_of__font_letter       :4;
    Quantity__u8 height_of__font_letter      :4;
    Quantity__u8 x__offset_of__font_letter   :4;
    Quantity__u8 y__offset_of__font_letter   :4;
    Index__u16 index_of__character__in_font :16;
} Font_Letter;

#define FONT_LETTER_MAX_QUANTITY_OF 256

typedef u8 Font_Flags;

#define FONT_FLAGS__NONE 0
#define FONT_FLAG__IS_ALLOCATED BIT(0)

typedef struct Font_t {
    Font_Letter font_lookup_table[
        FONT_LETTER_MAX_QUANTITY_OF];
    PLATFORM_Texture *p_PLATFORM_texture_of__font;
    Quantity__u8 max_width_of__font_letter;
    Quantity__u8 max_height_of__font_letter;
    Font_Flags font_flags;
} Font;

#define MAX_QUANTITY_OF__FONT 8

typedef struct Font_Manager_t {
    Font fonts[MAX_QUANTITY_OF__FONT];
} Font_Manager;

#define FONT_SMALL__MAX_WIDTH 4
#define FONT_SMALL__MAX_HEIGHT 6

#define FONT_LARGE__MAX_WIDTH 8
#define FONT_LARGE__MAX_HEIGHT 8

#define FONT_MAX_QUANTITY_OF 2
#define TYPER_MAX_QUANTITY_OF 2

#define MESSAGE_MAX_LENGTH_OF 96
#define MESSAGE_NAME_MAX_LENGTH_OF 16

typedef struct Message_t {
    Serialization_Header _serialization_header;
    unsigned char message__title[
        MESSAGE_NAME_MAX_LENGTH_OF];
    unsigned char message__body[
        MESSAGE_MAX_LENGTH_OF];
    Quantity__u8 length_of__message__title;
    Quantity__u8 length_of__message__body;
    Index__u8 index_of__body;
} Message;

#define MESSAGE_MAX_QUANTITY_OF 32

typedef struct Log_t {
    Message messages[MESSAGE_MAX_QUANTITY_OF];
    Message *p_next_message;
    Message *p_oldest_message;
} Log;

typedef struct Typer_t {
    Hitbox_AABB text_bounding_box;
    Vector__3i32 cursor_position__3i32;
    Font *p_font;
    PLATFORM_Texture *p_PLATFORM_texture__typer_target;
} Typer;

///
/// SECTION_inventory
///

typedef struct Item_t Item;

typedef struct Item_t {
    enum Item_Kind      the_kind_of_item__this_item_is;
} Item;

typedef struct Item_Manager_t {
    Item item_templates[(u16)Item_Kind__Unknown];
} Item_Manager;

typedef struct Item_Stack_t {
    Serialization_Header        _serialization_header;
    Item                        item;
    Quantity__u8                quantity_of__items;
    Quantity__u8                max_quantity_of__items;
} Item_Stack;

typedef void (*f_Item_Stack__Create)(Item_Stack *p_item_stack);
// TODO: serialization methods;

typedef struct Item_Stack_Allocation_Specifier_t {
    enum Item_Kind the_kind_of_item__this_specifier_is_for  :15;
    bool is_item_stack_allocation_specifier__allocated      :1;
    f_Item_Stack__Create f_item_stack__create;
} Item_Stack_Allocation_Specifier;

#define ITEM_STACK_RECORD_MAX_QUANTITY_OF 256

typedef struct Item_Stack_Manager_t {
    Item_Stack_Allocation_Specifier item_stack_allocation_specifiers
        [ITEM_STACK_RECORD_MAX_QUANTITY_OF];
    Quantity__u32 quantity_of__item_stack_allocation_specifier;
} Item_Stack_Manager;


#define INVENTORY_ITEM_MAXIMUM_QUANTITY_OF 27
#define INVENTORY_CONSUMABLES_QUANTITY_OF 3

///   __ item_stack index
///  |           __ container: 0, entity: 1 
///  |          |                           
/// [31 .. 26] [25] [24 .. 22] [21 .. 11] [10 ..  0]
///                 z - axis   x - axis   y - axis
///
#define UUID_BIT_SHIFT__INVENTORY__ITEM_STACK 26
#define UUID_BIT_SHIFT__INVENTORY__CONTAINER__Z_AXIS 22
#define UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS 11
#define UUID_MASK__INVENTORY__ITEM_STACK (MASK(6) << \
        UUID_BIT_SHIFT__INVENTORY__ITEM_STACK)
#define UUID_BIT__INVENTORY_IS__ENTITY_OR__CONTAINER BIT(25)
#define UUID_MASK__INVENTORY__CONTAINER__Z_AXIS (MASK(3) << \
        UUID_BIT_SHIFT__INVENTORY__CONTAINER__Z_AXIS)
#define UUID_MASK__INVENTORY__CONTAINER__X_AXIS (MASK(11) << \
        UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS)
#define UUID_MASK__INVENTORY__CONTAINER__Y_AXIS MASK(11)
#define UUID_MASK__INVENTORY__ENTITY MASK(25)

#define REGION__WIDTH__BIT_SHIFT UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS
#define REGION__HEIGHT__BIT_SHIFT UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS

#define REGION__WIDTH BIT(UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS)
#define REGION__HEIGHT BIT(UUID_BIT_SHIFT__INVENTORY__CONTAINER__X_AXIS)

typedef struct Vector__3i32_t Region_Vector__3i32;

typedef struct Inventory_t {
    ///
    /// Do not interact with this.
    ///
    Serialization_Header    _serialization_header;
    Item_Stack items[INVENTORY_ITEM_MAXIMUM_QUANTITY_OF];
    Quantity__u8 quantity_of__item_stacks;
} Inventory;

#define INVENTORY_MAX_QUANTITY_OF__ENTITY 32
#define INVENTORY_MAX_QUANTITY_OF__CONTAINER 32

typedef struct Inventory_Manager_t {
    Inventory inventories_for__containers[INVENTORY_MAX_QUANTITY_OF__CONTAINER];
    Inventory inventories_for__entities[INVENTORY_MAX_QUANTITY_OF__ENTITY];
    Repeatable_Psuedo_Random randomizer_of__inventory_manager;
    Quantity__u8 quantity_of__active_inventories_for__containers;
    Quantity__u8 quantity_of__active_inventories_for__entities;
} Inventory_Manager;

///
/// SECTION_entity
///

typedef struct Entity_t Entity;

typedef void (*m_Entity_Dispose_Handler)(
        Entity *p_entity_self, 
        Game *p_game);
///
/// method callback for entity AI.
/// Use this for pathfinding, attacking, and the like.
///
typedef void (*m_Entity_AI_Handler)(
        Entity *p_entity_self, 
        Game *p_game);
///
/// method callback for entity body.
/// Use this for homeostasis, and "specie-like" abilities.
///
typedef void (*m_Entity_Body_Handler)(
        Entity *p_entity_self,
        Game *p_game);

typedef void (*m_Entity_Game_Action_Handler)(
        Entity *p_entity_self,
        Game_Action *p_game_action,
        Game *p_game);

///
/// callee_data is an opaque pointer to whatever
/// data the user of this function pointer needs
/// passed in addition to collided entities.
///
typedef void (*m_Entity_Collision_Handler)(
        Entity *p_entity_collision_source,
        Entity *p_entity_collided,
        Direction__u8 direction_of_collision,
        Game *p_game);

typedef struct Tile_t Tile;

typedef void (*m_Entity_Tile_Collision_Handler)(
        Entity *p_entity_self,
        Tile *p_tile_collided,
        Signed_Index__i32 x_collision__i32,
        Signed_Index__i32 y_collision__i32,
        Direction__u8 direction_of__tile_collision);

typedef void (*m_Entity_Animation_Handler) 
    (Entity *p_entity_self);

///
/// Here we define the entity super struct. It has everything we could need
/// for an entity, even if some of the things are not used.
///

typedef uint8_t Entity_Flags__u8;

#define ENTITY_FLAG__NONE 0
#define ENTITY_FLAG__IS_ENABLED     BIT(0)
#define ENTITY_FLAG__IS_NOT_UPDATING_POSITION \
    NEXT_BIT(ENTITY_FLAG__IS_ENABLED)
#define ENTITY_FLAG__IS_NOT_UPDATING_GRAPHICS \
    NEXT_BIT(ENTITY_FLAG__IS_NOT_UPDATING_POSITION)
#define ENTITY_FLAG__IS_COLLIDING \
    NEXT_BIT(ENTITY_FLAG__IS_NOT_UPDATING_GRAPHICS)
#define ENTITY_FLAG__IS_UNLOADED \
    NEXT_BIT(ENTITY_FLAG__IS_COLLIDING)
#define ENTITY_FLAG__IS_HIDDEN \
    NEXT_BIT(ENTITY_FLAG__IS_UNLOADED)

typedef uint8_t Humanoid_Flags;
#define HUMANOID_FLAG__IS_UNDEAD                BIT(0)
#define HUMANOID_FLAG__HAS_DIVINE_PROVIDENCE    BIT(1)

#define ENTITY_RESOURCE_SYMBOL_MAX_QUANTITY_OF 32

typedef uint8_t Resource_Symbol__u8;
typedef uint8_t Heart__u8;
typedef uint8_t Energy_Orb__u8;

typedef struct Resource_Reserve_t {
    Resource_Symbol__u8 resource_symbols
        [ENTITY_RESOURCE_SYMBOL_MAX_QUANTITY_OF];
    ///
    /// Used for entities who has more than
    /// ENTITY_RESOURCE_SYMBOL_MAX_QUANTITY_OF
    /// of a resource.
    ///
    /// This overflow cannot be modified. ie it
    /// cannot be poisoned, etc.
    ///
    /// This is primarily used for Ancients only.
    ///
    Quantity__u16 resource_overflow;
    Quantity__u16 max_quantity_of__resource_overflow;
    Quantity__u8 max_quantity_of__resource_symbols;
} Resource_Reserve;

typedef uint8_t Hearts_Damaging_Flags;
#define HEARTS_DAMAGING_FLAGS__NONE 0
#define HEARTS_DAMAGING_FLAG__IS_POISONING \
    BIT(0)
#define HEARTS_DAMAGING_FLAG__IS_ORDER \
    BIT(1)
#define HEARTS_DAMAGING_FLAG__IS_CHAOS \
    BIT(2)
#define HEARTS_DAMAGING_FLAG__IS_CURSING \
    BIT(3)
#define HEARTS_DAMAGING_FLAG__IS_BLUDGEONING \
    BIT(4)
#define HEARTS_DAMAGING_FLAG__IS_SLASHING \
    BIT(5)
#define HEARTS_DAMAGING_FLAG__IS_PIERCING \
    BIT(6)
typedef struct Hearts_Damaging_Specifier_t {
    Quantity__u16 quantity_of__damage;
    Hearts_Damaging_Flags hearts_damaging__flags;
} Hearts_Damaging_Specifier;

#define HEARTS_HEALING_FLAG__IS_ANTIDOTE \
    BIT(0)
#define HEARTS_HEALING_FLAG__IS_IMMORTALIZING \
    BIT(1)
typedef uint8_t Hearts_Healing_Flags;
typedef struct Hearts_Healing_Specifier_t {
    Quantity__u16 quantity_of__healing;
    Hearts_Healing_Flags hearts_healing__flags;
} Hearts_Healing_Specifier;

#define ENERGY_DAMAGING_FLAG__IS_POISONING \
    BIT(0)
#define ENERGY_DAMAGING_FLAG__IS_ORDER \
    BIT(1)
#define ENERGY_DAMAGING_FLAG__IS_CHAOS \
    BIT(2)
typedef uint8_t Energy_Damaging_Flags;
typedef struct Energy_Damaging_Specifier_t {
    Quantity__u16 quantity_of__damage;
    Energy_Damaging_Flags energy_damaging__flags;
} Energy_Damaging_Specifier;

#define ENERGY_HEALING_FLAG__IS_ANTIDOTE \
    BIT(0)
#define ENERGY_HEALING_FLAG__IS_DEMONIZING \
    BIT(1)
typedef uint8_t Energy_Healing_Flags;
typedef struct Energy_Healing_Specifier_t {
    Quantity__u16 quantity_of__healing;
    Energy_Damaging_Flags energy_healing__flags;
} Energy_Healing_Specifier;

typedef int8_t Homeostasis__i8;
#define HOMEOSTASIS_MAX_QUANTITY_OF MASK(7)
#define HOMEOSTASIS_MIN_QUANTITY_OF (int8_t)BIT(7)

#define HOMEOSTASIS__EXTREME_BURNING 110
#define HOMEOSTASIS__BURNING 80
#define HOMEOSTASIS__HOT 40
#define HOMEOSTASIS__NEUTRAL 0
#define HOMEOSTASIS__COLD -40
#define HOMEOSTASIS__FREEZING -80
#define HOMEOSTASIS__EXTREME_FREEZING -110

#define HOMEOSTASIS__SOULFUL -100
#define HOMEOSTASIS__FLEETING_SOUL -50
#define HOMEOSTASIS__SOULLESS 0
#define HOMEOSTASIS__LICHLING 120
#define HOMEOSTASIS__LICH 128

typedef uint8_t Sustenance__u8;
#define SUSTENANCE_MAX_QUANTITY_OF (uint8_t)MASK(8)
#define SUSTENANCE_MIN_QUANTITY_OF 0

#define SUSTENANCE__BLOATED 240
#define SUSTENANCE__FULL 234
#define SUSTENANCE__SATISFIED 206
#define SUSTENANCE__WELL 178
#define SUSTENANCE__INDIFFERENT 150
#define SUSTENANCE__WANTING 122
#define SUSTENANCE__NEEDING 84
#define SUSTENANCE__DESPERATE 56
#define SUSTENANCE__DYING 28

typedef struct Entity_t {
    ///
    /// Do not interact with this.
    ///
    Serialization_Header            _serialization_header;

    m_Entity_Dispose_Handler m_entity_dispose_handler;
} Entity;

#define ENTITY_TILE_LOCAL_SPACE__BIT_SIZE 3
#define CHUNK_LOCAL_SPACE__BIT_SIZE 3

#define ENTITY_CHUNK_LOCAL_SPACE__BIT_SIZE \
    (ENTITY_TILE_LOCAL_SPACE__BIT_SIZE\
     + CHUNK_LOCAL_SPACE__BIT_SIZE)

#define ENTITY_TILE_FRACTIONAL__BIT_SIZE \
    (FRACTIONAL_PERCISION_4__BIT_SIZE \
     + ENTITY_TILE_LOCAL_SPACE__BIT_SIZE)

#define ENTITY_CHUNK_LOCAL_SPACE_FRACTIONAL__BIT_SIZE \
    (FRACTIONAL_PERCISION_4__BIT_SIZE \
     + ENTITY_CHUNK_LOCAL_SPACE__BIT_SIZE)

#define ENTITY_CHUNK_LOCAL_SPACE__BIT_MASK \
    MASK(ENTITY_CHUNK_LOCAL_SPACE__BIT_SIZE)

// 1.5 pixels.
#define ENTITY_VELOCITY__PLAYER          0b1100
#define ENTITY_VELOCITY__PLAYER_DIAGONAL 0b1001

typedef struct Entity_Manager_t {
    Entity entities[ENTITY_MAXIMUM_QUANTITY_OF];
    Repeatable_Psuedo_Random randomizer;
    Entity *p_local_player;
    Quantity__u32 entity_count__quantity_u32;
} Entity_Manager;

///
/// SECTION_input
///

typedef uint32_t Input_Code__u32;
typedef uint32_t Input_Flags__u32;

typedef struct Input_t {
    Input_Flags__u32 input_flags__pressed;
    Input_Flags__u32 input_flags__held;
    Input_Flags__u32 input_flags__released;

    /// 
    /// Not used by all platforms.
    ///
    Input_Flags__u32 input_flags__pressed_old;

    Vector__3i32 cursor__3i32;
    Vector__3i32 cursor__old__3i32;
} Input;

///
/// SECTION_multiplayer
///

typedef struct IPv4_Address_t {
    u8 ip_bytes[4];
    u16 port;
} IPv4_Address;

typedef struct TCP_Packet_t {
    u8 tcp_packet_bytes[MAX_SIZE_OF__TCP_PACKET];
} TCP_Packet;

typedef uint8_t TCP_Socket_Flags__u8;

#define TCP_SOCKET_FLAGS__NONE 0
///
/// When true, the socket will be skipped on poll_multiplayer(...)
/// It must be manually driven by some other means until the flag
/// is unset.
///
#define TCP_SOCKET_FLAG__IS_MANUALLY_DRIVEN BIT(0)

typedef struct TCP_Socket_t {
    Serialization_Header _serialization_header;
    TCP_Packet queue_of__tcp_packet[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET];
    Quantity__u16 packet_size__entries[MAX_QUANTITY_OF__TCP_PACKETS_PER__SOCKET];
    IPv4_Address tcp_socket__address;
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket;
    Index__u32 index_of__enqueue_begin;
    Quantity__u32 quantity_of__received_packets;
    TCP_Socket_State tcp_socket__state_of;
    TCP_Socket_Flags__u8 tcp_socket_flags__u8;
} TCP_Socket;

typedef void (*m_Poll_TCP_Socket_Manager)(
        TCP_Socket_Manager *p_tcp_socket_manager,
        Game *p_game);

typedef struct TCP_Socket_Manager_t {
    TCP_Socket tcp_sockets[MAX_QUANTITY_OF__TCP_SOCKETS];
    TCP_Socket *ptr_array_of__tcp_sockets[
        MAX_QUANTITY_OF__TCP_SOCKETS];
    PLATFORM_TCP_Context *p_PLATFORM_tcp_context;
    m_Poll_TCP_Socket_Manager m_poll_tcp_socket_manager;
    PLATFORM_TCP_Socket *p_PLATFORM_tcp_socket__pending_connection;
    IPv4_Address ipv4__pending_connection;
    Quantity__u32 quantity_of__connections;
} TCP_Socket_Manager;

///
/// SECTION_process
///

typedef struct Process_t Process;

typedef void (*m_Process)(
        Process *p_this_process,
        Game *p_game);

typedef uint8_t Process_Flags__u8;

#define PROCESS_FLAG__IS_CRITICAL BIT(0)
#define PROCESS_FLAG__IS_SUB_PROCESS BIT(1)
#define PROCESS_FLAGS__NONE 0

///
/// Multithreading abstraction.
///
typedef struct Process_t {
    Serialization_Header _serialization_header;
    m_Process m_process_run__handler;
    union {
        Process *p_queued_process;
        Process *p_sub_process;
    };
    void *p_process_data;
    i32F20 process_runtime__i32F20;
    Process_Status_Kind the_kind_of_status__this_process_has;
    Process_Kind the_kind_of__process_this__process_is;
    u8 process_sub_state__u8;
    Process_Flags__u8 process_flags__u8;
} Process;

#define PROCESS_MAX_QUANTITY_OF 512

typedef struct Process_Manager_t {
    Process processes[PROCESS_MAX_QUANTITY_OF];
    Process *ptr_array_of__processes[PROCESS_MAX_QUANTITY_OF];
    Process **p_ptr_to__last_process_in__ptr_array_of__processes;
    Repeatable_Psuedo_Random repeatable_psuedo_random_for__process_uuid;
    Identifier__u32 next__uuid__u32;
} Process_Manager;

///
/// SECTION_scene
///

typedef struct Scene_t Scene;

typedef struct Scene_Data__Game_t {
    Timer__u8 timer_for__hud_notification__u8;
    Timer__u8 timer_for__typer_sliding__u8;
} Scene_Data__Game;

///
/// Prepares p_game for scene entry.
///
typedef void (*m_Load_Scene)  (Scene *p_this_scene, Game* p_game);
///
/// Functions as main loop.
///
typedef void (*m_Enter_Scene) (Scene *p_this_scene, Game* p_game);
///
/// Cleans up p_game following scene exit
///
typedef void (*m_Unload_Scene)(Scene *p_this_scene, Game* p_game);

typedef struct Scene_t {
    Scene *p_parent_scene;
    m_Load_Scene m_load_scene_handler;
    m_Enter_Scene m_enter_scene_handler;
    m_Unload_Scene m_unload_scene_handler;
    void *p_scene_data;
    Identifier__u16 scene__identifier_u16;
    bool is_active;
} Scene;

//TODO: move to platform.h in ifndef
#define SCENE_MAX_QUANTITY_OF 8

typedef struct Scene_Manager_t {
    Scene scenes[SCENE_MAX_QUANTITY_OF];
    Scene *p_active_scene;
} Scene_Manager;

///
/// SECTION_sort
///

#define INDEX__UNKNOWN__SORT_NODE (INDEX__UNKNOWN__u16 >> 1)

typedef struct Sort_Node_t {
    void                    *p_node_data;
    Signed_Quantity__i16    heuristic_value;
    Index__u16              index_for__next_node    :15;
    bool                    is_allocated            :1;
} Sort_Node;

///
/// Heuristic for sorting.
///
typedef Signed_Quantity__i32 (*f_Sort_Heuristic)(
        Sort_Node *p_node__one,
        Sort_Node *p_node__two);

typedef struct Sort_List_t Sort_List;

///
/// Should be implemented to run just one
/// step of the sort algorithm per invocation.
///
/// Return true if fully sorted, otherwise false.
///
typedef bool (*m_Sort)(
        Sort_List *p_this_sort_list);

///
/// Auxiliary structures for Sort_List should
/// be defined here, and then accesed via
/// p_sort_list->sort_data
///
/// Note: Even if your algorithm has O(1)
/// space complexity, you should still
/// make sure of Sort_Data to leverage
/// the task-scheduling system.
///
typedef union Sort_Data_t {
    struct { // Heapsort
        ///
        /// if equals INDEX__UNKNOWN__SORT_NODE
        /// then heapify is complete.
        ///
        Index__u16 index_of__heapification;
        Index__u16 index_of__heap_sort;
    };
} Sort_Data;

///
/// NOTE: p_node_list is ASSUMED to be allocated
/// CONTIGUOUSLY!!!
///
typedef struct Sort_List_t {
    Sort_Node *p_node_list;
    f_Sort_Heuristic f_sort_heuristic;
    m_Sort m_sort;
    struct Sort_List_t *p_sort_list__next;
    Quantity__u32 size_of__p_node_list  :31;
    bool is_allocated                   :1;

    Sort_Data sort_data;
} Sort_List;

#define SORT_LIST__MAXIMUM_QUANTITY_OF 64
#define SORT_NODE__MAXIMUM_QUANTITY_OF 512

typedef struct Sort_List_Manager_t {
    Quantity__u32 quantity_of__allocated_sort_lists;
    Quantity__u32 quantity_of__allocated_sort_nodes;
    Sort_List sort_lists 
        [SORT_LIST__MAXIMUM_QUANTITY_OF];
    Sort_Node sort_nodes
        [SORT_NODE__MAXIMUM_QUANTITY_OF];
} Sort_List_Manager;

///
/// SECTION_ui
///

typedef struct UI_Element_t UI_Element;
typedef struct UI_Manager_t UI_Manager;

typedef u16 UI_Tile_Flags;

#define UI_TILE_FLAGS__NONE 0

#define UI_TILE_FLAG__SCALE_VERTICAL        BIT(0)
#define UI_TILE_FLAG__SCALE_HORIZONTAL      BIT(1)
#define UI_TILE_FLAG__FLIPPED_VERTICAL      BIT(2)
#define UI_TILE_FLAG__FLIPPED_HORIZONTAL    BIT(3)
#define UI_TILE_FLAG__GENERAL_1             BIT(4)
#define UI_TILE_FLAG__GENERAL_2             BIT(5)

#define UI_TILE__QUANTITY_OF__FLAGS 6

///
/// Endian-proof form of UI_Tile.
///
typedef u16 UI_Tile_Raw;

typedef struct UI_Tile_t {
    UI_Tile_Kind the_kind_of__ui_tile   :10;
    UI_Tile_Flags ui_tile_flags         :UI_TILE__QUANTITY_OF__FLAGS;
} UI_Tile;

#define UI_TILE_SPAN__QUANTITY_OF__CORNERS 4
#define UI_TILE_SPAN__QUANTITY_OF__EDGES 4
typedef struct UI_Tile_Span_t {
    union {
        UI_Tile ui_tile__corners[
            UI_TILE_SPAN__QUANTITY_OF__CORNERS];
        struct {
            UI_Tile ui_tile__corner__top_left;
            UI_Tile ui_tile__corner__top_right;
            UI_Tile ui_tile__corner__bottom_left;
            UI_Tile ui_tile__corner__bottom_right;
        };
    };
    union {
        UI_Tile ui_tile__edges[
            UI_TILE_SPAN__QUANTITY_OF__EDGES];
        struct {
            UI_Tile ui_tile__edge__top;
            UI_Tile ui_tile__edge__right;
            UI_Tile ui_tile__edge__bottom;
            UI_Tile ui_tile__edge__left;
        };
    };
    UI_Tile ui_tile__fill;
} UI_Tile_Span;

// TODO: remove
typedef uint8_t UI_Tile_Map__Flags;

#define UI_TILE_MAP__FLAGS__NONE 0
#define UI_TILE_MAP__FLAG__IS_ALLOCATED BIT(0)

typedef struct UI_Tile_Map__Wrapper_t {
    UI_Tile_Raw *p_ui_tile_data;
    Quantity__u32 width_of__ui_tile_map;
    Quantity__u32 height_of__ui_tile_map;
    UI_Tile_Map_Size catagory_size_of__ui_tile_map;
} UI_Tile_Map__Wrapper;

typedef struct UI_Tile_Map__Small_t {
    UI_Tile_Map__Flags ui_tile_map__flags;
    UI_Tile_Raw ui_tile_data__small[
        UI_TILE_MAP__SMALL__WIDTH
            * UI_TILE_MAP__SMALL__HEIGHT];
} UI_Tile_Map__Small;

typedef struct UI_Tile_Map__Medium_t {
    UI_Tile_Map__Flags ui_tile_map__flags;
    UI_Tile_Raw ui_tile_data__medium[
        UI_TILE_MAP__MEDIUM__WIDTH
            * UI_TILE_MAP__MEDIUM__HEIGHT];
} UI_Tile_Map__Medium;

typedef struct UI_Tile_Map__Large_t {
    UI_Tile_Map__Flags ui_tile_map__flags;
    UI_Tile_Raw ui_tile_data__large[
        UI_TILE_MAP__LARGE__WIDTH
            * UI_TILE_MAP__LARGE__HEIGHT];
} UI_Tile_Map__Large;

///
/// NOTE:   This is not included in the core game
///         structs, since not all platforms (nds)
///         leverages it. It is up to the platform
///         to explicitly include a UI_Tile_Map_Manager
///         somewhere within its PLATFORM_Gfx_Context.
///
typedef struct UI_Tile_Map_Manager_t {
    UI_Tile_Map__Large ui_tile_maps__large[
        UI_TILE_MAP__LARGE__MAX_QUANTITY_OF];
    UI_Tile_Map__Medium ui_tile_maps__medium[
        UI_TILE_MAP__MEDIUM__MAX_QUANTITY_OF];
    UI_Tile_Map__Small ui_tile_maps__small[
        UI_TILE_MAP__SMALL__MAX_QUANTITY_OF];
} UI_Tile_Map_Manager;

typedef void (*m_UI_Dispose)(
        UI_Element *p_this_ui_element,
        Game *p_game);

typedef void (*m_UI_Clicked)(
        UI_Element *p_this_ui_element,
        Game *p_game,
        PLATFORM_Graphics_Window *p_PLATFORM_gfx_window);
typedef void (*m_UI_Dragged)(
        UI_Element *p_this_ui_element,
        Game *p_game);
typedef void (*m_UI_Receive_Drop)(
        UI_Manager *p_ui_manager,
        UI_Element *p_this_ui_element,
        UI_Element *p_ui_element__dropped,
        Game *p_game);
typedef void (*m_UI_Dropped)(
        UI_Element *p_this_ui_element,
        Game *p_game);
typedef void (*m_UI_Held)(
        UI_Element *p_this_ui_element,
        Game *p_game);
typedef void (*m_UI_Render)(
        UI_Element *p_this_ui_element,
        Game *p_game,
        Graphics_Window *p_gfx_window);

typedef uint16_t UI_Flags__u16;
typedef uint8_t UI_Button_Flags__u8;

#define UI_HUD_NOTIFICATION_LIFESPAN_IN__SECONDS 4
#define UI_HUD_MESSAGE_LIFESPAN_IN__SECONDS 20

#define UI_FLAGS__BIT_SHIFT_IS_ALLOCATED 0
#define UI_FLAGS__BIT_SHIFT_IS_ENABLED \
    (UI_FLAGS__BIT_SHIFT_IS_ALLOCATED + 1)
#define UI_FLAGS__BIT_SHIFT_IS_NON_INTERACTIVE \
    (UI_FLAGS__BIT_SHIFT_IS_ENABLED + 1)
#define UI_FLAGS__BIT_SHIFT_IS_NEEDING_UPDATE \
    (UI_FLAGS__BIT_SHIFT_IS_NON_INTERACTIVE + 1)
#define UI_FLAGS__BIT_SHIFT_IS_BEING_HELD \
    (UI_FLAGS__BIT_SHIFT_IS_NEEDING_UPDATE + 1)
#define UI_FLAGS__BIT_SHIFT_IS_BEING_DRAGGED \
    (UI_FLAGS__BIT_SHIFT_IS_BEING_HELD + 1)
#define UI_FLAGS__BIT_SHIFT_IS_SNAPPED_X_OR_Y_AXIS \
    (UI_FLAGS__BIT_SHIFT_IS_BEING_DRAGGED + 1)
#define UI_FLAGS__BIT_SHIFT_IS_USING__SPRITE_OR_UI_TILE_SPAN \
    (UI_FLAGS__BIT_SHIFT_IS_SNAPPED_X_OR_Y_AXIS + 1)

#define UI_FLAGS__NONE 0

#define UI_FLAGS__BIT_IS_ALLOCATED \
    BIT(UI_FLAGS__BIT_SHIFT_IS_ALLOCATED)
#define UI_FLAGS__BIT_IS_ENABLED \
    BIT(UI_FLAGS__BIT_SHIFT_IS_ENABLED)
#define UI_FLAGS__BIT_IS_NON_INTERACTIVE \
    BIT(UI_FLAGS__BIT_SHIFT_IS_NON_INTERACTIVE)
#define UI_FLAGS__BIT_IS_NEEDING_UPDATE \
    BIT(UI_FLAGS__BIT_SHIFT_IS_NEEDING_UPDATE)
#define UI_FLAGS__BIT_IS_BEING_HELD \
    BIT(UI_FLAGS__BIT_SHIFT_IS_BEING_HELD)
#define UI_FLAGS__BIT_IS_BEING_DRAGGED \
    BIT(UI_FLAGS__BIT_SHIFT_IS_BEING_DRAGGED )
#define UI_FLAGS__BIT_IS_SNAPPED_X_OR_Y_AXIS \
    BIT(UI_FLAGS__BIT_SHIFT_IS_SNAPPED_X_OR_Y_AXIS)
#define UI_FLAGS__BIT_IS_USING__SPRITE_OR_UI_TILE_SPAN \
    BIT(UI_FLAGS__BIT_SHIFT_IS_USING__SPRITE_OR_UI_TILE_SPAN)

#define UI_BUTTON_FLAGS__NONE 0
#define UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLEABLE 0
#define UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLED \
    (UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLEABLE + 1)

#define UI_BUTTON_FLAGS__BIT_IS_TOGGLEABLE \
    BIT(UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLEABLE)
#define UI_BUTTON_FLAGS__BIT_IS_TOGGLED \
    BIT(UI_BUTTON_FLAGS__BIT_SHIFT_IS_TOGGLED)

typedef struct UI_Element_t {
    enum UI_Element_Kind    the_kind_of_ui_element__this_is;
    Hitbox_AABB             ui_bounding_box__aabb;
    /// DO NOT INVOKE
    m_UI_Clicked            m_ui_clicked_handler;
    /// DO NOT INVOKE
    m_UI_Dragged            m_ui_dragged_handler;
    /// DO NOT INVOKE
    m_UI_Dropped            m_ui_dropped_handler;
    /// DO NOT INVOKE
    m_UI_Receive_Drop       m_ui_receive_drop_handler;
    /// DO NOT INVOKE
    m_UI_Held               m_ui_held_handler;
    /// DO NOT INVOKE
    m_UI_Render             m_ui_render_handler;
    /// DO NOT INVOKE, DO NOT REMOVE FROM UI_MANAGER
    /// FROM WITHIN m_ui_dispose_handler!
    /// When implementing your own, be sure to
    /// also invoke m_ui_element__dispose_handler__default(...)
    m_UI_Dispose            m_ui_dispose_handler;
    void                    *p_ui_data;
    Serialized_Field        s_serialized_field;
    UI_Element *p_parent,   *p_child, *p_next;
    Identifier__u16         ui_identifier;
    UI_Flags__u16            ui_flags;
    union {
        Sprite_Wrapper          ui_sprite_wrapper;
        UI_Tile_Span            ui_tile_span;
    };
    union {
        struct { // UI_Button
            UI_Button_Flags__u8 ui_button_flags;
        };
        struct { // UI_Draggable
        };
        struct { // UI_Slider
            Vector__3i32    slider__spanning_length__3i32;
            u32             slider__distance__u32;
        };
    };
} UI_Element;

#define UI_ELEMENT_MAXIMUM_QUANTITY_OF 128
#define UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF 8

typedef UI_Element UI_Container_Entries[
    UI_CONTAINER_PTR_ENTRIES_MAXIMUM_QUANTITY_OF];

typedef void (*f_Foreach_UI_Element)(
        UI_Manager *p_ui_manager,
        Game *p_game,
        Graphics_Window *p_gfx_window,
        UI_Element *p_ui_element);

///
/// UI_Manager is not apart of core data structures,
/// and is instead apart of PLATFORM_Graphics_Window
/// which is left to the backend to implement.
///
/// Why? This is because by keeping a singleton UI_Manager
/// in Game_t and designing everything around that, it
/// then makes it difficult to seperate UI_Elements
/// in different Gfx_Windows. Some PLATFORMs can support
/// more than one window, some PLATFORMs don't even correlate
/// UI_Elements to a Gfx_Window... it varies.
///
/// So it's best to delegate the reponsibility to PLATFORM.
/// CORE logic should leverate PLATFORM_get_ui_manager_from__gfx_window(...)
/// And if a PLATFORM doesn't keep UI_Managers in Gfx_Windows
/// then it should constantly return the singleton.
///
typedef struct UI_Manager_t {
    Quantity__u8 quantity_of__ui_elements__quantity_u8;
    UI_Element ui_elements[UI_ELEMENT_MAXIMUM_QUANTITY_OF];
    UI_Element *ui_element_ptrs[UI_ELEMENT_MAXIMUM_QUANTITY_OF];
    UI_Element *p_ui_element__focused;

    PLATFORM_Graphics_Window 
        *p_PLATFORM_graphics_window_for__ui_manager;
} UI_Manager;

typedef struct UI_Context_t UI_Context;

typedef bool (*f_UI_Window__Load)(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager);

typedef bool (*f_UI_Window__Close)(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager);

#define MAX_QUANTITY_OF__UI_MANAGERS 8

typedef struct UI_Context_t {
    UI_Manager *pM_ui_managers[
        MAX_QUANTITY_OF__UI_MANAGERS];
    f_UI_Window__Load F_ui_window__loaders[
        Graphics_Window_Kind__Unknown];
    f_UI_Window__Close F_ui_window__closers[
        Graphics_Window_Kind__Unknown];
} UI_Context;

///
/// SECTION_world
///

typedef void (*m_Camera_Handler)(
        Camera *p_this_camera,
        World *p_world);

typedef struct Camera_t {
    Vector__3i32F4 position;
    m_Camera_Handler m_camera_handler;
    void *p_camera_data;
    Quantity__u32 width_of__fulcrum;
    Quantity__u32 height_of__fulcrum;
    i32F20 z_near;
    i32F20 z_far;
} Camera;

#define PATH_VECTORS_MAX_QUANTITY_OF 6

///
/// For pathfinding algorithm state machine.
/// Core does not ship with an A* pathfinding
/// algorithm yet due to memory constraints.
///
enum Path_Progression_State {
    Path_Progression_State__Obstructed,
    Path_Progression_State__Unobstructed,
    Path_Progression_State__Deviating,
    Path_Progression_State__Progressing,
    Path_Progression_State__Routed,
    Path_Progression_State__List_Exhausted
};

enum Path_Stepping_Result {
    Path_Stepping_Result__Obstructed,
    Path_Stepping_Result__Unobstructed
};

typedef struct Path_t {
    Ray__3i32F20    leading_ray_of__path;
    Vector__3i32    path_nodes__3i32
        [PATH_VECTORS_MAX_QUANTITY_OF];
    Degree__u9      obstruction_indicent_stack[
        PATH_VECTORS_MAX_QUANTITY_OF];
    i32F20          distance__travelled__i32F20;
    i32F4           distance_squared__from_target__i32F4;
    i32             distance__hamming__i32;
    Index__u8       index_of__path_node;
    Index__u8       index_of__incident;
    enum Path_Progression_State
                    state_of__path_progression      :7;
    bool            is_rotating__left_or__right     :1;
} Path;

#define PATH_MAX_QUANTITY_OF 8

typedef struct Path_List_t {
    Path            paths[PATH_MAX_QUANTITY_OF];
    Sort_List       *p_min_heap_for__paths;
    Sort_List       *p_max_heap_for__paths;
    Vector__3i32    destination__3i32;
    i32F4           destination_squared_radius__i32F4;
} Path_List;

#define PATH_LIST_MAX_QUANTITY_OF 64

typedef struct Path_List_Manager {
    Path_List       path_lists[PATH_LIST_MAX_QUANTITY_OF];
    Quantity__u32   quantity_of__path_lists;
} Path_List_Manager;

#define ROOM_ENTRANCE_MAX_QUANTITY_OF 4

typedef Quantity__u16 Room_Type__u16;
typedef uint8_t Room_Flags__u8;

#define ROOM_FLAGS__NONE 0
#define ROOM_FLAG__IS_ALLOCATED BIT(0)

typedef struct Room_t {
    Serialization_Header _serialization_header;
    Hitbox_AABB bounding_box_of__room;
    Vector__3i32F4 entrances__3i32F4
        [ROOM_ENTRANCE_MAX_QUANTITY_OF];
    Room_Type__u16 the_type_of__room;
    Quantity__u8 quantity_of__room_entrances;
    Room_Flags__u8 room_flags;
} Room;

#define ROOM_MAX_QUANTITY_OF 128
#define ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF 8

typedef Quantity__u16 Structure_Type__u16;
typedef uint8_t Structure_Flags__u8;

#define STRUCTURE_FLAGS__NONE 0
#define STRUCTURE_FLAG__IS_ALLOCATED BIT(0)

typedef Room* Structure_Ptr_Array_Of__Rooms[
    ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF];

typedef struct Structure_t {
    Serialization_Header _serialization_header;
    Structure_Ptr_Array_Of__Rooms ptr_array_of__rooms;
    Hitbox_AABB bounding_box_of__structure;
    Structure_Type__u16 the_kind_of__structure;
    Quantity__u8 quantity_of__rooms_in__structure;
    Structure_Flags__u8 structure_flags;
} Structure;

#define STRUCTURE_MAX_QUANTITY_OF (\
        ROOM_MAX_QUANTITY_OF \
        / ROOMS_IN_STRUCTURE__MAX_QUANTITY_OF)

#define STRUCTURES_IN_SITE__MAX_QUANTITY_OF\
    (STRUCTURE_MAX_QUANTITY_OF \
    / 4)
#define SITE_MAX_QUANTITY_OF\
    (STRUCTURE_MAX_QUANTITY_OF \
     / STRUCTURES_IN_SITE__MAX_QUANTITY_OF)

#define SITE__WIDTH_IN__TILES 512
#define SITE__HEIGHT_IN__TILES 512

typedef Structure *Site_Ptr_Array_Of__Structures[
    STRUCTURES_IN_SITE__MAX_QUANTITY_OF];

typedef struct Site_t {
    Serialization_Header _serialization_header;
    Site_Ptr_Array_Of__Structures ptr_array_of__structures_in__site;
    Hitbox_AABB bounding_box_of__site;
    Quantity__u8 quantity_of__structures_in__site;
} Site;

#define REGION__WIDTH_IN__CHUNKS \
    (REGION__WIDTH \
    >> CHUNK__WIDTH_BIT_SHIFT)
#define REGION__HEIGHT_IN__CHUNKS \
    (REGION__HEIGHT \
    >> CHUNK__HEIGHT_BIT_SHIFT)

#define SITE_QUANTITY_OF__PER_REGION \
    ((REGION__WIDTH * REGION__HEIGHT) \
     / (SITE__WIDTH_IN__TILES\
         * SITE__HEIGHT_IN__TILES))

typedef struct Region_t {
    Serialization_Header _serialization_header;
    u8 bitmap_of__serialized_chunks[
        (REGION__WIDTH_IN__CHUNKS
            * REGION__HEIGHT_IN__CHUNKS
            >> 3)];
    u8 bitmap_of__sites[
        SITE_QUANTITY_OF__PER_REGION
            >> 3];
} Region;

#define REGION_MAX_QUANTITY_OF 4

typedef struct Region_Manager_t {
    Region regions[REGION_MAX_QUANTITY_OF];
} Region_Manager;

typedef struct Structure_Manager_t {
    Room rooms[ROOM_MAX_QUANTITY_OF];
    Structure structures[STRUCTURE_MAX_QUANTITY_OF];

    Room *ptr_array_of__allocated_rooms[ROOM_MAX_QUANTITY_OF];
    Structure *ptr_array_of__allocated_structures[
        STRUCTURE_MAX_QUANTITY_OF];

    Quantity__u32 quantity_of__allocated_rooms;
    Quantity__u32 quantity_of__allocated_structures;
} Structure_Manager;

typedef bool (*f_Room_Compositor_Handler__Room)(
        Game *p_game,
        Room *p_room);

typedef bool (*f_Room_Compositor_Handler__Hallway)(
        Game *p_game,
        Room *p_room__origin,
        Room *p_room__destination);

typedef struct Room_Compositor_t {
    f_Room_Compositor_Handler__Room f_room_compositor_handler__room;
    f_Room_Compositor_Handler__Hallway f_room_compositor_handler__hallway;
} Room_Compositor;

typedef uint8_t Chunk_Tile_Index__u8;
///
/// Local to a chunk.
///
typedef Vector__3u8 Local_Tile_Vector__3u8;


#define TILE_PIXEL_HEIGHT 8
#define TILE_PIXEL_WIDTH 8

#define TILE_PIXEL_WIDTH__BIT_SIZE 3

#define TILE_SHEET_PIXEL_WIDTH 256
#define TILE_SHEET_PIXEL_HEIGHT 256

#define TILE_SHEET_TILE_WIDTH (TILE_SHEET_PIXEL_WIDTH / TILE_PIXEL_WIDTH)
#define TILE_SHEET_TILE_HEIGHT (TILE_SHEET_PIXEL_HEIGHT / TILE_PIXEL_HEIGHT)

#define QUANTITY_OF_TILES__IN_TILE_SHEET_ROW (TILE_SHEET_PIXEL_WIDTH / TILE_PIXEL_WIDTH)

#define TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING 0
#define TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE \
    (TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING + 1)
#define TILE_FLAGS__BIT_SHIFT_IS_CONTAINER \
    (TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE + 1)
#define TILE_FLAGS__BIT_SHIFT_GENERAL_PURPOSE_DATA_BIT \
    (TILE_FLAGS__BIT_IS_CONTAINER + 1)

#define TILE_FLAGS__BIT_IS_SIGHT_BLOCKING \
    BIT(TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING)
#define TILE_FLAGS__BIT_IS_UNPASSABLE \
    BIT(TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE)
#define TILE_FLAGS__BIT_IS_CONTAINER \
    BIT(TILE_FLAGS__BIT_SHIFT_IS_CONTAINER)
#define TILE_FLAGS__BIT_GENERAL_PURPOSE_DATA_BIT \
    BIT(TILE_FLAGS__BIT_SHIFT_GENERAL_PURPOSE_DATA_BIT)

#define TILE_FLAGS__NONE 0

#define TILE_SHEET_ELEMENT_WIDTH 32

#define TILE_SHEET_INDEX__WOOD 0
#define TILE_SHEET_INDEX__STONE_BRICK 1
#define TILE_SHEET_INDEX__GOLD 2
#define TILE_SHEET_INDEX__IRON 3
#define TILE_SHEET_INDEX__DIAMOND 4
#define TILE_SHEET_INDEX__AMEYTHYST 5
#define TILE_SHEET_INDEX__SANDSTONE 6
#define TILE_SHEET_INDEX__STONE 7
#define TILE_SHEET_INDEX__DIRT 8
#define TILE_SHEET_INDEX__SAND 9
#define TILE_SHEET_INDEX__GRASS 10
#define TILE_SHEET_INDEX__LEAVES 11
#define TILE_SHEET_INDEX__SNOW 12
#define TILE_SHEET_INDEX__WATER 257

typedef struct Tile_t Tile;

#define TILE_COVER_SHEET_INDEX__WALL (1 + TILE_SHEET_TILE_WIDTH * 16)
#define TILE_COVER_SHEET_INDEX__DOOR (16 + 1 + TILE_SHEET_TILE_WIDTH * 16)

#define TILE_COVER_SHEET_INDEX__PLANT (1 + TILE_SHEET_TILE_WIDTH * 2)
#define TILE_COVER_SHEET_INDEX__FLOWER_RED (1 + TILE_SHEET_TILE_WIDTH * 3)
#define TILE_COVER_SHEET_INDEX__FLOWER_BLUE (1 + TILE_SHEET_TILE_WIDTH * 4)
#define TILE_COVER_SHEET_INDEX__FLOWER_YELLOW (1 + TILE_SHEET_TILE_WIDTH * 5)
#define TILE_COVER_SHEET_INDEX__CACTUS (5 + TILE_SHEET_TILE_WIDTH * 0)
#define TILE_COVER_SHEET_INDEX__CHEST_SINGLE (7 + TILE_SHEET_TILE_WIDTH * 12)

#define TILE_COVER__BIT_SHIFT_IS_WALL 9
#define TILE_COVER__BIT_IS_WALL \
    BIT(TILE_COVER__BIT_SHIFT_IS_WALL)

typedef uint8_t Tile_Flags__u8;

typedef void (*f_Tile_Handler__Touch)(
        Game *p_game,
        Tile *p_tile,
        Tile_Vector__3i32 tile_vector__3i32,
        Entity *p_entity);

///
/// Returns false on placement failure
///
typedef bool (*f_Tile_Handler__Place)(
        Game *p_game,
        Tile *p_tile,
        u32 tile__placement_code__u32,
        Tile_Vector__3i32 tile_vector__3i32);

typedef bool (*f_Tile_Handler__Destroy)(
        Game *p_game,
        Tile *p_tile,
        u32 tile__destruction_code__u32,
        Tile_Vector__3i32 tile_vector__3i32);

typedef uint8_t Tile_Logic_Flags__u8;
#define TILE_LOGIC_FLAGS__NONE 0
#define TILE_LOGIC_FLAG__IS_UNPASSABLE BIT(0)
#define TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING BIT(1)

typedef struct Tile_Logic_Record_t {
    f_Tile_Handler__Touch       f_tile_handler__touch;
    f_Tile_Handler__Place       f_tile_handler__place;
    f_Tile_Handler__Destroy     f_tile_handler__destroy;
    Tile_Logic_Flags__u8        tile_logic_flags__u8;
} Tile_Logic_Record;

///
/// Manages the logic associated with special tiles.
/// IE. lava tile, water tile, chest tile, etc.
///
typedef struct Tile_Logic_Manager_t {
    Tile_Logic_Record tile_logic_records_for__ground_kinds[
        Tile_Kind__Unknown];
} Tile_Logic_Manager;

typedef struct Tile_t {
    enum Tile_Kind                  
        the_kind_of_tile__this_tile_is          :10;
    Tile_Flags__u8 tile_flags                   :6;
} Tile;

typedef uint16_t Tile_Render_Index__u16;
typedef uint16_t Tile_Wall_Adjacency_Code__u16;

typedef struct Tile_Render_Kernel_Result_t {
    Index__u16 index_of__texture;
    bool is_flipped__x    :1;
    bool is_flipped__y    :1;
    u8                    :6;
} Tile_Render_Kernel_Result;

typedef struct Tile_Render_Result_t {
    Tile_Render_Index__u16 tile_index__ground;
    Tile_Render_Index__u16 tile_index__cover;
    Tile_Render_Index__u16 tile_index__sprite_cover;
    Tile_Render_Index__u16 tile_index__sprite_cover__extra;
    Tile_Wall_Adjacency_Code__u16 wall_adjacency;
} Tile_Render_Result;

#define TILE_RENDER__WALL_ADJACENCY__BIT_SHIFT_VFLIP 5
#define TILE_RENDER__WALL_ADJACENCY__BIT_VFLIP \
    BIT(TILE_RENDER__WALL_ADJACENCY__BIT_SHIFT_VFLIP)

#define TILE_RENDER__WALL_ADJACENCY__EAST  0b00010001
#define TILE_RENDER__WALL_ADJACENCY__WEST  0b00110001
#define TILE_RENDER__WALL_ADJACENCY__NORTH 0b00000100
#define TILE_RENDER__WALL_ADJACENCY__SOUTH 0b00001000

#define TILE_RENDER__WALL_ADJACENCY__COVER_MASK \
    MASK(2) 
#define TILE_RENDER__WALL_ADJACENCY__SPRITE_COVER_MASK \
    MASK(4)

typedef struct World_Parameters_t World_Parameters;
typedef struct Chunk_t Chunk;
typedef struct Chunk_Data_t Chunk_Data;

typedef void (*f_Chunk_Generator)(
        Game *p_game,
        Global_Space *p_global_space);

typedef struct World_Parameters_t {
    f_Chunk_Generator f_chunk_generator;
} World_Parameters;

/// Should only be made from calls to inlined helpers
/// from chunk_manager.h
typedef struct Position_Local_To_Chunk_2i8_t {
    Quantity__u8 x__local__quantity_u8;
    Quantity__u8 y__local__quantity_u8;
} Position_Local_To_Chunk_2i8;

///
/// CHUNK_FLAG__IS_ACTIVE - chunk is ready to render and received updates
/// CHUNK_FLAG__IS_AWAITING_SERIALIZATION - chunk is busy being serialized
/// CHUNK_FLAG__IS_AWAITING_DESERIALIZATION - busy being deserialized
/// CHUNK_FLAG__IS_UPDATED - chunk tiles got updated, needs to be saved.
/// CHUNK_FLAG__IS_VISUALLY_UPDATED - chunk tiles got updated, but only for
///                                     visuals. No need to serialize yet.
///

typedef uint8_t Chunk_Flags;

#define CHUNK_FLAGS__NONE 0
#define CHUNK_FLAG__IS_ACTIVE BIT(0)
#define CHUNK_FLAG__IS_AWAITING_SERIALIZATION BIT(1)
#define CHUNK_FLAG__IS_AWAITING_DESERIALIZATION BIT(2)
#define CHUNK_FLAG__IS_UPDATED BIT(3)
#define CHUNK_FLAG__IS_VISUALLY_UPDATED BIT(4)

typedef struct Chunk_Data_t {
    Tile tiles[CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH];
} Chunk_Data;

typedef struct Chunk_t {
    ///
    /// Do not interact with this.
    ///
    Serialization_Header__UUID_64    _serialization_header;
    Chunk_Flags chunk_flags;
    union {
        Tile tiles[CHUNK__WIDTH * CHUNK__HEIGHT * CHUNK__DEPTH];
        Chunk_Data chunk_data;
    };
} Chunk;

typedef struct Chunk_Pool_t {
    Chunk chunks[QUANTITY_OF__GLOBAL_SPACE];
} Chunk_Pool;

typedef struct Chunk_Manager__Chunk_Map_Node_t {
    Chunk *p_chunk__here;
    struct Chunk_Manager__Chunk_Map_Node_t *p_north__chunk_map_node;
    struct Chunk_Manager__Chunk_Map_Node_t *p_east__chunk_map_node;
    struct Chunk_Manager__Chunk_Map_Node_t *p_south__chunk_map_node;
    struct Chunk_Manager__Chunk_Map_Node_t *p_west__chunk_map_node;
    Chunk_Vector__3i32 position_of__chunk_3i32;
} Chunk_Manager__Chunk_Map_Node;

typedef Chunk_Manager__Chunk_Map_Node
    Chunk_Manager__Chunk_Map[CHUNK_MANAGER__QUANTITY_OF_CHUNKS];

typedef struct Chunk_Manager_t {
    Chunk chunks[CHUNK_MANAGER__QUANTITY_OF_CHUNKS];
    Chunk_Manager__Chunk_Map_Node *ptr_array_queue__serialized_nodes[
        CHUNK_MANAGER__QUANTITY_OF_IO_QUEUED_CHUNKS];
    Chunk_Manager__Chunk_Map chunk_map;
    
    Chunk_Manager__Chunk_Map_Node *p_local_player_occupied__chunk_map_node;
    Chunk_Manager__Chunk_Map_Node *p_most_north_western__chunk_map_node;
    Chunk_Manager__Chunk_Map_Node *p_most_south_eastern__chunk_map_node;
    Chunk_Manager__Chunk_Map_Node *p_most_north_eastern__chunk_map_node;
    Chunk_Manager__Chunk_Map_Node *p_most_south_western__chunk_map_node;

    Signed_Index__i32 
        x__center_chunk__signed_index_i32, 
        y__center_chunk__signed_index_i32;
} Chunk_Manager;

typedef u8 Global_Space_Flags__u8;

#define GLOBAL_SPACE_FLAG__IS_CONSTRUCTING BIT(0)
#define GLOBAL_SPACE_FLAG__IS_DECONSTRUCTING BIT(1)
#define GLOBAL_SPACE_FLAG__IS_DIRTY BIT(2)

#define GLOBAL_SPACE_FLAGS__NONE 0

typedef struct Global_Space_t {
    Serialization_Header__UUID_64 _serialization_header;
    Chunk_Vector__3i32 chunk_vector__3i32;
    Chunk *p_chunk;
    Collision_Node *p_collision_node;
    Process *p_managing_process;

    ///
    /// 0: deallocated
    /// 1: awaiting usage or deallocation
    /// 2+: actively being referenced
    ///
    Quantity__u16 quantity_of__references;

    Global_Space_Flags__u8 global_space_flags__u8;
} Global_Space;

typedef struct Local_Space_t {
    Global_Space_Vector__3i32 global_space__vector__3i32;
    Global_Space *p_global_space;

    struct Local_Space_t *p_local_space__north;
    struct Local_Space_t *p_local_space__east;
    struct Local_Space_t *p_local_space__south;
    struct Local_Space_t *p_local_space__west;
} Local_Space;

typedef struct Local_Space_Manager_t {
    Local_Space local_spaces[
        AREA_OF__LOCAL_SPACE_MANAGER];
    Vector__3i32 center_of__local_space_manager__3i32;
    Local_Space *p_local_space__north_west;
    Local_Space *p_local_space__north_east;
    Local_Space *p_local_space__south_west;
    Local_Space *p_local_space__south_east;
} Local_Space_Manager;

typedef struct Global_Space_Manager_t {
    Global_Space global_spaces[
        QUANTITY_OF__GLOBAL_SPACE];
} Global_Space_Manager;

typedef uint8_t Game_Action_Flags;

#define GAME_ACTION_FLAGS__BIT_IS_ALLOCATED \
    BIT(0)
#define GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND \
    BIT(1)
#define GAME_ACTION_FLAGS__BIT_IS_WITH_PROCESS \
    BIT(2)
#define GAME_ACTION_FLAGS__BIT_IS_PROCESSED_ON_INVOCATION_OR_RESPONSE \
    BIT(3)
#define GAME_ACTION_FLAGS__BIT_IS_RESPONSE \
    BIT(4)
///
/// If Local, it will not be sent over tcp
///
#define GAME_ACTION_FLAGS__BIT_IS_LOCAL \
    BIT(5)
#define GAME_ACTION_FLAGS__BIT_IS_BROADCASTED \
    BIT(6)
#define GAME_ACTION_FLAGS__BIT_IS_BAD_REQUEST \
    BIT(7)

#define GAME_ACTION_FLAGS__NONE 0

#define GAME_ACTION_FLAG_MASK__INBOUND_SANITIZE \
    (GAME_ACTION_FLAGS__BIT_IS_ALLOCATED \
     | GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND)
#define GAME_ACTION_FLAG_MASK__OUTBOUND_SANITIZE \
    (GAME_ACTION_FLAGS__BIT_IS_ALLOCATED)

#define GAME_ACTION_FLAGS__INBOUND_SANITIZE \
    (GAME_ACTION_FLAGS__BIT_IS_IN_OR__OUT_BOUND)
#define GAME_ACTION_FLAGS__OUTBOUND_SANITIZE \
    (GAME_ACTION_FLAGS__NONE)

typedef struct _Game_Action_Header_t {
    Serialization_Header _serialiation_header;
    union {
        struct {
            Identifier__u32 uuid_of__client__u32;
            ///
            /// Primarily used only for TCP_Delivery, but
            /// open to use if ONLY for custom game_actions.
            ///
            Identifier__u32 uuid_of__game_action__responding_to;
        };
        ///
        /// Set to out of bounds for a global broadcast
        ///
        Vector__3i32F4 vector_3i32F4__broadcast_point;
    };
    Game_Action_Kind the_kind_of_game_action__this_action_is;
    Game_Action_Flags game_action_flags;
} _Game_Action_Header;

///
/// Game actions are invoked using the m_Process signature.
/// If your game action is NOT processed, then m_process will
/// be null in your invocation.
///
typedef struct Game_Action_t {
    union {
        struct {
            Serialization_Header _serialiation_header;
            union {
                struct {
                    Identifier__u32 uuid_of__client__u32;
                    ///
                    /// Primarily used only for TCP_Delivery, but
                    /// open to use if ONLY for custom game_actions.
                    ///
                    Identifier__u32 uuid_of__game_action__responding_to;
                };
                ///
                /// Set to out of bounds for a global broadcast
                ///
                Vector__3i32F4 vector_3i32F4__broadcast_point;
            };
            Game_Action_Kind the_kind_of_game_action__this_action_is;
            Game_Action_Flags game_action_flags;
        };
        _Game_Action_Header _game_action_header;
    };

    ///
    /// Extend Game_Action here:
    ///
    union {
        /// ------------
        ///     General
        /// ------------
        struct {
            uint32_t ga_kind__bad_request__request_error_code;
        };

        /// ------------
        ///     TCP
        /// ------------

        union {
            struct {
                IPv4_Address ga_kind__tcp_connect__begin__ipv4_address;
                Identifier__u32 ga_kind__tcp_connect__begin__session__uuid__u32;
            }; // Connect__Begin
            struct {
                Identifier__u64 ga_kind__tcp_connect__session_token;
            }; // Connect
            struct {
#define GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES\
                (sizeof(TCP_Packet)\
                - sizeof(_Game_Action_Header)\
                - sizeof(uint64_t))
#define TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)\
                ((sizeof(type)\
                        + GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES)\
                        / GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES)
#define TCP_PAYLOAD_BITMAP__QUANTITY_OF__BYTES(type)\
                (TCP_PAYLOAD_BITMAP__QUANTITY_OF_PAYLOADS\
                    * GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES)
#define TCP_PAYLOAD_BITMAP(type, name)\
                u8 name[TCP_PAYLOAD_BITMAP__QUANTITY_OF__PAYLOADS(type)]
#define TCP_PAYLOAD_BIT(index) (index & MASK(3))
#define TCP_PAYLOAD_BYTE(index) (index >> 3)
                u8 ga_kind__tcp_delivery__payload[
                    GA_KIND__TCP_DELIVERY__PAYLOAD_SIZE_IN__BYTES];
                Quantity__u16 ga_kind__tcp_delivery__packet_index;
            }; // Delivery
        }; // TCP

        /// ------------
        /// </  TCP    >
        /// ------------

        /// ---------------------
        ///     Global_Space
        /// ---------------------

        union {
            struct {
                Global_Space_Vector__3i32 
                    ga_kind__global_space__request__gsv_3i32;
                TCP_PAYLOAD_BITMAP(Chunk, 
                        ga_kind__global_space__request__chunk_payload_bitmap);
                // in seconds:
#define GA_KIND__GBLOAL_SPACE__REQUEST__TIMEOUT 4
                Timer__u32 ga_kind__global_space__request__timeout;
            }; // Global_Space__Request
            struct {
                Global_Space_Vector__3i32 
                    ga_kind__global_space__resolve__gsv__3i32;
            }; // Global_Space__Resolve
            struct {
                Global_Space_Vector__3i32 
                    ga_kind__global_space__store__gsv__3i32;
            }; // Global_Space__Store
        }; // Global_Space

        /// ---------------------
        /// </   Global_Space   >
        /// ---------------------
    };
} Game_Action;

#define MAX_QUANTITY_OF__GAME_ACTIONS 512

typedef struct Game_Action_Manager_t {
    Game_Action game_actions[
        MAX_QUANTITY_OF__GAME_ACTIONS];
    Repeatable_Psuedo_Random repeatable_pseudo_random;
} Game_Action_Manager;

typedef struct Game_Action_Logic_Entry_t {
    m_Process m_process_of__game_action__inbound;
    m_Process m_process_of__game_action__outbound;
    Game_Action_Flags game_action_flags__inbound;
    Game_Action_Flags game_action_flags__inbound_mask;
    Game_Action_Flags game_action_flags__outbound;
    Game_Action_Flags game_action_flags__outbound_mask;
    Process_Flags__u8 process_flags_of__game_action__outbound;
    Process_Flags__u8 process_flags_of__game_action__inbound;
} Game_Action_Logic_Entry;

typedef struct Game_Action_Logic_Table_t {
    Game_Action_Logic_Entry game_action_logic_entries[
        Game_Action_Kind__Unknown];
} Game_Action_Logic_Table;

typedef struct Client_t {
    Serialization_Header _serialization_header;
    Game_Action_Manager game_action_manager__inbound;
    Game_Action_Manager game_action_manager__outbound;
    Local_Space_Manager local_space_manager;
    Serialized_Field s_entity_of__client;
} Client;

#define WORLD_NAME_MAX_SIZE_OF 32
typedef char World_Name_String[WORLD_NAME_MAX_SIZE_OF];

typedef struct World_t {
    Serialization_Header _serialization_header;
    Entity_Manager entity_manager;

    Chunk_Manager chunk_manager;
    Collision_Manager collision_manager;

    Global_Space_Manager global_space_manager;
    Collision_Node_Pool collision_node_pool;
    Chunk_Pool chunk_pool;
    Hitbox_AABB_Manager hitbox_aabb_manager;

    Structure_Manager structure_manager;
    Tile_Logic_Manager tile_logic_manager;
    World_Parameters world_parameters;
    Repeatable_Psuedo_Random repeatable_pseudo_random;

    Inventory_Manager   inventory_manager;
    Item_Manager        item_manager;

    Camera camera;
    PLATFORM_Graphics_Window *p_PLATFORM_graphics_window_for__world;

    World_Name_String name;
    Quantity__u8 length_of__world_name;
} World;

///
/// SECTION_gfx_window
///

#define MAX_QUANTITY_OF__GRAPHICS_WINDOWS 8

typedef uint8_t Graphics_Window_Flags__u8;

#define GRAPHICS_WINDOW__FLAG__IS_RENDERING_WORLD BIT(0)
#define GRAPHICS_WINDOW__FLAG__COMPOSE__DIRTY BIT(1)

#define GRAPHICS_WINDOW__FLAGS__NONE 0

typedef struct Graphics_Window_t {
    UI_Tile_Map__Wrapper ui_tile_map__wrapper;
    Vector__3i32 origin_of__gfx_window;
    Vector__3i32 position_of__gfx_window;
    Vector__3i32 position_of__gfx_window__minimum;
    Vector__3i32 position_of__gfx_window__maximum;
    Camera *p_camera;
    UI_Manager *p_ui_manager;
    PLATFORM_Graphics_Window *p_PLATFORM_gfx_window;
    struct Graphics_Window_t *p_child__graphics_window;
    Graphics_Window_Kind the_kind_of__window;
    Index__u8 priority_of__window;
    Graphics_Window_Flags__u8 graphics_window__flags;
} Graphics_Window;

typedef struct Graphics_Window_Manager_t {
    Graphics_Window graphics_windows[
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS];
} Graphics_Window_Manager;

///
/// SECTION_core
///

typedef struct Gfx_Context_t {
    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context;
    Graphics_Window_Manager graphics_window_manager;
    Sprite_Gfx_Allocation_Manager sprite_gfx_allocation_manager;
    Aliased_Texture_Manager aliased_texture_manager;
    UI_Context ui_context;
    UI_Manager ui_manager;
    UI_Tile_Map_Manager ui_tile_map_manager;
} Gfx_Context;

typedef struct Game_Action_t Game_Action;
typedef bool (*m_Game_Action_Handler)(
        Game *p_this_game,
        Client *p_client,
        Game_Action *p_game_action);

typedef struct Game_t {
    Input input;
    Scene_Manager scene_manager;

    World world;

    Process_Manager process_manager;
    Sort_List_Manager sort_list_manager;
    Path_List_Manager path_list_manager;

    Log log__global;
    Log log__local;
    Log log__system;

    Gfx_Context gfx_context;
    PLATFORM_Audio_Context *p_PLATFORM_audio_context;
    PLATFORM_File_System_Context *p_PLATFORM_file_system_context;

    Game_Action_Logic_Table game_action_logic_table;

    // TODO: obselete
    // m_Game_Action_Handler m_game_action_handler;

    Timer__u32 tick__timer_u32;
    Timer__u32 time__seconds__u32;
    Timer__u32 time__nanoseconds__u32;

    Quantity__u32 max_quantity_of__clients;
    Quantity__u32 quantity_of__clients;
    Client *pM_clients;
    Client **pM_ptr_array_of__clients;
    TCP_Socket_Manager *pM_tcp_socket_manager;

    m_Game_Action_Handler m_game_action_handler__dispatch;
    m_Game_Action_Handler m_game_action_handler__receive;
    m_Game_Action_Handler m_game_action_handler__resolve;

    u32F20 time_elapsed__u32F20;
    u32F20 tick_accumilator__u32F20;
    bool is_world__initialized;
} Game;

#endif
