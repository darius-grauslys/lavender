#include "world/local_space_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "vectors.h"
#include "world/chunk.h"
#include "world/chunk_vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/local_space.h"
#include "world/tile_vectors.h"
#include "world/world.h"

static inline
Local_Space *get_p_local_space_by__index_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Index__u32 index_of__local_space) {
#ifndef NDEBUG
    if (index_of__local_space > AREA_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__index_from__local_space_manager, index out of range, %d/%d", index_of__local_space, AREA_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
#endif
    return &p_local_space_manager->local_spaces[index_of__local_space];
}

static inline
Local_Space *get_p_local_space_by__local_xy_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        u32 x__u32,
        u32 y__u32) {
#ifndef NDEBUG
    if (x__u32 >= WIDTH_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__local_xy_from__local_space_manager, x out of bounds: %d/%d", x__u32, WIDTH_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
    if (y__u32 >= HEIGHT_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__local_xy_from__local_space_manager, y out of bounds: %d/%d", y__u32, WIDTH_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
#endif
    return &p_local_space_manager->local_spaces[
        x__u32
        + (y__u32 * WIDTH_OF__LOCAL_SPACE_MANAGER)];
}

void initialize_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Global_Space_Vector__3i32 center_of__local_space_manager__3i32) {
    memset(p_local_space_manager,
            0,
            sizeof(Local_Space_Manager));

    for (i32 y__i32 = 0;
            y__i32 < HEIGHT_OF__LOCAL_SPACE_MANAGER;
            y__i32++) {
        for (i32 x__i32 = 0;
                x__i32 < WIDTH_OF__LOCAL_SPACE_MANAGER;
                x__i32++) {
            Local_Space *p_local_space__here =
                get_p_local_space_by__local_xy_from__local_space_manager(
                        p_local_space_manager, 
                        x__i32, 
                        y__i32);

            i32 x__left = 
                (x__i32)
                ? x__i32 - 1
                : WIDTH_OF__LOCAL_SPACE_MANAGER - 1
                ;
            i32 x__right = 
                (x__i32 + 1 < WIDTH_OF__LOCAL_SPACE_MANAGER)
                ? x__i32 + 1
                : 0
                ;

            i32 y__down = 
                (y__i32)
                ? y__i32 - 1
                : HEIGHT_OF__LOCAL_SPACE_MANAGER - 1
                ;
            i32 y__up = 
                (y__i32 + 1 < HEIGHT_OF__LOCAL_SPACE_MANAGER)
                ? y__i32 + 1
                : 0
                ;

            set_neighbors_of__local_space(
                    p_local_space__here, 
                    get_p_local_space_by__local_xy_from__local_space_manager(
                        p_local_space_manager, 
                        x__i32, y__up), 
                    get_p_local_space_by__local_xy_from__local_space_manager(
                        p_local_space_manager, 
                        x__right, y__i32), 
                    get_p_local_space_by__local_xy_from__local_space_manager(
                        p_local_space_manager, 
                        x__i32, y__down), 
                    get_p_local_space_by__local_xy_from__local_space_manager(
                        p_local_space_manager, 
                        x__left, y__i32));
            p_local_space__here->global_space__vector__3i32 =
                get_vector__3i32(
                        x__i32
                        + center_of__local_space_manager__3i32.x__i32
                        - (WIDTH_OF__LOCAL_SPACE_MANAGER>>1), 
                        y__i32
                        + center_of__local_space_manager__3i32.y__i32
                        - (HEIGHT_OF__LOCAL_SPACE_MANAGER>>1), 
                        0);
        }
    }

    p_local_space_manager->p_local_space__south_west =
        get_p_local_space_by__local_xy_from__local_space_manager(
                p_local_space_manager, 
                0, 
                0);
    p_local_space_manager->p_local_space__south_east =
        get_p_local_space_by__local_xy_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER - 1, 
                0);
    p_local_space_manager->p_local_space__north_west =
        get_p_local_space_by__local_xy_from__local_space_manager(
                p_local_space_manager, 
                0, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1);
    p_local_space_manager->p_local_space__north_east =
        get_p_local_space_by__local_xy_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER-1, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1);
}

void drop_all__local_spaces_in__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game) {
    for (Index__u32 index_of__local_space = 0;
            index_of__local_space < AREA_OF__LOCAL_SPACE_MANAGER;
            index_of__local_space++) {
        Local_Space *p_local_space =
            get_p_local_space_by__index_from__local_space_manager(
                    p_local_space_manager, 
                    index_of__local_space);
        if (!get_p_global_space_from__local_space(p_local_space)) {
            continue;
        }
        drop_global_space_within__global_space_manager(
                p_game,
                p_local_space->global_space__vector__3i32);
    }
}

void hold_all__unheld_local_spaces_in__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game) {
    for (Index__u32 index_of__local_space = 0;
            index_of__local_space < AREA_OF__LOCAL_SPACE_MANAGER;
            index_of__local_space++) {
        Local_Space *p_local_space =
            get_p_local_space_by__index_from__local_space_manager(
                    p_local_space_manager, 
                    index_of__local_space);
        if (get_p_global_space_from__local_space(p_local_space)) {
            continue;
        }
        p_local_space->p_global_space =
            hold_global_space_within__global_space_manager(
                    p_game,
                    p_local_space->global_space__vector__3i32);
    }
}

void set_center_of__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Global_Space_Vector__3i32 center_of__local_space_manager__3i32) {
    if (is_vectors_3i32__equal(
                p_local_space_manager
                ->center_of__local_space_manager__3i32, 
                center_of__local_space_manager__3i32)) {
        return;
    }
    
    Global_Space_Vector__3i32 distance_manhattan__3i32 =
        subtract_vectors__3i32(
                p_local_space_manager
                ->center_of__local_space_manager__3i32, 
                center_of__local_space_manager__3i32);

    // TODO: z

    if ((u32)distance_manhattan__3i32.x__i32 + 1 < 3
            && (u32)distance_manhattan__3i32.y__i32 + 1 < 3) {
        Direction__u8 direction = DIRECTION__NONE;
        if (distance_manhattan__3i32.x__i32 < 0)
            direction |= DIRECTION__WEST;
        else if (distance_manhattan__3i32.x__i32 > 0)
            direction |= DIRECTION__EAST;

        if (distance_manhattan__3i32.y__i32 < 0)
            direction |= DIRECTION__SOUTH;
        else if (distance_manhattan__3i32.y__i32 > 0)
            direction |= DIRECTION__NORTH;

        move_local_space_manager(
                p_local_space_manager, 
                p_game, 
                direction);

        return;
    }

    drop_all__local_spaces_in__local_space_manager(
            p_local_space_manager,
            p_game);
    initialize_local_space_manager(
            p_local_space_manager,
            center_of__local_space_manager__3i32);
    hold_all__unheld_local_spaces_in__local_space_manager(
            p_local_space_manager,
            p_game);

    p_local_space_manager
        ->center_of__local_space_manager__3i32 =
        center_of__local_space_manager__3i32;
}

static inline
void move_p_ptr_local_space__north(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__north;
}

static inline
void move_p_ptr_local_space__south(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__south;
}

static inline
void move_p_ptr_local_space__east(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__east;
}

static inline
void move_p_ptr_local_space__west(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__west;
}

bool poll_local_space__traversal(
        Local_Space **p_ptr_local_space,
        Local_Space *p_local_space__end,
        Direction__u8 direction_to__traverse) {
    switch (direction_to__traverse) {
        default:
            return false;
        case DIRECTION__NORTH:
            move_p_ptr_local_space__north(p_ptr_local_space);
            break;
        case DIRECTION__EAST:
            move_p_ptr_local_space__east(p_ptr_local_space);
            break;
        case DIRECTION__SOUTH:
            move_p_ptr_local_space__south(p_ptr_local_space);
            break;
        case DIRECTION__WEST:
            move_p_ptr_local_space__west(p_ptr_local_space);
            break;
    }

    return *p_ptr_local_space != p_local_space__end;
}

void update_local_spaces_between__these_two_local_spaces(
        Game *p_game,
        Local_Space *p_local_space__current,
        Local_Space *p_local_space__end,
        Direction__u8 direction_to__update) {
    switch(direction_to__update) {
        default:
            return;
        case DIRECTION__NORTH:
        case DIRECTION__EAST:
        case DIRECTION__SOUTH:
        case DIRECTION__WEST:
            break;
    }
    do {
        if (get_p_global_space_from__local_space(p_local_space__current)) {
            drop_global_space_within__global_space_manager(
                    p_game, 
                    p_local_space__current->global_space__vector__3i32
                    );
            p_local_space__current->p_global_space = 0;
        }

        switch (direction_to__update) {
            default:
            case DIRECTION__NORTH:
                p_local_space__current->global_space__vector__3i32 =
                    p_local_space__current
                    ->p_local_space__south
                    ->global_space__vector__3i32;
                p_local_space__current->global_space__vector__3i32.y__i32++;
                break;
            case DIRECTION__EAST:
                p_local_space__current->global_space__vector__3i32 =
                    p_local_space__current
                    ->p_local_space__west
                    ->global_space__vector__3i32;
                p_local_space__current->global_space__vector__3i32.x__i32++;
                break;
            case DIRECTION__SOUTH:
                p_local_space__current->global_space__vector__3i32 =
                    p_local_space__current
                    ->p_local_space__north
                    ->global_space__vector__3i32;
                p_local_space__current->global_space__vector__3i32.y__i32--;
                break;
            case DIRECTION__WEST:
                p_local_space__current->global_space__vector__3i32 =
                    p_local_space__current
                    ->p_local_space__east
                    ->global_space__vector__3i32;
                p_local_space__current->global_space__vector__3i32.x__i32--;
                break;
        }

        p_local_space__current->p_global_space =
            hold_global_space_within__global_space_manager(
                    p_game,
                    p_local_space__current->global_space__vector__3i32);
    } while (poll_local_space__traversal(
                &p_local_space__current, 
                p_local_space__end,
                direction_to__update));
}

void move_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Direction__u8 direction__u8) {
    if (direction__u8 & DIRECTION__NORTH) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .y__i32++;

        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_west);

        update_local_spaces_between__these_two_local_spaces(
                p_game,
                p_local_space_manager->p_local_space__north_west, 
                p_local_space_manager->p_local_space__north_east, 
                DIRECTION__EAST);
    }
    else if (direction__u8 & DIRECTION__SOUTH) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .y__i32--;

        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_west);

        update_local_spaces_between__these_two_local_spaces(
                p_game,
                p_local_space_manager->p_local_space__south_west, 
                p_local_space_manager->p_local_space__south_east, 
                DIRECTION__EAST);
    }
    if (direction__u8 & DIRECTION__EAST) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .x__i32++;

        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_west);

        update_local_spaces_between__these_two_local_spaces(
                p_game,
                p_local_space_manager->p_local_space__north_east, 
                p_local_space_manager->p_local_space__south_east, 
                DIRECTION__SOUTH);
    }
    else if (direction__u8 & DIRECTION__WEST) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .x__i32--;

        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_west);

        update_local_spaces_between__these_two_local_spaces(
                p_game,
                p_local_space_manager->p_local_space__north_west, 
                p_local_space_manager->p_local_space__south_west, 
                DIRECTION__SOUTH);
    }
}

Local_Space *get_p_local_space_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4) {
    Chunk_Vector__3i32 chunk_vector__3i32 = 
        vector_3i32F4_to__chunk_vector_3i32(
                vector__3i32F4);

    if (chunk_vector__3i32.x__i32
            < (p_local_space_manager
                ->center_of__local_space_manager__3i32.x__i32
                - (WIDTH_OF__LOCAL_SPACE_MANAGER>>1))) {
        debug_error("get_p_local_space_by__3i32F4_from__local_space_manager, position out of bonuds.");
        return 0;
    }
    if (chunk_vector__3i32.x__i32
            > (p_local_space_manager
                ->center_of__local_space_manager__3i32.x__i32
                + (WIDTH_OF__LOCAL_SPACE_MANAGER>>1))) {
        debug_error("get_p_local_space_by__3i32F4_from__local_space_manager, position out of bonuds.");
        return 0;
    }
    if (chunk_vector__3i32.y__i32
            < (p_local_space_manager
                ->center_of__local_space_manager__3i32.y__i32
                - (HEIGHT_OF__LOCAL_SPACE_MANAGER>>1))) {
        debug_error("get_p_local_space_by__3i32F4_from__local_space_manager, position out of bonuds.");
        return 0;
    }
    if (chunk_vector__3i32.y__i32
            > (p_local_space_manager
                ->center_of__local_space_manager__3i32.y__i32
                + (HEIGHT_OF__LOCAL_SPACE_MANAGER>>1))) {
        debug_error("get_p_local_space_by__3i32F4_from__local_space_manager, position out of bonuds.");
        return 0;
    }

    i32 x_delta__i32 = 
        chunk_vector__3i32.x__i32
        - p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.x__i32;
    i32 y_delta__i32 = 
        chunk_vector__3i32.y__i32
        - p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.y__i32;

    Local_Space *p_local_space =
        p_local_space_manager->p_local_space__south_west;
    while (x_delta__i32--) {
        move_p_ptr_local_space__east(&p_local_space);
    }
    while (y_delta__i32--) {
        move_p_ptr_local_space__north(&p_local_space);
    }

    return p_local_space;
}

Tile *get_p_tile_by__3i32F4_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector__3i32F4) {
    Local_Space *p_local_space =
        get_p_local_space_by__3i32F4_from__local_space_manager(
                p_local_space_manager,
                vector__3i32F4);

    if (!is_local_space__allocated(p_local_space))
        return 0;

    Local_Tile_Vector__3u8 local_tile_vector__3u8 =
        vector_3i32F4_to__local_tile_vector_3u8(vector__3i32F4);

    return get_p_tile_from__chunk(
            p_local_space
            ->p_global_space
            ->p_chunk, 
            local_tile_vector__3u8);
}

void poll_local_space_for__scrolling(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Global_Space_Manager *p_global_space_manager,
        Global_Space_Vector__3i32 global_space_vector__center__3i32) {
    if (is_vectors_3i32__equal(
                global_space_vector__center__3i32, 
                p_local_space_manager
                ->center_of__local_space_manager__3i32)) {
        return;
    }

    do {
        i32 d_x__i32 = global_space_vector__center__3i32.x__i32
            - p_local_space_manager->center_of__local_space_manager__3i32.x__i32;
        i32 d_y__i32 = global_space_vector__center__3i32.y__i32
            - p_local_space_manager->center_of__local_space_manager__3i32.y__i32;
        Direction__u8 direction = DIRECTION__NONE;
        if (d_x__i32 < 0)
            direction |= DIRECTION__WEST;
        else if (d_x__i32 > 0)
            direction |= DIRECTION__EAST;
        if (d_y__i32 < 0)
            direction |= DIRECTION__SOUTH;
        else if (d_y__i32 > 0)
            direction |= DIRECTION__NORTH;
        move_local_space_manager(
                p_local_space_manager, 
                p_game,
                direction);
    } while (!is_vectors_3i32__equal(
                global_space_vector__center__3i32, 
                p_local_space_manager
                ->center_of__local_space_manager__3i32));
}

bool is_vector_3i32F4_within__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Vector__3i32F4 vector_3i32F4) {
    Global_Space_Vector__3i32 global_space__3i32 =
        vector_3i32F4_to__chunk_vector_3i32(vector_3i32F4);

    bool is_bounded__x = 
        global_space__3i32.x__i32
        <= p_local_space_manager
            ->p_local_space__north_east
            ->global_space__vector__3i32.x__i32;
    is_bounded__x &=
        global_space__3i32.x__i32
        >= p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.x__i32;
        
    bool is_bounded__y = 
        global_space__3i32.y__i32
        <= p_local_space_manager
            ->p_local_space__north_east
            ->global_space__vector__3i32.y__i32;
    is_bounded__y &=
        global_space__3i32.y__i32
        >= p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.y__i32;

    return is_bounded__x && is_bounded__y;
}
