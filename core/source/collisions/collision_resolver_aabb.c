#include "collisions/collision_resolver_aabb.h"
#include "collisions/collision_node.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "degree.h"
#include "game.h"
#include "game_action/core/hitbox/game_action__hitbox.h"
#include "numerics.h"
#include "platform_defines.h"
#include "vectors.h"
#include "world/chunk.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"
#include "world/local_space.h"
#include "world/tile.h"
#include "world/tile_vectors.h"
#include "world/tile_logic_table.h"
#include "world/world.h"
#include "raycast/ray.h"

void f_hitbox_aabb_collision_handler__default(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb__colliding,
        Hitbox_AABB *p_hitbox_aabb__collided) {
    int32_t source_x = get_x_i32F4_from__hitbox(p_hitbox_aabb__colliding);
    int32_t source_y = get_y_i32F4_from__hitbox(p_hitbox_aabb__colliding);
    int32_t collided_x = get_x_i32F4_from__hitbox(p_hitbox_aabb__collided);
    int32_t collided_y = get_y_i32F4_from__hitbox(p_hitbox_aabb__collided);

    int32_t delta_x = 
        source_x - collided_x;
    int32_t delta_y = 
        source_y - collided_y;

    Quantity__u32 width_of__source =
        get_width_u32_of__hitbox_aabb(p_hitbox_aabb__colliding);
    Quantity__u32 height_of__source =
        get_height_u32_of__hitbox_aabb(p_hitbox_aabb__colliding);

    Quantity__u32 width_of__collided =
        get_width_u32_of__hitbox_aabb(p_hitbox_aabb__collided);
    Quantity__u32 height_of__collided =
        get_height_u32_of__hitbox_aabb(p_hitbox_aabb__collided);

    Signed_Quantity__i32 ideal_delta_x =
        width_of__collided + width_of__source;
    Signed_Quantity__i32 ideal_delta_y =
        height_of__collided + height_of__source;


    if (delta_x * delta_x < COLLISION_DELTA_THRESHOLD) {
        p_hitbox_aabb__collided->velocity__3i32F4.x__i32F4 = 
            (ideal_delta_x - delta_x) >> 2
            ;
        p_hitbox_aabb__colliding->velocity__3i32F4.x__i32F4 =
            (ideal_delta_x + delta_x) >> 2
            ;
    }

    if (delta_y * delta_y < COLLISION_DELTA_THRESHOLD) {
        p_hitbox_aabb__collided->velocity__3i32F4.y__i32F4 =
            (ideal_delta_y - delta_y) >> 2
            ;
        p_hitbox_aabb__colliding->velocity__3i32F4.y__i32F4 = 
            (ideal_delta_y + delta_y) >> 2
            ;
    }
}

void f_hitbox_aabb_tile_touch_handler__default(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb,
        Tile *p_tile,
        Signed_Index__i32 x_collision__i32,
        Signed_Index__i32 y_collision__i32) {
    // TODO: only occur if tile is unpassable, since
    // later on tile_logic flags will be changed.
    Vector__3i32F4 tile_center =
        get_vector__3i32F4(
                ARITHMETRIC_L_SHIFT(
                    x_collision__i32,
                    FRACTIONAL_PERCISION_4__BIT_SIZE)
                + 0b1000, 
                ARITHMETRIC_L_SHIFT(
                    y_collision__i32,
                    FRACTIONAL_PERCISION_4__BIT_SIZE)
                + 0b1000, 
                0);

    Signed_Index__i32 delta_x =
        get_x_i32F4_from__hitbox(p_hitbox_aabb)
        - tile_center.x__i32F4;
    Signed_Index__i32 delta_y =
        get_y_i32F4_from__hitbox(p_hitbox_aabb)
        - tile_center.y__i32F4;

    Signed_Index__i32 ideal_delta_x =
        (TILE__WIDTH_AND__HEIGHT_IN__PIXELS
        + get_width_u32_of__hitbox_aabb(p_hitbox_aabb))
        // TODO: why bitshift of 2?
        >> 2;
    Signed_Index__i32 ideal_delta_y =
        (TILE__WIDTH_AND__HEIGHT_IN__PIXELS
        + get_height_u32_of__hitbox_aabb(p_hitbox_aabb))
        >> 2;

    if (delta_x * delta_x >= delta_y * delta_y) {
        p_hitbox_aabb->velocity__3i32F4.x__i32F4 =
            -(ideal_delta_x - delta_x) >> 2
            ;
    }
    if (delta_x * delta_x <= delta_y * delta_y) {
        p_hitbox_aabb->velocity__3i32F4.y__i32F4 =
            -(ideal_delta_y - delta_y) >> 2
            ;
    }
}

void poll_collision_resolver_aabb(
        Game *p_game,
        Hitbox_AABB_Manager *p_hitbox_aabb_manager,
        f_Hitbox_AABB_Collision_Handler f_hitbox_aabb_collision_handler,
        f_Hitbox_AABB_Tile_Touch_Handler f_hitbox_aabb_tile_touch_handler) {
    for(Index__u32 index_of__hitbox = 0;
            index_of__hitbox < MAX_QUANTITY_OF__HITBOX_AABB;
            index_of__hitbox++) {
        Hitbox_AABB *p_hitbox_aabb =
            get_p_hitbox_aabb_by__index_from__hitbox_aabb_manager(
                    p_hitbox_aabb_manager,
                    index_of__hitbox);

        if (!p_hitbox_aabb)
            break;

        Local_Space_Manager *p_local_space_manager =
            get_p_local_space_manager_thats__closest_to__this_position(
                    p_game, 
                    get_position_3i32_of__hitbox_aabb(p_hitbox_aabb));
    
        if (!p_local_space_manager) {
            // TODO: dispose hitbox
#warning TODO: dispose hitbox
            continue;
        }

        if (f_hitbox_aabb_collision_handler) {
            poll_hitbox_aabb_for__tile_collision(
                    p_game, 
                    p_local_space_manager, 
                    p_hitbox_aabb, 
                    f_hitbox_aabb_tile_touch_handler);
        }

        Local_Space *p_local_space =
            get_p_local_space_from__local_space_manager(
                    p_local_space_manager, 
                    vector_3i32_to__chunk_vector_3i32(
                        get_position_3i32_of__hitbox_aabb(
                            p_hitbox_aabb)));

        if (!p_local_space 
                || !is_local_space__active(p_local_space)
                || !f_hitbox_aabb_collision_handler) {
            // TODO: unload presence.
            continue;
        }

        poll_for__collisions_within_this__collision_node(
                p_game, 
                get_p_world_from__game(p_game), 
                get_p_collision_node_from__local_space(
                    p_local_space), 
                f_hitbox_aabb_collision_handler, 
                p_hitbox_aabb);
        if (is_local_space__active(p_local_space
                    ->p_local_space__north)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__north), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__north
                    ->p_local_space__east)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__north
                        ->p_local_space__east), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__east)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__east), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__south
                    ->p_local_space__east)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__south
                        ->p_local_space__east), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__south)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__east), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__south
                    ->p_local_space__west)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__south
                        ->p_local_space__west), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__west)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__west), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
        if (is_local_space__active(
                    p_local_space
                    ->p_local_space__north
                    ->p_local_space__west)) {
            poll_for__collisions_within_this__collision_node(
                    p_game, 
                    get_p_world_from__game(p_game), 
                    get_p_collision_node_from__local_space(
                        p_local_space
                        ->p_local_space__north
                        ->p_local_space__west), 
                    f_hitbox_aabb_collision_handler, 
                    p_hitbox_aabb);
        }
    }
}

void poll_hitbox_aabb_for__tile_collision(
        Game *p_game,
        Local_Space_Manager *p_local_space_manager,
        Hitbox_AABB *p_hitbox_aabb,
        f_Hitbox_AABB_Tile_Touch_Handler f_hitbox_aabb_tile_touch_handler) {

    Vector__3i32F4 aa, bb;
    get_aa_bb_as__vectors_3i32F4_from__hitbox(
            p_hitbox_aabb, &aa, &bb);

    Vector__3i32F4 position__3i32F4 =
        get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb);
    Vector__3i32F4 velocity__3i32F4 =
        get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb);

    u8 local_z_tile = get_tile_z_u8_from__vector_3i32F4(
            get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb));

    //TODO: magic num
    i32F4 chunk_xy_vectors[8] = {
        get_chunk_x_i32_from__vector_3i32F4(aa),
        get_chunk_y_i32_from__vector_3i32F4(aa),
        get_chunk_x_i32_from__vector_3i32F4(bb),
        get_chunk_y_i32_from__vector_3i32F4(aa),
        get_chunk_x_i32_from__vector_3i32F4(aa),
        get_chunk_y_i32_from__vector_3i32F4(bb),
        get_chunk_x_i32_from__vector_3i32F4(bb),
        get_chunk_y_i32_from__vector_3i32F4(bb),
    };
    Signed_Index__i32 local_positions[8] = {
        get_tile_x_u8_from__vector_3i32F4(aa),
        get_tile_y_u8_from__vector_3i32F4(aa),
        get_tile_x_u8_from__vector_3i32F4(bb),
        get_tile_y_u8_from__vector_3i32F4(aa),
        get_tile_x_u8_from__vector_3i32F4(aa),
        get_tile_y_u8_from__vector_3i32F4(bb),
        get_tile_x_u8_from__vector_3i32F4(bb),
        get_tile_y_u8_from__vector_3i32F4(bb),
    };
    Signed_Index__i32 corner_positions[8] = {
        i32F4_to__i32(aa.x__i32F4), i32F4_to__i32(aa.y__i32F4),
        i32F4_to__i32(bb.x__i32F4), i32F4_to__i32(aa.y__i32F4),
        i32F4_to__i32(aa.x__i32F4), i32F4_to__i32(bb.y__i32F4),
        i32F4_to__i32(bb.x__i32F4), i32F4_to__i32(bb.y__i32F4)
    };
    Direction__u8 directions[4] = {
        DIRECTION__SOUTH_EAST,
        DIRECTION__SOUTH_WEST,
        DIRECTION__NORTH_EAST,
        DIRECTION__NORTH_WEST
    };

    if (velocity__3i32F4.z__i32F4 < 0) {
        Vector__3i32F4 ray_begin__3i32F4 =
            (Vector__3i32F4){
            0, 0,
            position__3i32F4.z__i32F4
            };
        Ray__3i32F20 ray__3i32F20 =
            get_ray(ray_begin__3i32F4, ANGLE__180, Ray_Plane_Mode__XZ);
        do {
            for (Index__u32 index=0;index<8;index+=2) {
                i32F4 z_ground_tile__i32F4 = 
                    get_z_i32F4_from__hitbox(p_hitbox_aabb)
                    - get_z_offset_i32F4_of__ray(
                            &ray__3i32F20)
                    ;
                if ((z_ground_tile__i32F4 & MASK(FRACTIONAL_PERCISION_4__BIT_SIZE
                            + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT))
                        > BIT(FRACTIONAL_PERCISION_4__BIT_SIZE
                            + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT - 1)) {
                    // round up
                    z_ground_tile__i32F4 += i32_to__i32F4(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT - 1));
                }
                z_ground_tile__i32F4 &= ~MASK(FRACTIONAL_PERCISION_4__BIT_SIZE
                        + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT);
                Tile *p_tile = 
                    get_p_tile_by__3i32F4_from__local_space_manager(
                            p_local_space_manager, 
                            (Vector__3i32F4){
                                i32_to__i32F4(corner_positions[index]),
                                i32_to__i32F4(corner_positions[index+1]),
                                z_ground_tile__i32F4
                            });
                if (!p_tile)
                    continue;
                if (!poll__is_tile__without_ground(
                            get_p_tile_logic_table_from__world(
                                get_p_world_from__game(p_game)), 
                            p_tile)) {
                    z_ground_tile__i32F4 +=
                        poll__tile_height(
                                get_p_tile_logic_table_from__world(
                                    get_p_world_from__game(p_game)), 
                                p_tile);
                    dispatch_game_action__hitbox(
                            p_game, 
                            GET_UUID_P(p_hitbox_aabb), 
                            get_vector__3i32F4(
                                get_x_i32F4_from__hitbox(p_hitbox_aabb), 
                                get_y_i32F4_from__hitbox(p_hitbox_aabb), 
                                z_ground_tile__i32F4), 
                            get_vector__3i32F4(
                                get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb).x__i32F4, 
                                get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb).y__i32F4, 
                                0), 
                            get_vector__3i16F8(
                                get_acceleration_3i16F8_of__hitbox_aabb(p_hitbox_aabb).x__i16F8, 
                                get_acceleration_3i16F8_of__hitbox_aabb(p_hitbox_aabb).y__i16F8, 
                                0));
                    goto landed_on_ground;
                }
            }
            step_p_ray_until__next_tile(&ray__3i32F20);
        } while (is_p_ray_within__squared_length_i32F4(
                    &ray__3i32F20, 
                    multiply__i32F4(velocity__3i32F4.z__i32F4,
                        velocity__3i32F4.z__i32F4)));
    }
landed_on_ground:;

    Tile *p_tile = get_p_tile_by__3i32F4_from__local_space_manager(
            p_local_space_manager, 
            get_position_3i32F4_of__hitbox_aabb(p_hitbox_aabb));
    if (!poll__is_tile__without_ground(
                get_p_tile_logic_table_from__world(
                    get_p_world_from__game(p_game)),
                p_tile)
            && (p_hitbox_aabb->position__3i32F4.z__i32F4
            & MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT 
                + FRACTIONAL_PERCISION_4__BIT_SIZE)) >= TILE_STAIR_HEIGHT) {
        Vector__3i32F4 offset__3i32F4 =
            get_2i32F4_offset_from__angle(
                    get_angle_from__direction(
                        get_movement_direction_of__hitbox(
                            p_hitbox_aabb)));
        offset__3i32F4.x__i32F4 <<= FRACTIONAL_PERCISION_4__BIT_SIZE - 1;
        offset__3i32F4.y__i32F4 <<= FRACTIONAL_PERCISION_4__BIT_SIZE - 1;
        Tile_Logic_Record tile_logic_record;
        Vector__3i32F4 forward_position__3i32F4 =
            (Vector__3i32F4){
                get_x_i32F4_from__hitbox(p_hitbox_aabb) + offset__3i32F4.x__i32F4,
                get_y_i32F4_from__hitbox(p_hitbox_aabb) + offset__3i32F4.y__i32F4,
                (get_z_i32F4_from__hitbox(
                        p_hitbox_aabb) & ~MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT 
                            + FRACTIONAL_PERCISION_4__BIT_SIZE))
                    + i32_to__i32F4(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT))
            };
        p_tile = get_p_tile_by__3i32F4_from__local_space_manager(
                p_local_space_manager, 
                forward_position__3i32F4);

        get_tile_logic_record_for__this_tile(
                get_p_tile_logic_table_from__world(
                    get_p_world_from__game(p_game)), 
                &tile_logic_record, 
                p_tile);
        if (!is_tile_logic_record__unpassable(&tile_logic_record)
                && !is_tile_logic_record__without_ground(&tile_logic_record)) {
            dispatch_game_action__hitbox(
                    p_game, 
                    GET_UUID_P(p_hitbox_aabb), 
                    forward_position__3i32F4,
                    // get_vector__3i32F4(
                    //     get_x_i32F4_from__hitbox(p_hitbox_aabb), 
                    //     get_y_i32F4_from__hitbox(p_hitbox_aabb), 
                    //     get_z_i32F4_from__hitbox(p_hitbox_aabb)
                    //     + i32_to__i32F4(BIT(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT))),
                    get_velocity_3i32F4_of__hitbox_aabb(p_hitbox_aabb),
                    get_acceleration_3i16F8_of__hitbox_aabb(p_hitbox_aabb));
            return;
        }
    }

    for (Index__u32 index=0;index<8;index+=2) {
        Signed_Index__i32 x__chunk =
            chunk_xy_vectors[index]; //entity->hitbox.x__chunk;
        Signed_Index__i32 y__chunk =
            chunk_xy_vectors[index+1]; //entity->hitbox.y__chunk;

        Chunk_Vector__3i32 gsv__3i32 =
            get_vector__3i32(
                    x__chunk, 
                    y__chunk, 
                    get_chunk_z_i32_from__hitbox(p_hitbox_aabb));

        Local_Space *p_local_space =
            get_p_local_space_from__local_space_manager(
                    p_local_space_manager, 
                    gsv__3i32);

        if (!is_local_space__active(
                    p_local_space)) {
            continue;
        }

        Chunk *p_chunk =
            get_p_chunk_from__local_space(p_local_space);

        if (!p_chunk) {
            debug_warning__verbose("access attempt: %d, %d",
                    x__chunk, y__chunk);
            debug_error("poll_hitbox_aabb_for__tile_collision, hitbox out of bounds.");
            return;
        }

        Tile *p_tile =
            get_p_tile_from__chunk_using__u8(
                    p_chunk,
                    local_positions[index],
                    local_positions[index+1],
                    local_z_tile);

        // TODO: rename unpassable to something else,
        // as this is just polling for touch-tile logic.
        if (poll__is_tile__unpassable(
                    get_p_tile_logic_table_from__world(
                        get_p_world_from__game(p_game)), 
                    p_tile)) {
            f_hitbox_aabb_tile_touch_handler(
                    p_game,
                    get_p_world_from__game(p_game),
                    p_hitbox_aabb,
                    p_tile,
                    corner_positions[index],
                    corner_positions[index+1]);
        }
    }
    return;
}
