#include <util/bitmap/test_suite_util_bitmap_bitmap.h>

#include <util/bitmap/bitmap.c>

TEST_FUNCTION(bitmap__initialize_all_false) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    for (Index__u32 i = 0; i < 64; i++) {
        munit_assert_false(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__initialize_all_true) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, true, 64);

    for (Index__u32 i = 0; i < 64; i++) {
        munit_assert_true(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__set_single_bit) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    set_bit_in__bitmap(test_bitmap, 64, 0, true);
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 0));

    for (Index__u32 i = 1; i < 64; i++) {
        munit_assert_false(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__clear_single_bit) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, true, 64);

    set_bit_in__bitmap(test_bitmap, 64, 5, false);
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 64, 5));

    for (Index__u32 i = 0; i < 64; i++) {
        if (i == 5) continue;
        munit_assert_true(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__set_last_bit) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    set_bit_in__bitmap(test_bitmap, 64, 63, true);
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 63));

    for (Index__u32 i = 0; i < 63; i++) {
        munit_assert_false(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__set_multiple_bits) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    set_bit_in__bitmap(test_bitmap, 64, 0, true);
    set_bit_in__bitmap(test_bitmap, 64, 7, true);
    set_bit_in__bitmap(test_bitmap, 64, 8, true);
    set_bit_in__bitmap(test_bitmap, 64, 63, true);

    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 0));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 7));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 8));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 63));

    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 64, 1));
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 64, 62));

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__set_and_clear_same_bit) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    set_bit_in__bitmap(test_bitmap, 64, 10, true);
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 64, 10));

    set_bit_in__bitmap(test_bitmap, 64, 10, false);
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 64, 10));

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__byte_boundary_bits) {
    BITMAP(test_bitmap, 32);
    initialize_bitmap(test_bitmap, false, 32);

    set_bit_in__bitmap(test_bitmap, 32, 7, true);
    set_bit_in__bitmap(test_bitmap, 32, 8, true);
    set_bit_in__bitmap(test_bitmap, 32, 15, true);
    set_bit_in__bitmap(test_bitmap, 32, 16, true);

    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 32, 7));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 32, 8));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 32, 15));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 32, 16));

    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 32, 6));
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 32, 9));

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__larger_bitmap) {
    BITMAP(test_bitmap, 256);
    initialize_bitmap(test_bitmap, false, 256);

    set_bit_in__bitmap(test_bitmap, 256, 0, true);
    set_bit_in__bitmap(test_bitmap, 256, 128, true);
    set_bit_in__bitmap(test_bitmap, 256, 255, true);

    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 256, 0));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 256, 128));
    munit_assert_true(
        is_bit_set_in__bitmap(test_bitmap, 256, 255));

    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 256, 1));
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 256, 127));
    munit_assert_false(
        is_bit_set_in__bitmap(test_bitmap, 256, 254));

    return MUNIT_OK;
}

TEST_FUNCTION(bitmap__reinitialize_clears) {
    BITMAP(test_bitmap, 64);
    initialize_bitmap(test_bitmap, false, 64);

    set_bit_in__bitmap(test_bitmap, 64, 0, true);
    set_bit_in__bitmap(test_bitmap, 64, 32, true);
    set_bit_in__bitmap(test_bitmap, 64, 63, true);

    initialize_bitmap(test_bitmap, false, 64);

    for (Index__u32 i = 0; i < 64; i++) {
        munit_assert_false(
            is_bit_set_in__bitmap(test_bitmap, 64, i));
    }

    return MUNIT_OK;
}

DEFINE_SUITE(bitmap,
    INCLUDE_TEST__STATELESS(bitmap__initialize_all_false),
    INCLUDE_TEST__STATELESS(bitmap__initialize_all_true),
    INCLUDE_TEST__STATELESS(bitmap__set_single_bit),
    INCLUDE_TEST__STATELESS(bitmap__clear_single_bit),
    INCLUDE_TEST__STATELESS(bitmap__set_last_bit),
    INCLUDE_TEST__STATELESS(bitmap__set_multiple_bits),
    INCLUDE_TEST__STATELESS(bitmap__set_and_clear_same_bit),
    INCLUDE_TEST__STATELESS(bitmap__byte_boundary_bits),
    INCLUDE_TEST__STATELESS(bitmap__larger_bitmap),
    INCLUDE_TEST__STATELESS(bitmap__reinitialize_clears),
    END_TESTS)
