#include <rendering/font/test_suite_rendering_font_typer.h>

#include <rendering/font/typer.c>

TEST_FUNCTION(typer__initialize__sets_cursor_position) {
    Typer typer;
    memset(&typer, 0xFF, sizeof(typer));
    initialize_typer(&typer, 10, 20, 100, 50, 8, 0, 0);
    munit_assert_int32(typer.cursor_position__3i32.x__i32, ==, 0);
    munit_assert_int32(typer.cursor_position__3i32.y__i32, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__initialize__sets_line_spacing) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 12, 0, 0);
    munit_assert_uint16(
        typer.quantity_of__space_in__pixels_between__lines, ==, 12);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__initialize_with_font__sets_font) {
    Typer typer;
    Font font;
    initialize_font(&font);
    initialize_typer_with__font(&typer, 0, 0, 100, 50, 8, 0, 0, &font);
    munit_assert_ptr_equal(typer.p_font, &font);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__initialize__without_font_does_not_set_font) {
    Typer typer;
    memset(&typer, 0, sizeof(typer));
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    // initialize_typer does NOT set the font per spec
    // p_font should remain whatever it was (zeroed from memset)
    munit_assert_ptr_null(typer.p_font);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__set_cursor__sets_position) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    Vector__3i32 pos = { .x__i32 = 15, .y__i32 = 25, .z__i32 = 0 };
    set_typer__cursor(&typer, pos);
    munit_assert_int32(typer.cursor_position__3i32.x__i32, ==, 15);
    munit_assert_int32(typer.cursor_position__3i32.y__i32, ==, 25);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__reset_cursor__resets_to_zero) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 5, 10);
    Vector__3i32 pos = { .x__i32 = 50, .y__i32 = 30, .z__i32 = 0 };
    set_typer__cursor(&typer, pos);
    reset_typer_cursor(&typer);
    munit_assert_int32(typer.cursor_position__3i32.x__i32, ==, 0);
    munit_assert_int32(typer.cursor_position__3i32.y__i32, ==, 0);
    munit_assert_int32(typer.cursor_position__3i32.z__i32, ==, 0);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__set_texture_target__sets_texture_mode) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    Texture texture;
    texture.p_PLATFORM_texture = 0;
    texture.texture_flags = 0;
    set_PLATFORM_texture_target_for__typer(&typer, texture);
    munit_assert_true(is_typer_targetting__PLATFORM_texture(&typer));
    munit_assert_false(is_typer_targetting__PLATFORM_graphics_window(&typer));
    return MUNIT_OK;
}

TEST_FUNCTION(typer__set_graphics_window_target__sets_window_mode) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    PLATFORM_Graphics_Window gfx_window;
    memset(&gfx_window, 0, sizeof(gfx_window));
    set_PLATFORM_graphics_window_target_for__typer(&typer, &gfx_window);
    munit_assert_true(is_typer_targetting__PLATFORM_graphics_window(&typer));
    munit_assert_false(is_typer_targetting__PLATFORM_texture(&typer));
    return MUNIT_OK;
}

TEST_FUNCTION(typer__offset_by_font_letter__advances_cursor_x) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    Font_Letter letter;
    memset(&letter, 0, sizeof(letter));
    letter.width_of__font_letter = 5;
    offset_typer_by__font_letter(&typer, &letter);
    munit_assert_int32(typer.cursor_position__3i32.x__i32, ==, 5);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__offset_by_font_letter__accumulates) {
    Typer typer;
    initialize_typer(&typer, 0, 0, 100, 50, 8, 0, 0);
    Font_Letter letter;
    memset(&letter, 0, sizeof(letter));
    letter.width_of__font_letter = 4;
    offset_typer_by__font_letter(&typer, &letter);
    offset_typer_by__font_letter(&typer, &letter);
    offset_typer_by__font_letter(&typer, &letter);
    munit_assert_int32(typer.cursor_position__3i32.x__i32, ==, 12);
    return MUNIT_OK;
}

TEST_FUNCTION(typer__get_p_font_letter__returns_correct_entry) {
    Typer typer;
    Font font;
    initialize_font(&font);
    initialize_typer_with__font(&typer, 0, 0, 100, 50, 8, 0, 0, &font);

    Font_Letter *p_letter = get_p_font_letter_from__typer(&typer, 'X');
    munit_assert_ptr_not_null(p_letter);
    munit_assert_ptr_equal(p_letter, &font.font_lookup_table['X']);
    return MUNIT_OK;
}

DEFINE_SUITE(typer,
    INCLUDE_TEST__STATELESS(typer__initialize__sets_cursor_position),
    INCLUDE_TEST__STATELESS(typer__initialize__sets_line_spacing),
    INCLUDE_TEST__STATELESS(typer__initialize_with_font__sets_font),
    INCLUDE_TEST__STATELESS(typer__initialize__without_font_does_not_set_font),
    INCLUDE_TEST__STATELESS(typer__set_cursor__sets_position),
    INCLUDE_TEST__STATELESS(typer__reset_cursor__resets_to_zero),
    INCLUDE_TEST__STATELESS(typer__set_texture_target__sets_texture_mode),
    INCLUDE_TEST__STATELESS(typer__set_graphics_window_target__sets_window_mode),
    INCLUDE_TEST__STATELESS(typer__offset_by_font_letter__advances_cursor_x),
    INCLUDE_TEST__STATELESS(typer__offset_by_font_letter__accumulates),
    INCLUDE_TEST__STATELESS(typer__get_p_font_letter__returns_correct_entry),
    END_TESTS)
