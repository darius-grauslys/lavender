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
    if (index_of__local_space > VOLUME_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__index_from__local_space_manager, index out of range, %d/%d", index_of__local_space, VOLUME_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
#endif
    return &p_local_space_manager->local_spaces[index_of__local_space];
}

static inline
Local_Space *get_p_local_space_by__local_xyz_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        u32 x__u32,
        u32 y__u32,
        u32 z__u32) {
#ifndef NDEBUG
    if (x__u32 >= WIDTH_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__local_xyz_from__local_space_manager, x out of bounds: %d/%d", x__u32, WIDTH_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
    if (y__u32 >= HEIGHT_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__local_xyz_from__local_space_manager, y out of bounds: %d/%d", y__u32, HEIGHT_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
    if (z__u32 >= DEPTH_OF__LOCAL_SPACE_MANAGER) {
        debug_error("get_p_local_space_by__local_xyz_from__local_space_manager, z out of bounds: %d/%d", z__u32, DEPTH_OF__LOCAL_SPACE_MANAGER);
        return 0;
    }
#endif
    return &p_local_space_manager->local_spaces[
        x__u32
        + (y__u32 * WIDTH_OF__LOCAL_SPACE_MANAGER)
        + (z__u32 * WIDTH_OF__LOCAL_SPACE_MANAGER
            * HEIGHT_OF__LOCAL_SPACE_MANAGER)];
}

void initialize_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Global_Space_Vector__3i32 center_of__local_space_manager__3i32) {
    memset(p_local_space_manager,
            0,
            sizeof(Local_Space_Manager));

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
    for (i32 _z__i32 = 0;
            _z__i32 < DEPTH_OF__LOCAL_SPACE_MANAGER;
            _z__i32++) {
#else
#define _z__i32 0
#endif
        for (i32 y__i32 = 0;
                y__i32 < HEIGHT_OF__LOCAL_SPACE_MANAGER;
                y__i32++) {
            for (i32 x__i32 = 0;
                    x__i32 < WIDTH_OF__LOCAL_SPACE_MANAGER;
                    x__i32++) {
                Local_Space *p_local_space__here =
                    get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__i32, 
                            y__i32,
                            _z__i32);

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

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
                i32 z__below =
                    (_z__i32)
                    ? _z__i32 - 1
                    : DEPTH_OF__LOCAL_SPACE_MANAGER - 1
                    ;
                i32 z__above =
                    (_z__i32 + 1 < DEPTH_OF__LOCAL_SPACE_MANAGER)
                    ? _z__i32 + 1
                    : 0
                    ;
#else
#define z__below 0
#define z__above 0
#endif

                set_neighbors_of__local_space(
                        p_local_space__here, 
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__i32, y__up, _z__i32), 
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__right, y__i32, _z__i32), 
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__i32, y__down, _z__i32), 
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__left, y__i32, _z__i32),
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__i32, y__i32, z__above),
                        get_p_local_space_by__local_xyz_from__local_space_manager(
                            p_local_space_manager, 
                            x__i32, y__i32, z__below));
                p_local_space__here->global_space__vector__3i32 =
                    get_vector__3i32(
                            x__i32
                            + center_of__local_space_manager__3i32.x__i32
                            - (WIDTH_OF__LOCAL_SPACE_MANAGER>>1) + 2, 
                            y__i32
                            + center_of__local_space_manager__3i32.y__i32
                            - (HEIGHT_OF__LOCAL_SPACE_MANAGER>>1), 
                            _z__i32
                            + center_of__local_space_manager__3i32.z__i32
                            - (DEPTH_OF__LOCAL_SPACE_MANAGER>>1));
            }
        }
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
    }
#endif

    p_local_space_manager->p_local_space__south_west =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                0, 
                0,
                0);
    p_local_space_manager->p_local_space__south_east =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER - 1, 
                0,
                0);
    p_local_space_manager->p_local_space__north_west =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                0, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1,
                0);
    p_local_space_manager->p_local_space__north_east =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER-1, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1,
                0);

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
    p_local_space_manager->p_local_space__south_west__top =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                0, 
                0,
                DEPTH_OF__LOCAL_SPACE_MANAGER-1);
    p_local_space_manager->p_local_space__south_east__top =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER - 1, 
                0,
                DEPTH_OF__LOCAL_SPACE_MANAGER-1);
    p_local_space_manager->p_local_space__north_west__top =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                0, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1,
                DEPTH_OF__LOCAL_SPACE_MANAGER-1);
    p_local_space_manager->p_local_space__north_east__top =
        get_p_local_space_by__local_xyz_from__local_space_manager(
                p_local_space_manager, 
                WIDTH_OF__LOCAL_SPACE_MANAGER-1, 
                HEIGHT_OF__LOCAL_SPACE_MANAGER-1,
                DEPTH_OF__LOCAL_SPACE_MANAGER-1);
#else
    p_local_space_manager->p_local_space__south_west__top = 0;
    p_local_space_manager->p_local_space__south_east__top = 0;
    p_local_space_manager->p_local_space__north_west__top = 0;
    p_local_space_manager->p_local_space__north_east__top = 0;
#endif
}

void drop_all__local_spaces_in__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game) {
    for (Index__u32 index_of__local_space = 0;
            index_of__local_space < VOLUME_OF__LOCAL_SPACE_MANAGER;
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
            index_of__local_space < VOLUME_OF__LOCAL_SPACE_MANAGER;
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
        if (!p_local_space->p_global_space) {
            debug_error("hold_all__unheld_local_spaces_in__local_space_manager, p_global_space == 0.");
        }
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
                center_of__local_space_manager__3i32,
                p_local_space_manager
                ->center_of__local_space_manager__3i32);

    // this boolean logic works because u32(-1) + 1 == 0.
    // and we are checking a range of -1 to 1 in each axis.
    if ((u32)distance_manhattan__3i32.x__i32 + 1 < 3
            && (u32)distance_manhattan__3i32.y__i32 + 1 < 3
            && (u32)distance_manhattan__3i32.z__i32 + 1 < 3) {
        Direction__u8 direction = DIRECTION__NONE;
        if (distance_manhattan__3i32.x__i32 < 0)
            direction |= DIRECTION__WEST;
        else if (distance_manhattan__3i32.x__i32 > 0)
            direction |= DIRECTION__EAST;

        if (distance_manhattan__3i32.y__i32 < 0)
            direction |= DIRECTION__SOUTH;
        else if (distance_manhattan__3i32.y__i32 > 0)
            direction |= DIRECTION__NORTH;

        if (distance_manhattan__3i32.z__i32 < 0)
            direction |= DIRECTION__DOWNWARDS;
        else if (distance_manhattan__3i32.z__i32 > 0)
            direction |= DIRECTION__UPWARDS;

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

void move_p_ptr_local_space__upwards(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__above;
}

void move_p_ptr_local_space__downwards(
        Local_Space **p_ptr_local_space) {
    *p_ptr_local_space =
        (*p_ptr_local_space)->p_local_space__below;
}

bool poll_local_space__traversal(
        Local_Space **p_ptr_local_space,
        Local_Space *p_local_space__end,
        Direction__u8 direction_to__traverse) {
    if (*p_ptr_local_space == p_local_space__end)
        return false;

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
        case DIRECTION__UPWARDS:
            move_p_ptr_local_space__upwards(p_ptr_local_space);
            break;
        case DIRECTION__DOWNWARDS:
            move_p_ptr_local_space__downwards(p_ptr_local_space);
            break;
    }

    return true;
}

void update_local_spaces_between__these_two_local_spaces(
        Game *p_game,
        Local_Space *p_local_space__current,
        Local_Space *p_local_space__end,
        Chunk_Vector__3i32 chunk_vector__start__3i32,
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
        p_local_space__current->global_space__vector__3i32 =
            chunk_vector__start__3i32;
        p_local_space__current->p_global_space =
            hold_global_space_within__global_space_manager(
                    p_game,
                    chunk_vector__start__3i32);
        if (!p_local_space__current->p_global_space) {
            debug_error("update_local_spaces_between__these_two_local_spaces, p_global_space == 0.");
        }
        switch (direction_to__update) {
            default:
            case DIRECTION__NORTH:
                chunk_vector__start__3i32.y__i32++;
                break;
            case DIRECTION__EAST:
                chunk_vector__start__3i32.x__i32++;
                break;
            case DIRECTION__SOUTH:
                chunk_vector__start__3i32.y__i32--;
                break;
            case DIRECTION__WEST:
                chunk_vector__start__3i32.x__i32--;
                break;
        }
    } while (poll_local_space__traversal(
                &p_local_space__current, 
                p_local_space__end,
                direction_to__update));
}

void move_local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Game *p_game,
        Direction__u8 direction__u8) {
    Local_Space *p_local_space__current = 0;
    Local_Space *p_local_space__end = 0;
    Chunk_Vector__3i32 chunk_vector__start__3i32;

    if (direction__u8 & DIRECTION__NORTH) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .y__i32++;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__north_west
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.y__i32++;

        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_west);

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__north(
                &p_local_space_manager->p_local_space__south_west__top);
#endif

        p_local_space__current
            = p_local_space_manager->p_local_space__north_west;
        p_local_space__end
            = p_local_space_manager->p_local_space__north_east;

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        do {
#endif
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__EAST);
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
            move_p_ptr_local_space__upwards(&p_local_space__end);
        } while(poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__north_west__top, 
                    DIRECTION__UPWARDS));
#endif
    }
    else if (direction__u8 & DIRECTION__SOUTH) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .y__i32--;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.y__i32--;

        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_west);

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__south(
                &p_local_space_manager->p_local_space__south_west__top);
#endif

        p_local_space__current
            = p_local_space_manager->p_local_space__south_west;
        p_local_space__end
            = p_local_space_manager->p_local_space__south_east;

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        do {
#endif
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__EAST);
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
            move_p_ptr_local_space__upwards(&p_local_space__end);
        } while(poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__south_west__top, 
                    DIRECTION__UPWARDS));
#endif
    }
    if (direction__u8 & DIRECTION__EAST) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .x__i32++;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__north_east
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.x__i32++;

        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_west);

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__east(
                &p_local_space_manager->p_local_space__south_west__top);
#endif

        p_local_space__current
            = p_local_space_manager->p_local_space__north_east;
        p_local_space__end
            = p_local_space_manager->p_local_space__south_east;

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        do {
#endif
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__SOUTH);
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
            move_p_ptr_local_space__upwards(&p_local_space__end);
        } while(poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__north_east__top, 
                    DIRECTION__UPWARDS));
#endif
    } else if (direction__u8 & DIRECTION__WEST) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .x__i32--;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__north_west
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.x__i32--;

        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_west);
        
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__west(
                &p_local_space_manager->p_local_space__south_west__top);
#endif

        p_local_space__current
            = p_local_space_manager->p_local_space__north_west;
        p_local_space__end
            = p_local_space_manager->p_local_space__south_west;

#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
        do {
#endif
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__SOUTH);
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
            move_p_ptr_local_space__upwards(&p_local_space__end);
        } while(poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__north_west__top, 
                    DIRECTION__UPWARDS));
#endif
    }
#if DEPTH_OF__LOCAL_SPACE_MANAGER > 1
    if (direction__u8 & DIRECTION__UPWARDS) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .z__i32++;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__north_west
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.z__i32++;

        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__south_west);

        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__upwards(
                &p_local_space_manager->p_local_space__south_west__top);

        p_local_space__current
            = p_local_space_manager->p_local_space__north_west__top;
        p_local_space__end
            = p_local_space_manager->p_local_space__south_west__top;

        do {
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__SOUTH);
            move_p_ptr_local_space__east(&p_local_space__end);
        } while (poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__north_east__top, 
                    DIRECTION__EAST));
    } else if (direction__u8 & DIRECTION__DOWNWARDS) {
        p_local_space_manager->center_of__local_space_manager__3i32
            .z__i32++;

        chunk_vector__start__3i32 =
            p_local_space_manager
            ->p_local_space__north_west
            ->global_space__vector__3i32
            ;
        chunk_vector__start__3i32.z__i32++;

        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__north_east);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__north_west);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__south_east);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__south_west);

        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__north_east__top);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__north_west__top);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__south_east__top);
        move_p_ptr_local_space__downwards(
                &p_local_space_manager->p_local_space__south_west__top);

        p_local_space__current
            = p_local_space_manager->p_local_space__north_west;
        p_local_space__end
            = p_local_space_manager->p_local_space__south_west;

        do {
            update_local_spaces_between__these_two_local_spaces(
                    p_game,
                    p_local_space__current,
                    p_local_space__end,
                    chunk_vector__start__3i32,
                    DIRECTION__SOUTH);
            move_p_ptr_local_space__east(&p_local_space__end);
        } while (poll_local_space__traversal(
                    &p_local_space__current, 
                    p_local_space_manager->p_local_space__north_east, 
                    DIRECTION__EAST));
    }
#endif
}

Local_Space *get_p_local_space_from__local_space_manager(
        Local_Space_Manager *p_local_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32) {
#ifndef NDEBUG
    if (chunk_vector__3i32.x__i32
            < (p_local_space_manager
                ->center_of__local_space_manager__3i32.x__i32
                - (WIDTH_OF__LOCAL_SPACE_MANAGER>>1))) {
        debug_error("get_p_local_space_by__3i32F4_from__local_space_manager, position out of bounds.");
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
#endif

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
    i32 z_delta__i32 = 
        chunk_vector__3i32.z__i32
        - p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.z__i32;

    Local_Space *p_local_space =
        p_local_space_manager->p_local_space__south_west;
    while (x_delta__i32--) {
        move_p_ptr_local_space__east(&p_local_space);
    }
    while (y_delta__i32--) {
        move_p_ptr_local_space__north(&p_local_space);
    }
    while (z_delta__i32--) {
        move_p_ptr_local_space__upwards(&p_local_space);
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
        i32 d_z__i32 = global_space_vector__center__3i32.z__i32
            - p_local_space_manager->center_of__local_space_manager__3i32.z__i32;
        Direction__u8 direction = DIRECTION__NONE;
        if (d_x__i32 < 0)
            direction |= DIRECTION__WEST;
        else if (d_x__i32 > 0)
            direction |= DIRECTION__EAST;
        if (d_y__i32 < 0)
            direction |= DIRECTION__SOUTH;
        else if (d_y__i32 > 0)
            direction |= DIRECTION__NORTH;
        if (d_z__i32 < 0)
            direction |= DIRECTION__DOWNWARDS;
        else if (d_z__i32 > 0)
            direction |= DIRECTION__UPWARDS;
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

    bool is_bounded__z = 
        global_space__3i32.z__i32
        <= p_local_space_manager
            ->p_local_space__north_east
            ->global_space__vector__3i32.z__i32;
    is_bounded__z &=
        global_space__3i32.z__i32
        >= p_local_space_manager
            ->p_local_space__south_west
            ->global_space__vector__3i32.z__i32;

    return is_bounded__x && is_bounded__y && is_bounded__z;
}
