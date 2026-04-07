#include <input/test_suite_input_input.h>

#include <input/input.c>

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.1 Initialization, 1.5.10 Postconditions
///
TEST_FUNCTION(initialize_input__sets_all_flags_to_zero) {
    Input input;
    input.input_flags__pressed = 0xFFFFFFFF;
    input.input_flags__held = 0xFFFFFFFF;
    input.input_flags__released = 0xFFFFFFFF;
    input.input_flags__pressed_old = 0xFFFFFFFF;
    input.input_mode__u8 = INPUT_MODE__WRITING;

    initialize_input(&input);

    munit_assert_uint32(input.input_flags__pressed, ==, INPUT_NONE);
    munit_assert_uint32(input.input_flags__held, ==, INPUT_NONE);
    munit_assert_uint32(input.input_flags__released, ==, INPUT_NONE);
    munit_assert_uint32(input.input_flags__pressed_old, ==, INPUT_NONE);
    munit_assert_int32(input.cursor__3i32.x__i32, ==, 0);
    munit_assert_int32(input.cursor__3i32.y__i32, ==, 0);
    munit_assert_int32(input.cursor__3i32.z__i32, ==, 0);
    munit_assert_int32(input.cursor__old__3i32.x__i32, ==, 0);
    munit_assert_int32(input.cursor__old__3i32.y__i32, ==, 0);
    munit_assert_int32(input.cursor__old__3i32.z__i32, ==, 0);
    munit_assert_uint8(input.index_of__writing_buffer__read, ==, 0);
    munit_assert_uint8(input.index_of__writing_buffer__write, ==, 0);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__forward_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD;

    munit_assert_true(is_input__forward_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__forward_pressed__returns_false_when_not_set) {
    Input input;
    initialize_input(&input);

    munit_assert_false(is_input__forward_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__left_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_LEFT;

    munit_assert_true(is_input__left_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__right_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_RIGHT;

    munit_assert_true(is_input__right_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__backward_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_BACKWARD;

    munit_assert_true(is_input__backward_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__use_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_USE;

    munit_assert_true(is_input__use_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__use_secondary_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_USE_SECONDARY;

    munit_assert_true(is_input__use_secondary_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__click_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_CLICK;

    munit_assert_true(is_input__click_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__lockon_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_LOCKON;

    munit_assert_true(is_input__lockon_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__game_settings_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_GAME_SETTINGS;

    munit_assert_true(is_input__game_settings_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__examine_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_EXAMINE;

    munit_assert_true(is_input__examine_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__consume_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_CONSUME;

    munit_assert_true(is_input__consume_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__turn_left_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_TURN_LEFT;

    munit_assert_true(is_input__turn_left_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(is_input__turn_right_pressed__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_TURN_RIGHT;

    munit_assert_true(is_input__turn_right_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(pressed_query__returns_false_for_different_flag) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD;

    munit_assert_false(is_input__left_pressed(&input));
    munit_assert_false(is_input__right_pressed(&input));
    munit_assert_false(is_input__backward_pressed(&input));
    munit_assert_false(is_input__use_pressed(&input));
    munit_assert_false(is_input__click_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.6 Button State Queries — Pressed
///
TEST_FUNCTION(multiple_pressed_flags__all_query_true) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD | INPUT_USE | INPUT_CLICK;

    munit_assert_true(is_input__forward_pressed(&input));
    munit_assert_true(is_input__use_pressed(&input));
    munit_assert_true(is_input__click_pressed(&input));
    munit_assert_false(is_input__left_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__forward_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_FORWARD;

    munit_assert_true(is_input__forward_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__forward_held__returns_false_when_not_set) {
    Input input;
    initialize_input(&input);

    munit_assert_false(is_input__forward_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__left_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_LEFT;

    munit_assert_true(is_input__left_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__right_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_RIGHT;

    munit_assert_true(is_input__right_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__backward_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_BACKWARD;

    munit_assert_true(is_input__backward_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__use_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_USE;

    munit_assert_true(is_input__use_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__use_secondary_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_USE_SECONDARY;

    munit_assert_true(is_input__use_secondary_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__lockon_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_LOCKON;

    munit_assert_true(is_input__lockon_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__game_settings_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_GAME_SETTINGS;

    munit_assert_true(is_input__game_settings_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__examine_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_EXAMINE;

    munit_assert_true(is_input__examine_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__consume_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_CONSUME;

    munit_assert_true(is_input__consume_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__turn_left_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_TURN_LEFT;

    munit_assert_true(is_input__turn_left_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.7 Button State Queries — Held
///
TEST_FUNCTION(is_input__turn_right_held__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_TURN_RIGHT;

    munit_assert_true(is_input__turn_right_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__forward_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_FORWARD;

    munit_assert_true(is_input__forward_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__forward_released__returns_false_when_not_set) {
    Input input;
    initialize_input(&input);

    munit_assert_false(is_input__forward_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__left_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_LEFT;

    munit_assert_true(is_input__left_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__right_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_RIGHT;

    munit_assert_true(is_input__right_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__backward_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_BACKWARD;

    munit_assert_true(is_input__backward_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__use_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_USE;

    munit_assert_true(is_input__use_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__use_secondary_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_USE_SECONDARY;

    munit_assert_true(is_input__use_secondary_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__click_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_CLICK;

    munit_assert_true(is_input__click_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__lockon_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_LOCKON;

    munit_assert_true(is_input__lockon_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__game_settings_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_GAME_SETTINGS;

    munit_assert_true(is_input__game_settings_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__examine_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_EXAMINE;

    munit_assert_true(is_input__examine_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__consume_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_CONSUME;

    munit_assert_true(is_input__consume_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__turn_left_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_TURN_LEFT;

    munit_assert_true(is_input__turn_left_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.5 Button State Queries — Released
///
TEST_FUNCTION(is_input__turn_right_released__returns_true_when_set) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_TURN_RIGHT;

    munit_assert_true(is_input__turn_right_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.9 Input Consumption
///
TEST_FUNCTION(consume_input__clears_specified_flag_from_all_states) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD | INPUT_USE;
    input.input_flags__held = INPUT_FORWARD | INPUT_USE;
    input.input_flags__released = INPUT_FORWARD | INPUT_USE;

    consume_input(&input, INPUT_FORWARD);

    munit_assert_false(is_input__forward_pressed(&input));
    munit_assert_false(is_input__forward_held(&input));
    munit_assert_false(is_input__forward_released(&input));
    munit_assert_true(is_input__use_pressed(&input));
    munit_assert_true(is_input__use_held(&input));
    munit_assert_true(is_input__use_released(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.9 Input Consumption
///
TEST_FUNCTION(consume_input__clears_multiple_flags) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD | INPUT_LEFT | INPUT_USE;
    input.input_flags__held = INPUT_FORWARD | INPUT_LEFT | INPUT_USE;
    input.input_flags__released = INPUT_FORWARD | INPUT_LEFT | INPUT_USE;

    consume_input(&input, INPUT_FORWARD | INPUT_LEFT);

    munit_assert_false(is_input__forward_pressed(&input));
    munit_assert_false(is_input__left_pressed(&input));
    munit_assert_true(is_input__use_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.4 Clear, 1.5.10 Postconditions
///
TEST_FUNCTION(clear_input__zeroes_all_flags_and_saves_cursor) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD;
    input.input_flags__held = INPUT_USE;
    input.input_flags__released = INPUT_CLICK;
    input.cursor__3i32.x__i32 = 42;
    input.cursor__3i32.y__i32 = 84;
    input.cursor__3i32.z__i32 = 0;

    clear_input(&input);

    munit_assert_uint32(input.input_flags__pressed, ==, INPUT_NONE);
    munit_assert_uint32(input.input_flags__held, ==, INPUT_NONE);
    munit_assert_uint32(input.input_flags__released, ==, INPUT_NONE);
    munit_assert_int32(input.cursor__old__3i32.x__i32, ==, 42);
    munit_assert_int32(input.cursor__old__3i32.y__i32, ==, 84);
    munit_assert_int32(input.cursor__3i32.x__i32, ==, 0);
    munit_assert_int32(input.cursor__3i32.y__i32, ==, 0);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_held__true_when_cursor_not_moved) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_CLICK;
    input.cursor__3i32.x__i32 = 10;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_true(is_input__click_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_held__false_when_cursor_moved) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_CLICK;
    input.cursor__3i32.x__i32 = 15;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_false(is_input__click_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_held__false_when_click_not_held) {
    Input input;
    initialize_input(&input);
    input.cursor__3i32.x__i32 = 10;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_false(is_input__click_held(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_dragged__true_when_cursor_moved) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_CLICK;
    input.cursor__3i32.x__i32 = 15;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_true(is_input__click_dragged(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_dragged__false_when_cursor_not_moved) {
    Input input;
    initialize_input(&input);
    input.input_flags__held = INPUT_CLICK;
    input.cursor__3i32.x__i32 = 10;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_false(is_input__click_dragged(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.8 Composite Input Queries
///
TEST_FUNCTION(is_input__click_dragged__false_when_click_not_held) {
    Input input;
    initialize_input(&input);
    input.cursor__3i32.x__i32 = 15;
    input.cursor__3i32.y__i32 = 20;
    input.cursor__3i32.z__i32 = 0;
    input.cursor__old__3i32.x__i32 = 10;
    input.cursor__old__3i32.y__i32 = 20;
    input.cursor__old__3i32.z__i32 = 0;

    munit_assert_false(is_input__click_dragged(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.3 Writing Buffer
///
TEST_FUNCTION(writing_buffer__buffer_and_poll_single_char) {
    Input input;
    initialize_input(&input);

    buffer_input_for__writing(&input, 'A');
    unsigned char ch = poll_input_for__writing(&input);

    munit_assert_uint8(ch, ==, 'A');

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.3 Writing Buffer
///
TEST_FUNCTION(writing_buffer__buffer_and_poll_multiple_chars) {
    Input input;
    initialize_input(&input);

    buffer_input_for__writing(&input, 'H');
    buffer_input_for__writing(&input, 'i');

    unsigned char ch1 = poll_input_for__writing(&input);
    unsigned char ch2 = poll_input_for__writing(&input);

    munit_assert_uint8(ch1, ==, 'H');
    munit_assert_uint8(ch2, ==, 'i');

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.3 Writing Buffer
///
TEST_FUNCTION(writing_buffer__last_symbol_returns_most_recent) {
    Input input;
    initialize_input(&input);

    buffer_input_for__writing(&input, 'X');
    buffer_input_for__writing(&input, 'Y');

    unsigned char last = get_last_symbol_of__input_for__writing(&input);
    munit_assert_uint8(last, ==, 'Y');

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.10 Mode Management
///
TEST_FUNCTION(get_input_mode__returns_current_mode) {
    Input input;
    initialize_input(&input);

    munit_assert_uint8(get_input_mode_of__input(&input), ==, INPUT_MODE__NONE);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.4.10 Mode Management
///
TEST_FUNCTION(set_input_mode__changes_mode) {
    Input input;
    initialize_input(&input);

    set_input_mode_of__input(&input, INPUT_MODE__WRITING);
    munit_assert_uint8(get_input_mode_of__input(&input), ==, INPUT_MODE__WRITING);

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.5.2 Three-State Input Model
///
TEST_FUNCTION(held_and_pressed_independent) {
    Input input;
    initialize_input(&input);
    input.input_flags__pressed = INPUT_FORWARD;
    input.input_flags__held = INPUT_LEFT;

    munit_assert_true(is_input__forward_pressed(&input));
    munit_assert_false(is_input__forward_held(&input));
    munit_assert_true(is_input__left_held(&input));
    munit_assert_false(is_input__left_pressed(&input));

    return MUNIT_OK;
}

///
/// Spec: docs/specs/core/input/input.h.spec.md
/// Section: 1.5.2 Three-State Input Model
///
TEST_FUNCTION(released_independent_of_pressed_and_held) {
    Input input;
    initialize_input(&input);
    input.input_flags__released = INPUT_USE;

    munit_assert_true(is_input__use_released(&input));
    munit_assert_false(is_input__use_pressed(&input));
    munit_assert_false(is_input__use_held(&input));

    return MUNIT_OK;
}

DEFINE_SUITE(input,
    INCLUDE_TEST__STATELESS(initialize_input__sets_all_flags_to_zero),
    INCLUDE_TEST__STATELESS(is_input__forward_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__forward_pressed__returns_false_when_not_set),
    INCLUDE_TEST__STATELESS(is_input__left_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__right_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__backward_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_secondary_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__click_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__lockon_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__game_settings_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__examine_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__consume_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_left_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_right_pressed__returns_true_when_set),
    INCLUDE_TEST__STATELESS(pressed_query__returns_false_for_different_flag),
    INCLUDE_TEST__STATELESS(multiple_pressed_flags__all_query_true),
    INCLUDE_TEST__STATELESS(is_input__forward_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__forward_held__returns_false_when_not_set),
    INCLUDE_TEST__STATELESS(is_input__left_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__right_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__backward_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_secondary_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__lockon_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__game_settings_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__examine_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__consume_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_left_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_right_held__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__forward_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__forward_released__returns_false_when_not_set),
    INCLUDE_TEST__STATELESS(is_input__left_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__right_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__backward_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__use_secondary_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__click_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__lockon_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__game_settings_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__examine_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__consume_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_left_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(is_input__turn_right_released__returns_true_when_set),
    INCLUDE_TEST__STATELESS(consume_input__clears_specified_flag_from_all_states),
    INCLUDE_TEST__STATELESS(consume_input__clears_multiple_flags),
    INCLUDE_TEST__STATELESS(clear_input__zeroes_all_flags_and_saves_cursor),
    INCLUDE_TEST__STATELESS(is_input__click_held__true_when_cursor_not_moved),
    INCLUDE_TEST__STATELESS(is_input__click_held__false_when_cursor_moved),
    INCLUDE_TEST__STATELESS(is_input__click_held__false_when_click_not_held),
    INCLUDE_TEST__STATELESS(is_input__click_dragged__true_when_cursor_moved),
    INCLUDE_TEST__STATELESS(is_input__click_dragged__false_when_cursor_not_moved),
    INCLUDE_TEST__STATELESS(is_input__click_dragged__false_when_click_not_held),
    INCLUDE_TEST__STATELESS(writing_buffer__buffer_and_poll_single_char),
    INCLUDE_TEST__STATELESS(writing_buffer__buffer_and_poll_multiple_chars),
    INCLUDE_TEST__STATELESS(writing_buffer__last_symbol_returns_most_recent),
    INCLUDE_TEST__STATELESS(get_input_mode__returns_current_mode),
    INCLUDE_TEST__STATELESS(set_input_mode__changes_mode),
    INCLUDE_TEST__STATELESS(held_and_pressed_independent),
    INCLUDE_TEST__STATELESS(released_independent_of_pressed_and_held),
    END_TESTS)
