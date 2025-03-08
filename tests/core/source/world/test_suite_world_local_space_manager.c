#include "client.h"
#include "defines_weak.h"
#include "game.h"
#include "munit.h"
#include "platform_defines.h"
#include "vectors.h"
#include "world/local_space_manager.h"
#include "world/world.h"
#include <world/test_suite_world_local_space_manager.h>

#include <world/local_space_manager.c>

MunitResult assert_local_space_manager__integrity(
        Local_Space_Manager *p_local_space_manager) {
    Local_Space *p_local_space =
        get_p_local_space_by__index_from__local_space_manager(
                p_local_space_manager,
                munit_rand_uint32()
                % (sizeof(p_local_space_manager->local_spaces)
                        / sizeof(Local_Space))
                );

    Local_Space *p_local_space__current =
        p_local_space;
    for (Index__u32 index_of__step = 0;
            index_of__step < WIDTH_OF__LOCAL_SPACE_MANAGER;
            index_of__step++) {
        move_p_ptr_local_space__east(&p_local_space__current);
    }

    munit_assert(p_local_space == p_local_space__current);

    for (Index__u32 index_of__step = 0;
            index_of__step < WIDTH_OF__LOCAL_SPACE_MANAGER;
            index_of__step++) {
        move_p_ptr_local_space__west(&p_local_space__current);
    }

    munit_assert(p_local_space == p_local_space__current);

    for (Index__u32 index_of__step = 0;
            index_of__step < WIDTH_OF__LOCAL_SPACE_MANAGER;
            index_of__step++) {
        move_p_ptr_local_space__north(&p_local_space__current);
    }

    munit_assert(p_local_space == p_local_space__current);

    for (Index__u32 index_of__step = 0;
            index_of__step < WIDTH_OF__LOCAL_SPACE_MANAGER;
            index_of__step++) {
        move_p_ptr_local_space__south(&p_local_space__current);
    }

    munit_assert(p_local_space == p_local_space__current);

    return MUNIT_OK;
}

TEST_FUNCTION(initialize_local_space_manager) {
    Local_Space_Manager local_space_manager;
    initialize_local_space_manager(
            &local_space_manager, 
            VECTOR__3i32__0_0_0);

    return assert_local_space_manager__integrity(
            &local_space_manager);
}

TEST_FUNCTION(set_center_of__local_space_manager) {
    Game game;
    initialize_game(&game);
    initialize_world(
            &game, 
            get_p_world_from__game(&game), 
            0);

    allocate_client_pool_for__game(
            &game, 
            1);
    Client *p_client =
        allocate_client_from__game(
                &game, 
                0);

    Local_Space_Manager *p_local_space_manager =
        get_p_local_space_manager_from__client(p_client);
    initialize_local_space_manager(
            p_local_space_manager, 
            VECTOR__3i32__0_0_0);

    set_center_of__local_space_manager(
            p_local_space_manager, 
            &game, 
            VECTOR__3i32__0_0_0);

    munit_assert(
            is_vectors_3i32__equal(
                p_local_space_manager
                    ->center_of__local_space_manager__3i32,
                VECTOR__3i32__0_0_0));

    MunitResult munit_result =
        assert_local_space_manager__integrity(
                p_local_space_manager);
    if (munit_result != MUNIT_OK) {
        return munit_result;
    }

    set_center_of__local_space_manager(
            p_local_space_manager, 
            &game, 
            get_vector__3i32(1, 0, 0));

    munit_assert(
            is_vectors_3i32__equal(
                p_local_space_manager
                    ->center_of__local_space_manager__3i32,
                get_vector__3i32(1, 0, 0)));

    munit_result =
        assert_local_space_manager__integrity(
                p_local_space_manager);
    if (munit_result != MUNIT_OK) {
        return munit_result;
    }

    for (Index__u32 index_of__test = 0;
            index_of__test < 32;
            index_of__test++) {
        Vector__3i32 vec_3i32 =
            get_vector__3i32(
                munit_rand_int_range(-1000, 1000), 
                munit_rand_int_range(-1000, 1000), 
                0);

        set_center_of__local_space_manager(
                p_local_space_manager, 
                &game, 
                vec_3i32);

        munit_assert(
                is_vectors_3i32__equal(
                    p_local_space_manager
                        ->center_of__local_space_manager__3i32,
                    vec_3i32));

        munit_result =
            assert_local_space_manager__integrity(
                    p_local_space_manager);
        if (munit_result != MUNIT_OK) {
            return munit_result;
        }
    }

    return MUNIT_OK;
}

TEST_FUNCTION(move_local_space_manager) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(get_p_local_space_by__3i32F4_from__local_space_manager) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(get_p_tile_by__3i32F4_from__local_space_manager) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(poll_local_space_for__scrolling) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(is_vector_3i32F4_within__local_space_manager) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(load_local_space_manager_at__global_space_vector__3i32) {

    return MUNIT_SKIP;
}

TEST_FUNCTION(get_center_of__local_space_manager) {

    return MUNIT_SKIP;
}

DEFINE_SUITE(
        local_space_manager, 
        INCLUDE_TEST__STATELESS
            (initialize_local_space_manager),
		INCLUDE_TEST__STATELESS(set_center_of__local_space_manager),
		INCLUDE_TEST__STATELESS(move_local_space_manager),
		INCLUDE_TEST__STATELESS(
            get_p_local_space_by__3i32F4_from__local_space_manager),
		INCLUDE_TEST__STATELESS(
            get_p_tile_by__3i32F4_from__local_space_manager),
		INCLUDE_TEST__STATELESS(poll_local_space_for__scrolling),
		INCLUDE_TEST__STATELESS(
            is_vector_3i32F4_within__local_space_manager),
		INCLUDE_TEST__STATELESS(
            load_local_space_manager_at__global_space_vector__3i32),
		INCLUDE_TEST__STATELESS(get_center_of__local_space_manager),
        END_TESTS)
