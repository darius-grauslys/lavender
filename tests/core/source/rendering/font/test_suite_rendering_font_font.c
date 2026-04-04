#include <rendering/font/test_suite_rendering_font_font.h>

#include <rendering/font/font.c>

TEST_FUNCTION(font__initialize__clears_state) {
    Font font;
    memset(&font, 0xFF, sizeof(font));
    initialize_font(&font);
    munit_assert_false(is_font__allocated(&font));
    return MUNIT_OK;
}

TEST_FUNCTION(font__is_font__allocated__returns_false_after_init) {
    Font font;
    initialize_font(&font);
    munit_assert_false(is_font__allocated(&font));
    return MUNIT_OK;
}

TEST_FUNCTION(font__set_font_as__allocated__sets_flag) {
    Font font;
    initialize_font(&font);
    set_font_as__allocated(&font);
    munit_assert_true(is_font__allocated(&font));
    return MUNIT_OK;
}

TEST_FUNCTION(font__set_font_as__deallocated__clears_flag) {
    Font font;
    initialize_font(&font);
    set_font_as__allocated(&font);
    munit_assert_true(is_font__allocated(&font));
    set_font_as__deallocated(&font);
    munit_assert_false(is_font__allocated(&font));
    return MUNIT_OK;
}

TEST_FUNCTION(font__get_p_font_letter__returns_correct_entry) {
    Font font;
    initialize_font(&font);
    Font_Letter *p_letter_A = get_p_font_letter_from__font(&font, 'A');
    munit_assert_ptr_not_null(p_letter_A);
    munit_assert_ptr_equal(p_letter_A, &font.font_lookup_table['A']);
    return MUNIT_OK;
}

TEST_FUNCTION(font__get_p_font_letter__different_chars_return_different_entries) {
    Font font;
    initialize_font(&font);
    Font_Letter *p_letter_A = get_p_font_letter_from__font(&font, 'A');
    Font_Letter *p_letter_B = get_p_font_letter_from__font(&font, 'B');
    munit_assert_ptr_not_equal(p_letter_A, p_letter_B);
    return MUNIT_OK;
}

TEST_FUNCTION(font__initialize_font_letter__sets_fields) {
    Font_Letter letter;
    memset(&letter, 0, sizeof(letter));
    initialize_font__letter(&letter, 4, 6, 1, 2, 42);
    munit_assert_uint8(letter.width_of__font_letter, ==, 4);
    munit_assert_uint8(letter.height_of__font_letter, ==, 6);
    munit_assert_uint8(letter.x__offset_of__font_letter, ==, 1);
    munit_assert_uint8(letter.y__offset_of__font_letter, ==, 2);
    munit_assert_uint16(letter.index_of__character__in_font, ==, 42);
    return MUNIT_OK;
}

TEST_FUNCTION(font__initialize__lookup_table_zeroed) {
    Font font;
    initialize_font(&font);
    for (int i = 0; i < FONT_LETTER_MAX_QUANTITY_OF; i++) {
        munit_assert_uint8(font.font_lookup_table[i].width_of__font_letter, ==, 0);
        munit_assert_uint8(font.font_lookup_table[i].height_of__font_letter, ==, 0);
    }
    return MUNIT_OK;
}

DEFINE_SUITE(font,
    INCLUDE_TEST__STATELESS(font__initialize__clears_state),
    INCLUDE_TEST__STATELESS(font__is_font__allocated__returns_false_after_init),
    INCLUDE_TEST__STATELESS(font__set_font_as__allocated__sets_flag),
    INCLUDE_TEST__STATELESS(font__set_font_as__deallocated__clears_flag),
    INCLUDE_TEST__STATELESS(font__get_p_font_letter__returns_correct_entry),
    INCLUDE_TEST__STATELESS(font__get_p_font_letter__different_chars_return_different_entries),
    INCLUDE_TEST__STATELESS(font__initialize_font_letter__sets_fields),
    INCLUDE_TEST__STATELESS(font__initialize__lookup_table_zeroed),
    END_TESTS)
