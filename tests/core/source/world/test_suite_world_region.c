#include <world/test_suite_world_region.h>

#include <world/region.c>

TEST_FUNCTION(region__truncate_chunk_vector__masks_correctly) {
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 0;
    cv.y__i32 = 0;
    cv.z__i32 = 0;
    truncate_p_chunk_vector_3i32_to__region(&cv);
    munit_assert_int32(cv.x__i32, ==, 0);
    munit_assert_int32(cv.y__i32, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(region__truncate_chunk_vector__large_values_masked) {
    Chunk_Vector__3i32 cv;
    cv.x__i32 = 1000;
    cv.y__i32 = 1000;
    cv.z__i32 = 0;
    Chunk_Vector__3i32 cv_original = cv;
    truncate_p_chunk_vector_3i32_to__region(&cv);
    munit_assert_int32(cv.x__i32, <=, cv_original.x__i32);
    munit_assert_int32(cv.y__i32, <=, cv_original.y__i32);
    return MUNIT_OK;
}

DEFINE_SUITE(region,
    INCLUDE_TEST__STATELESS(region__truncate_chunk_vector__masks_correctly),
    INCLUDE_TEST__STATELESS(region__truncate_chunk_vector__large_values_masked),
    END_TESTS)
