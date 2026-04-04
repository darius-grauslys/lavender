#include <serialization/test_suite_serialization_game_directory.h>

#include <serialization/game_directory.c>

TEST_FUNCTION(game_directory__append_path_concatenates) {
    IO_path base;
    IO_path suffix;
    memset(base, 0, sizeof(IO_path));
    memset(suffix, 0, sizeof(IO_path));
    strncpy(base, "/home/user", sizeof(IO_path) - 1);
    strncpy(suffix, "/saves", sizeof(IO_path) - 1);
    append_path(base, suffix);
    munit_assert_string_equal(base, "/home/user/saves");
    return MUNIT_OK;
}

TEST_FUNCTION(game_directory__append_path_empty_suffix) {
    IO_path base;
    IO_path suffix;
    memset(base, 0, sizeof(IO_path));
    memset(suffix, 0, sizeof(IO_path));
    strncpy(base, "/home/user", sizeof(IO_path) - 1);
    append_path(base, suffix);
    munit_assert_string_equal(base, "/home/user");
    return MUNIT_OK;
}

TEST_FUNCTION(game_directory__append_path_empty_base) {
    IO_path base;
    IO_path suffix;
    memset(base, 0, sizeof(IO_path));
    memset(suffix, 0, sizeof(IO_path));
    strncpy(suffix, "/saves", sizeof(IO_path) - 1);
    append_path(base, suffix);
    munit_assert_string_equal(base, "/saves");
    return MUNIT_OK;
}

DEFINE_SUITE(game_directory,
    INCLUDE_TEST__STATELESS(game_directory__append_path_concatenates),
    INCLUDE_TEST__STATELESS(game_directory__append_path_empty_suffix),
    INCLUDE_TEST__STATELESS(game_directory__append_path_empty_base),
    END_TESTS)
