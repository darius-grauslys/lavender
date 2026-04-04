#include <collisions/test_suite_collisions_collision_resolver_aabb.h>

#include <collisions/collision_resolver_aabb.c>

static int collision_handler_call_count = 0;
static int tile_touch_handler_call_count = 0;

static void test_collision_handler(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb__colliding,
        Hitbox_AABB *p_hitbox_aabb__collided) {
    (void)p_game;
    (void)p_world;
    (void)p_hitbox_aabb__colliding;
    (void)p_hitbox_aabb__collided;
    collision_handler_call_count++;
}

static void test_tile_touch_handler(
        Game *p_game,
        World *p_world,
        Hitbox_AABB *p_hitbox_aabb,
        Tile *p_tile,
        Signed_Index__i32 x__i32,
        Signed_Index__i32 y__i32) {
    (void)p_game;
    (void)p_world;
    (void)p_hitbox_aabb;
    (void)p_tile;
    (void)x__i32;
    (void)y__i32;
    tile_touch_handler_call_count++;
}

TEST_FUNCTION(collision_resolver_aabb__default_collision_handler__does_not_crash_on_non_overlapping) {
    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos_a = { 0, 0, 0 };
    Vector__3i32F4 pos_b = { 1000 << 4, 1000 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 16, 16, pos_a);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 16, 16, pos_b);

    f_hitbox_aabb_collision_handler__default(
            NULL, NULL, &hitbox_a, &hitbox_b);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__default_collision_handler__does_not_crash_on_overlapping) {
    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos_a = { 10 << 4, 10 << 4, 0 };
    Vector__3i32F4 pos_b = { 12 << 4, 12 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 16, 16, pos_a);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 16, 16, pos_b);

    f_hitbox_aabb_collision_handler__default(
            NULL, NULL, &hitbox_a, &hitbox_b);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__custom_handler__is_invoked) {
    collision_handler_call_count = 0;

    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos_a = { 10 << 4, 10 << 4, 0 };
    Vector__3i32F4 pos_b = { 12 << 4, 12 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 32, 32, pos_a);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 32, 32, pos_b);

    test_collision_handler(NULL, NULL, &hitbox_a, &hitbox_b);

    munit_assert_int(collision_handler_call_count, ==, 1);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__custom_tile_handler__is_invoked) {
    tile_touch_handler_call_count = 0;

    Hitbox_AABB hitbox;
    Vector__3i32F4 pos = { 10 << 4, 10 << 4, 0 };
    initialize_hitbox_aabb_as__allocated(
            &hitbox, 1, 16, 16, pos);

    Tile tile;
    memset(&tile, 0, sizeof(tile));

    test_tile_touch_handler(NULL, NULL, &hitbox, &tile, 10, 10);

    munit_assert_int(tile_touch_handler_call_count, ==, 1);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__is_hitbox_aabb_colliding__no_overlap) {
    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos_a = { 0, 0, 0 };
    Vector__3i32F4 pos_b = { 500 << 4, 500 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 16, 16, pos_a);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 16, 16, pos_b);

    Direction__u8 result = is_hitbox_aabb__colliding(
            &hitbox_a, &hitbox_b);

    munit_assert_uint8(result, ==, DIRECTION__NONE);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__is_hitbox_aabb_colliding__overlap) {
    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos_a = { 10 << 4, 10 << 4, 0 };
    Vector__3i32F4 pos_b = { 12 << 4, 12 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 32, 32, pos_a);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 32, 32, pos_b);

    Direction__u8 result = is_hitbox_aabb__colliding(
            &hitbox_a, &hitbox_b);

    munit_assert_uint8(result, !=, DIRECTION__NONE);

    return MUNIT_OK;
}

TEST_FUNCTION(collision_resolver_aabb__is_hitbox_aabb_colliding__same_position) {
    Hitbox_AABB hitbox_a;
    Hitbox_AABB hitbox_b;

    Vector__3i32F4 pos = { 50 << 4, 50 << 4, 0 };

    initialize_hitbox_aabb_as__allocated(
            &hitbox_a, 1, 16, 16, pos);
    initialize_hitbox_aabb_as__allocated(
            &hitbox_b, 2, 16, 16, pos);

    Direction__u8 result = is_hitbox_aabb__colliding(
            &hitbox_a, &hitbox_b);

    munit_assert_uint8(result, !=, DIRECTION__NONE);

    return MUNIT_OK;
}

DEFINE_SUITE(collision_resolver_aabb,
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__default_collision_handler__does_not_crash_on_non_overlapping),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__default_collision_handler__does_not_crash_on_overlapping),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__custom_handler__is_invoked),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__custom_tile_handler__is_invoked),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__is_hitbox_aabb_colliding__no_overlap),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__is_hitbox_aabb_colliding__overlap),
    INCLUDE_TEST__STATELESS(collision_resolver_aabb__is_hitbox_aabb_colliding__same_position),
    END_TESTS)
