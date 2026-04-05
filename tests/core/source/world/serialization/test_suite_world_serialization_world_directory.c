#include <world/serialization/test_suite_world_serialization_world_directory.h>

#include <world/serialization/world_directory.c>

TEST_FUNCTION(world_directory__append_chunk_file__tiles__succeeds_with_space) {
    char path[64];
    memset(path, 0, sizeof(path));
    strcpy(path, "/some/dir");
    Quantity__u16 length = strlen(path);
    bool result = append_chunk_file__tiles_to__path(path, length, 64);
    munit_assert_true(result);
    munit_assert_string_equal(path, "/some/dir/t");
    return MUNIT_OK;
}

TEST_FUNCTION(world_directory__append_chunk_file__tiles__fails_when_buffer_too_small) {
    char path[12];
    memset(path, 0, sizeof(path));
    strcpy(path, "/some/dir");
    Quantity__u16 length = strlen(path);
    bool result = append_chunk_file__tiles_to__path(path, length, 11);
    munit_assert_false(result);
    return MUNIT_OK;
}

DEFINE_SUITE(world_directory,
    INCLUDE_TEST__STATELESS(world_directory__append_chunk_file__tiles__succeeds_with_space),
    INCLUDE_TEST__STATELESS(world_directory__append_chunk_file__tiles__fails_when_buffer_too_small),
    END_TESTS)
