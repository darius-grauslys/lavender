#include "client.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "munit.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "vectors.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"
#include <world/test_suite_world_local_space_manager.h>

#include <world/local_space_manager.c>

typedef struct LSM_RandomStep_t {
    i8 step;
    i8 step_code;
    Local_Space *p_local_space__next;
} LSM_RandomStep;

static Local_Space *__step_local_space(
        Local_Space *p_local_space__current,
        LSM_RandomStep *p_lsm_random_step) {
    i8 step = p_lsm_random_step->step;
    switch (p_lsm_random_step->step_code) {
        default:
        case 0:
            return
                (step)
                ? p_local_space__current->p_local_space__east
                : p_local_space__current->p_local_space__west
                ;
            break;
        case 1:
            return
                (step)
                ? p_local_space__current->p_local_space__north
                : p_local_space__current->p_local_space__south
                ;
            break;
#if LOCAL_SPACE_MANAGER__DEPTH > 1
        case 2:
            return
                (step)
                ? p_local_space__current->p_local_space__above
                : p_local_space__current->p_local_space__below
                ;
            break;
#endif
    }
}

static Local_Space *__step_local_space__reversed(
        Local_Space *p_local_space__current,
        LSM_RandomStep *p_lsm_random_step) {
    i8 step = !p_lsm_random_step->step;
    switch (p_lsm_random_step->step_code) {
        default:
        case 0:
            return
                (step)
                ? p_local_space__current->p_local_space__east
                : p_local_space__current->p_local_space__west
                ;
            break;
        case 1:
            return
                (step)
                ? p_local_space__current->p_local_space__north
                : p_local_space__current->p_local_space__south
                ;
            break;
#if LOCAL_SPACE_MANAGER__DEPTH > 1
        case 2:
            return
                (step)
                ? p_local_space__current->p_local_space__above
                : p_local_space__current->p_local_space__below
                ;
            break;
#endif
    }
}

static LSM_RandomStep __get_random_step(Local_Space *p_local_space__current) {
    i8 step = munit_rand_int_range(0, 1);

    i8 step_code = munit_rand_int_range(0, 2);
    LSM_RandomStep lsm_step = (LSM_RandomStep){
        step, step_code, 0
    };
    lsm_step.p_local_space__next =
        __step_local_space(p_local_space__current, &lsm_step);
    return lsm_step;
}

static MunitResult __test_random_walk(
        Local_Space *p_local_space__begin,
        u32 step_count) {
    LSM_RandomStep steps[step_count];
    Local_Space *p_local_space__current = p_local_space__begin;
    for (u32 current_step = 0; current_step < step_count; current_step++) {
        steps[current_step] = __get_random_step(p_local_space__current);
        p_local_space__current = __step_local_space(
                p_local_space__current, 
                &steps[current_step]);
        munit_assert_ptr_not_null(p_local_space__current);
    }
    for (u32 current_step = step_count - 1; current_step > 0; current_step--) {
        p_local_space__current = __step_local_space__reversed(
                p_local_space__current, 
                &steps[current_step]);
        munit_assert_ptr_not_null(p_local_space__current);
        if (current_step) {
            munit_assert_ptr_equal(
                    p_local_space__current, 
                    steps[current_step - 1].p_local_space__next);
        } else {
            munit_assert_ptr_equal(
                    p_local_space__current, 
                    p_local_space__begin);
        }
    }
    return MUNIT_OK;
}

static MunitResult __test_walks(
        Local_Space *p_local_space,
        u32 quantity_of__walks,
        u32 quantity_of__steps) {
    for (u32 current_walk = 0; current_walk < quantity_of__walks; current_walk++) {
        MunitResult result = 
            __test_random_walk(
                p_local_space, 
                quantity_of__steps);
        munit_assert(result == MUNIT_OK);
    }
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_local_space_manager) {
    // TODO: test more rigorously
    Local_Space_Manager lsm;
    initialize_local_space_manager(
            &lsm, 
            get_vector__3i32(0, 0, 0));
    Local_Space *p_local_space =
        get_p_local_space_from__local_space_manager(
                &lsm, 
                get_vector__3i32(0, 0, 0));
    munit_assert_not_null(p_local_space);
    __test_walks(
            p_local_space, 10, 100);
    return MUNIT_OK;
}

TEST_FUNCTION(lsm_walk_post_teleport) {
    Game game;
    initialize_game(&game);
    allocate_world_for__game(&game);
    initialize_world(
            &game, 
            get_p_world_from__game(&game));
    allocate_client_pool_for__game(
            &game, 
            0, 1);
    Client *p_client =
        get_p_client_by__uuid_from__game(
                &game, 
                0);
    allocate_hitbox_aabb_from__hitbox_aabb_manager(
            get_p_hitbox_aabb_manager_from__game(&game), 
            GET_UUID_P(p_client));
    initialize_client(
            p_client, 
            0, 
            get_vector__3i32(0, 0, 0));
    Process *p_process__load_world =
        load_world(&game);
    uint32_t TIMEOUT = BIT(20);
    do {
        poll_process_manager(
                get_p_process_manager_from__game(&game), 
                &game);
    } while (!is_process__complete(p_process__load_world)
            && TIMEOUT--);
    if (!TIMEOUT)
        return MUNIT_FAIL;

    Process *p_process__teleport = teleport_client(
            &game, p_client, 
            get_vector__3i32F4_using__i32(
                1000, 
                1000, 
#if LOCAL_SPACE_MANAGER__DEPTH > 1
                1000
#else
                0
#endif
                ));

    TIMEOUT = BIT(20);
    do {
        poll_process_manager(
                get_p_process_manager_from__game(&game), 
                &game);
    } while (!is_process__complete(p_process__teleport)
            && TIMEOUT--);
    if (!TIMEOUT)
        return MUNIT_FAIL;

    Local_Space *p_local_space =
        get_p_local_space_from__local_space_manager(
                get_p_local_space_manager_from__client(p_client), 
                vector_3i32F4_to__chunk_vector_3i32(
                    get_position_3i32F4_of__hitbox_aabb(
                        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                            get_p_hitbox_aabb_manager_from__game(&game), 
                            GET_UUID_P(p_client)))));
    munit_assert_not_null(p_local_space);
    __test_walks(
            p_local_space, 20, 100);

    return MUNIT_OK;
}

DEFINE_SUITE(local_space_manager, 
        INCLUDE_TEST__STATELESS(initialize_local_space_manager),
        INCLUDE_TEST__STATELESS(lsm_walk_post_teleport),
        END_TESTS)
