#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "process/process_manager.h"
#include "process/test_util__process_manager.h"
#include "random.h"
#include "test_util.h"
#include "test_util__vectors.h"
#include "vectors.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "world/world.h"
#include <world/test_suite_world_global_space_manager.h>

#include <world/global_space_manager.c>

TEST_FUNCTION(initialize_global_space_manager) {
    Global_Space_Manager global_space_manager;
    initialize_global_space_manager(
            &global_space_manager);

    Quantity__u32 quantity_of__test_steps =
        munit_rand_int_range(0, 1000);
    for (Index__u32 index_of__test_step = 0;
            index_of__test_step < quantity_of__test_steps;
            index_of__test_step++) {
        Global_Space *p_global_space =
            get_p_global_space_from__global_space_manager(
                    &global_space_manager, 
                    get_vector__3i32(
                        munit_rand_int_range(-1000, 1000), 
                        munit_rand_int_range(-1000, 1000), 
                        munit_rand_int_range(-1000, 1000)
                        ));
        munit_assert(!p_global_space);
    }

	return MUNIT_OK;
}

TEST_FUNCTION(allocate_global_space_in__global_space_manager) {
    Global_Space_Manager global_space_manager;
    initialize_global_space_manager(
            &global_space_manager);

    Global_Space *p_global_space =
        allocate_global_space_in__global_space_manager(
                &global_space_manager, 
                VECTOR__3i32__0_0_0);

    munit_assert(p_global_space != 0);

    Vector__3i32 vector_buffer__3i32[QUANTITY_OF__GLOBAL_SPACE + 1];
    test_util__initialize_buffer_of__vector__3i32(
            vector_buffer__3i32, 
            QUANTITY_OF__GLOBAL_SPACE + 1);
    vector_buffer__3i32[0] = VECTOR__3i32__0_0_0;

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE - 1;
            index_of__test_step++) {
        p_global_space = 
            allocate_global_space_in__global_space_manager(
                    &global_space_manager, 
                    test_util__insert_unique_vector__3i32(
                        vector_buffer__3i32, 
                        QUANTITY_OF__GLOBAL_SPACE + 1, 
                        -1000, 1000));
        munit_assert(p_global_space != 0);
    }

    p_global_space = 
        allocate_global_space_in__global_space_manager(
                &global_space_manager, 
                test_util__get_unique_vector__3i32(
                    vector_buffer__3i32, 
                    QUANTITY_OF__GLOBAL_SPACE + 1, 
                    -1000, 1000));

    munit_assert(p_global_space == 0);

	return MUNIT_OK;
}

TEST_FUNCTION(release_global_space_in__global_space_manager) {
    Global_Space_Manager global_space_manager;
    initialize_global_space_manager(
            &global_space_manager);

    Vector__3i32 vector_buffer__3i32[QUANTITY_OF__GLOBAL_SPACE];
    test_util__initialize_buffer_of__vector__3i32(
            vector_buffer__3i32, 
            QUANTITY_OF__GLOBAL_SPACE);
    vector_buffer__3i32[0] = VECTOR__3i32__0_0_0;

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE;
            index_of__test_step++) {
        allocate_global_space_in__global_space_manager(
                &global_space_manager, 
                test_util__insert_unique_vector__3i32(
                    vector_buffer__3i32, 
                    QUANTITY_OF__GLOBAL_SPACE, 
                    -1000, 1000));
    }

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE;
            index_of__test_step++) {
        Global_Space *p_global_space =
            get_p_global_space_from__global_space_manager(
                    &global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));
        release_global_space_in__global_space_manager(
                &global_space_manager, 
                p_global_space);
        p_global_space =
            get_p_global_space_from__global_space_manager(
                    &global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));
        munit_assert(p_global_space == 0);
    }

	return MUNIT_OK;
}

TEST_FUNCTION(get_p_global_space_from__global_space_manager) {
    Global_Space_Manager global_space_manager;
    initialize_global_space_manager(
            &global_space_manager);

    Vector__3i32 vector_buffer__3i32[QUANTITY_OF__GLOBAL_SPACE];
    test_util__initialize_buffer_of__vector__3i32(
            vector_buffer__3i32, 
            QUANTITY_OF__GLOBAL_SPACE);

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE;
            index_of__test_step++) {
        Global_Space *p_global_space__expected =
            allocate_global_space_in__global_space_manager(
                    &global_space_manager, 
                    test_util__insert_unique_vector__3i32(
                        vector_buffer__3i32, 
                        QUANTITY_OF__GLOBAL_SPACE, 
                        -1000, 1000));
        Global_Space *p_global_space__actual =
            get_p_global_space_from__global_space_manager(
                    &global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));
        munit_assert(p_global_space__actual == p_global_space__expected);
    }
	return MUNIT_OK;
}

TEST_FUNCTION(hold_global_space_within__global_space_manager) {
    Game game;
    initialize_game(&game);
    initialize_world(
            &game, 
            get_p_world_from__game(&game), 
            0);
    allocate_client_pool_for__game(
            &game, 
            1);
    allocate_client_from__game(
            &game, 
            0);

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(&game));

    Vector__3i32 vector_buffer__3i32[QUANTITY_OF__GLOBAL_SPACE];
    test_util__initialize_buffer_of__vector__3i32(
            vector_buffer__3i32, 
            QUANTITY_OF__GLOBAL_SPACE);

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE;
            index_of__test_step++) {
        Global_Space *p_global_space__expected =
            hold_global_space_within__global_space_manager(
                    &game,
                    test_util__insert_unique_vector__3i32(
                        vector_buffer__3i32, 
                        QUANTITY_OF__GLOBAL_SPACE, 
                        -1000, 1000));

        munit_assert(p_global_space__expected != 0);

        Global_Space *p_global_space__actual =
            get_p_global_space_from__global_space_manager(
                    p_global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));

        munit_assert(p_global_space__actual == p_global_space__expected);

        Global_Space *p_global_space__actual_2 =
            hold_global_space_within__global_space_manager(
                    &game,
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));

        munit_assert(p_global_space__expected == p_global_space__actual_2);
    }

	return MUNIT_OK;
}

TEST_FUNCTION(drop_global_space_within__global_space_manager) {
    Game game;
    initialize_game(&game);
    initialize_world(
            &game, 
            get_p_world_from__game(&game), 
            0);
    allocate_client_pool_for__game(
            &game, 
            1);
    allocate_client_from__game(
            &game, 
            0);

    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__world(
                get_p_world_from__game(&game));

    Vector__3i32 vector_buffer__3i32[QUANTITY_OF__GLOBAL_SPACE];
    test_util__initialize_buffer_of__vector__3i32(
            vector_buffer__3i32, 
            QUANTITY_OF__GLOBAL_SPACE);

    for (Index__u32 index_of__test_step = 0;
            index_of__test_step
            < QUANTITY_OF__GLOBAL_SPACE;
            index_of__test_step++) {
        Global_Space *p_global_space__expected =
            hold_global_space_within__global_space_manager(
                    &game,
                    test_util__insert_unique_vector__3i32(
                        vector_buffer__3i32, 
                        QUANTITY_OF__GLOBAL_SPACE, 
                        -1000, 1000));
        hold_global_space_within__global_space_manager(
                &game,
                test_util__get_vector__3i32_from__vector_buffer(
                    vector_buffer__3i32, 
                    index_of__test_step, 
                    QUANTITY_OF__GLOBAL_SPACE));

        drop_global_space_within__global_space_manager(
                &game, 
                test_util__get_vector__3i32_from__vector_buffer(
                    vector_buffer__3i32, 
                    index_of__test_step, 
                    QUANTITY_OF__GLOBAL_SPACE));

        Global_Space *p_global_space__actual =
            get_p_global_space_from__global_space_manager(
                    p_global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));

        munit_assert(p_global_space__expected == p_global_space__actual);

        drop_global_space_within__global_space_manager(
                &game, 
                test_util__get_vector__3i32_from__vector_buffer(
                    vector_buffer__3i32, 
                    index_of__test_step, 
                    QUANTITY_OF__GLOBAL_SPACE));

        p_global_space__actual =
            get_p_global_space_from__global_space_manager(
                    p_global_space_manager, 
                    test_util__get_vector__3i32_from__vector_buffer(
                        vector_buffer__3i32, 
                        index_of__test_step, 
                        QUANTITY_OF__GLOBAL_SPACE));
        
        munit_assert(
                p_global_space__actual 
                && is_global_space__deconstructing(
                    p_global_space__actual));
    }

	return MUNIT_OK;
}

DEFINE_SUITE(
        global_space_manager, 
        INCLUDE_TEST__STATELESS(initialize_global_space_manager),
        INCLUDE_TEST__STATELESS(
            allocate_global_space_in__global_space_manager),
        INCLUDE_TEST__STATELESS(
            release_global_space_in__global_space_manager),
        INCLUDE_TEST__STATELESS(
            get_p_global_space_from__global_space_manager),
        INCLUDE_TEST__STATELESS(
            hold_global_space_within__global_space_manager),
        INCLUDE_TEST__STATELESS(
            drop_global_space_within__global_space_manager),
        END_TESTS)
