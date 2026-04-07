#include <world/test_suite_world_world.h>

#include <world/world.c>

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.7 Name Management
///
TEST_FUNCTION(world__set_name__sets_name) {
    World world;
    memset(&world, 0, sizeof(World));
    World_Name_String name = "test_world";
    set_name_of__world(&world, name);
    munit_assert_string_equal(world.name, "test_world");
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_camera__returns_camera_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Camera *p_camera = get_p_camera_from__world(&world);
    munit_assert_ptr_equal(p_camera, &world.camera);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_inventory_manager__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Inventory_Manager *p_inv = get_p_inventory_manager_from__world(&world);
    munit_assert_ptr_equal(p_inv, &world.inventory_manager);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_item_manager__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Item_Manager *p_item = get_p_item_manager_from__world(&world);
    munit_assert_ptr_equal(p_item, &world.item_manager);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_tile_logic_table__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Tile_Logic_Table *p_tlt = get_p_tile_logic_table_from__world(&world);
    munit_assert_ptr_equal(p_tlt, &world.tile_logic_table);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_chunk_generation_table__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Chunk_Generator_Table *p_cgt = get_p_chunk_generation_table_from__world(&world);
    munit_assert_ptr_equal(p_cgt, &world.chunk_generator_table);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_global_space_manager__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Global_Space_Manager *p_gsm = get_p_global_space_manager_from__world(&world);
    munit_assert_ptr_equal(p_gsm, &world.global_space_manager);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_collision_node_pool__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Collision_Node_Pool *p_cnp = get_p_collision_node_pool_from__world(&world);
    munit_assert_ptr_equal(p_cnp, &world.collision_node_pool);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.8 Sub-Component Accessors (static inline)
///
TEST_FUNCTION(world__get_p_chunk_pool__returns_address) {
    World world;
    memset(&world, 0, sizeof(World));
    Chunk_Pool *p_cp = get_p_chunk_pool_from__world(&world);
    munit_assert_ptr_equal(p_cp, &world.chunk_pool);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/world.h.spec.md
/// Section: 1.4.9 Handler Setters (static inline)
///          1.4.10 Spawn Point and Render Kernel (static inline)
///
TEST_FUNCTION(world__set_spawn_point__and_get) {
    World world;
    memset(&world, 0, sizeof(World));
    Vector__3i32F4 spawn;
    spawn.x__i32F4 = 100;
    spawn.y__i32F4 = 200;
    spawn.z__i32F4 = 0;
    set_spawn_point_of__world(&world, spawn);
    Vector__3i32F4 result = get_spawn_point_of__world(&world);
    munit_assert_int32(result.x__i32F4, ==, 100);
    munit_assert_int32(result.y__i32F4, ==, 200);
    munit_assert_int32(result.z__i32F4, ==, 0);
    return MUNIT_OK;
}

DEFINE_SUITE(world,
    INCLUDE_TEST__STATELESS(world__set_name__sets_name),
    INCLUDE_TEST__STATELESS(world__get_p_camera__returns_camera_address),
    INCLUDE_TEST__STATELESS(world__get_p_inventory_manager__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_item_manager__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_tile_logic_table__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_chunk_generation_table__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_global_space_manager__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_collision_node_pool__returns_address),
    INCLUDE_TEST__STATELESS(world__get_p_chunk_pool__returns_address),
    INCLUDE_TEST__STATELESS(world__set_spawn_point__and_get),
    END_TESTS)
