#include "client.h"
#include "collisions/hitbox_aabb_manager.h"
#include "game.h"
#include "vectors.h"
#include "world/world.h"
#include <world/test_suite_world_world.h>
#include "process/process_manager.h"
#include "process/process.h"

#include <world/world.c>

TEST_FUNCTION(set_name_of__world) {
    Game game;
    World world;
    initialize_world(&game, &world);

    set_name_of__world(&world, "WORLD");
    munit_assert(strncmp(
                world.name,
                "WORLD",
                sizeof("WORLD")
                ) == 0);
    return MUNIT_OK;
}

TEST_FUNCTION(load_world) {
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
    return MUNIT_OK;    
}

TEST_FUNCTION(teleport_world) {
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
            get_vector__3i32F4_using__i32(1000, 1000, 0));

    TIMEOUT = BIT(20);
    do {
        poll_process_manager(
                get_p_process_manager_from__game(&game), 
                &game);
    } while (!is_process__complete(p_process__teleport)
            && TIMEOUT--);
    if (!TIMEOUT)
        return MUNIT_FAIL;

    return MUNIT_OK;    
}

DEFINE_SUITE(world, 
        INCLUDE_TEST__STATELESS(set_name_of__world),
        INCLUDE_TEST__STATELESS(load_world),
        INCLUDE_TEST__STATELESS(teleport_world),
        END_TESTS)
