#include <ui/test_suite_ui_ui_slider.h>

#include <ui/ui_slider.c>

TEST_FUNCTION(initialize_ui_element_as__slider__sets_kind) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    munit_assert_int(
            ui_element.the_kind_of_ui_element__this_is,
            ==,
            UI_Element_Kind__Slider);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__x_axis_sets_snapped_flag) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    munit_assert_true(is_ui_element__snapped_x_or_y_axis(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__y_axis_clears_snapped_flag) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 0;
    span.y__i32 = 100;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            false);
    munit_assert_false(is_ui_element__snapped_x_or_y_axis(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__sets_spanning_length) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 200;
    span.y__i32 = 50;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    Vector__3i32 result = get_ui_slider__spanning_length(&ui_element);
    munit_assert_int32(result.x__i32, ==, 200);
    munit_assert_int32(result.y__i32, ==, 50);
    return MUNIT_OK;
}

TEST_FUNCTION(set_ui_slider_at__this_distance_u32__sets_distance) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    set_ui_slider_at__this_distance_u32(&ui_element, 42);
    munit_assert_uint32(ui_element.slider__distance__u32, ==, 42);
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__sets_dragged_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    munit_assert_true(does_ui_element_have__dragged_handler(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__sets_transformed_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    munit_assert_true(
            does_ui_element_have__transformed_handler(&ui_element));
    return MUNIT_OK;
}

TEST_FUNCTION(initialize_ui_element_as__slider__sets_dispose_handler) {
    UI_Element ui_element;
    memset(&ui_element, 0, sizeof(ui_element));
    Vector__3i32 span;
    span.x__i32 = 100;
    span.y__i32 = 0;
    span.z__i32 = 0;
    initialize_ui_element_as__slider(
            &ui_element,
            span,
            0,
            true);
    munit_assert_true(does_ui_element_have__dispose_handler(&ui_element));
    return MUNIT_OK;
}

DEFINE_SUITE(ui_slider,
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__sets_kind),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__x_axis_sets_snapped_flag),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__y_axis_clears_snapped_flag),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__sets_spanning_length),
    INCLUDE_TEST__STATELESS(set_ui_slider_at__this_distance_u32__sets_distance),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__sets_dragged_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__sets_transformed_handler),
    INCLUDE_TEST__STATELESS(initialize_ui_element_as__slider__sets_dispose_handler),
    END_TESTS)
