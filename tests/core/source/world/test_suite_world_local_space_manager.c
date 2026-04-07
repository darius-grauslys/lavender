#include <world/test_suite_world_local_space_manager.h>

#include <world/local_space_manager.c>

/**
 * Spec:    docs/specs/core/world/local_space_manager.h.spec.md
 * Section: 1.4.1 Initialization
 *          1.4.5 Convenience (static inline)
 */
TEST_FUNCTION(local_space_manager__initialize__sets_center) {
    Local_Space_Manager manager;
    Global_Space_Vector__3i32 center;
    center.x__i32 = 5;
    center.y__i32 = 10;
    center.z__i32 = 0;
    initialize_local_space_manager(&manager, center);
    Chunk_Vector__3i32 result = get_center_of__local_space_manager(&manager);
    munit_assert_int32(result.x__i32, ==, 5);
    munit_assert_int32(result.y__i32, ==, 10);
    munit_assert_int32(result.z__i32, ==, 0);
    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/world/local_space_manager.h.spec.md
 * Section: 1.4.3 Lookup
 */
TEST_FUNCTION(local_space_manager__get_by_index__valid_index) {
    Local_Space_Manager manager;
    Global_Space_Vector__3i32 center;
    center.x__i32 = 0;
    center.y__i32 = 0;
    center.z__i32 = 0;
    initialize_local_space_manager(&manager, center);
    Local_Space *p_ls = get_p_local_space_by__index_from__local_space_manager(&manager, 0);
    munit_assert_ptr_not_null(p_ls);
    munit_assert_ptr_equal(p_ls, &manager.local_spaces[0]);
    return MUNIT_OK;
}

/**
 * Spec:    docs/specs/core/world/local_space_manager.h.spec.md
 * Section: 1.4.3 Lookup
 */
TEST_FUNCTION(local_space_manager__get_by_index__last_valid_index) {
    Local_Space_Manager manager;
    Global_Space_Vector__3i32 center;
    center.x__i32 = 0;
    center.y__i32 = 0;
    center.z__i32 = 0;
    initialize_local_space_manager(&manager, center);
    Local_Space *p_ls = get_p_local_space_by__index_from__local_space_manager(
        &manager, VOLUME_OF__LOCAL_SPACE_MANAGER - 1);
    munit_assert_ptr_not_null(p_ls);
    return MUNIT_OK;
}

DEFINE_SUITE(local_space_manager,
    INCLUDE_TEST__STATELESS(local_space_manager__initialize__sets_center),
    INCLUDE_TEST__STATELESS(local_space_manager__get_by_index__valid_index),
    INCLUDE_TEST__STATELESS(local_space_manager__get_by_index__last_valid_index),
    END_TESTS)
