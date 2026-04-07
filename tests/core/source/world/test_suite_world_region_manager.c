#include <world/test_suite_world_region_manager.h>

#include <world/region_manager.c>

/**
 * @spec    core/world/region_manager.h.spec.md
 * @section 1.4 Functions — initialize_region_manager
 * @section 1.3.1 Region_Manager (struct) — center_of__region_manager
 *
 * Verifies that initialize_region_manager zeroes the center coordinate
 * of the region manager.
 */
TEST_FUNCTION(region_manager__initialize__succeeds) {
    Region_Manager manager;
    initialize_region_manager(&manager);
    munit_assert_int32(manager.center_of__region_manager.x__i32, ==, 0);
    munit_assert_int32(manager.center_of__region_manager.y__i32, ==, 0);
    munit_assert_int32(manager.center_of__region_manager.z__i32, ==, 0);
    return MUNIT_OK;
}

DEFINE_SUITE(region_manager,
    INCLUDE_TEST__STATELESS(region_manager__initialize__succeeds),
    END_TESTS)
