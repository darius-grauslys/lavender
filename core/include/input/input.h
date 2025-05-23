#ifndef INPUT_H
#define INPUT_H

#include "platform_defaults.h"
#include <bits/pthreadtypes.h>
#include <vectors.h>
#include <defines.h>

void initialize_input(Input *p_input);

///
/// Get the next character made by the player
/// via some keyboard input, be it touch, controller, or keyboard.
///
unsigned char poll_input_for__writing(Input *p_input);

void buffer_input_for__writing(
        Input *p_input,
        char symbol);

static inline
unsigned char get_last_symbol_of__input_for__writing(
        Input *p_input) {
    return p_input->last_symbol;
}

static inline
void clear_input(Input *p_input) {
    p_input->input_flags__held = INPUT_NONE;
    p_input->input_flags__pressed = INPUT_NONE;
    p_input->input_flags__released = INPUT_NONE;
    p_input->cursor__old__3i32 =
        p_input->cursor__3i32;
    initialize_3i32_vector(&p_input->cursor__3i32);
}

static bool inline is_input__forward_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_FORWARD;
}
static bool inline is_input__left_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_LEFT;
}
static bool inline is_input__right_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_RIGHT;
}
static bool inline is_input__backward_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_BACKWARD;
}
static bool inline is_input__game_settings_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_GAME_SETTINGS;
}
static bool inline is_input__lockon_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_LOCKON;
}
static bool inline is_input__use_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_USE;
}
static bool inline is_input__use_secondary_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_USE_SECONDARY;
}
static bool inline is_input__examine_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_EXAMINE;
}
static bool inline is_input__consume_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_CONSUME;
}
static bool inline is_input__turn_left_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_TURN_LEFT;
}
static bool inline is_input__turn_right_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_TURN_RIGHT;
}
static bool inline is_input__none_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_NONE;
}
static bool inline is_input__click_released(Input *p_input) {
    return p_input->input_flags__released & INPUT_CLICK;
}



static bool inline is_input__forward_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_FORWARD;
}
static bool inline is_input__left_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_LEFT;
}
static bool inline is_input__right_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_RIGHT;
}
static bool inline is_input__backward_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_BACKWARD;
}
static bool inline is_input__game_settings_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_GAME_SETTINGS;
}
static bool inline is_input__lockon_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_LOCKON;
}
static bool inline is_input__use_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_USE;
}
static bool inline is_input__use_secondary_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_USE_SECONDARY;
}
static bool inline is_input__examine_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_EXAMINE;
}
static bool inline is_input__consume_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_CONSUME;
}
static bool inline is_input__turn_left_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_TURN_LEFT;
}
static bool inline is_input__turn_right_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_TURN_RIGHT;
}
static bool inline is_input__none_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_NONE;
}
static bool inline is_input__click_pressed(Input *p_input) {
    return p_input->input_flags__pressed & INPUT_CLICK;
}



static bool inline is_input__forward_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_FORWARD;
}
static bool inline is_input__left_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_LEFT;
}
static bool inline is_input__right_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_RIGHT;
}
static bool inline is_input__backward_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_BACKWARD;
}
static bool inline is_input__game_settings_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_GAME_SETTINGS;
}
static bool inline is_input__lockon_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_LOCKON;
}
static bool inline is_input__use_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_USE;
}
static bool inline is_input__use_secondary_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_USE_SECONDARY;
}
static bool inline is_input__examine_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_EXAMINE;
}
static bool inline is_input__none_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_NONE;
}
static bool inline is_input__consume_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_CONSUME;
}
static bool inline is_input__turn_left_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_TURN_LEFT;
}
static bool inline is_input__turn_right_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_TURN_RIGHT;
}
static bool inline is_input__click_held(Input *p_input) {
    return p_input->input_flags__held & INPUT_CLICK
        && is_vectors_3i32__equal(
                p_input->cursor__3i32,
                p_input->cursor__old__3i32)
                ;
}

static bool inline is_input__click_dragged(Input *p_input) {
    return p_input->input_flags__held & INPUT_CLICK
        && !is_vectors_3i32__equal(
                p_input->cursor__3i32,
                p_input->cursor__old__3i32)
                ;
}

static inline
void consume_input(
        Input *p_input,
        Input_Flags__u32 input_flags) {
    p_input
        ->input_flags__released &=
        ~input_flags;
    p_input
        ->input_flags__pressed &=
        ~input_flags;
    p_input
        ->input_flags__held &=
        ~input_flags;
}

static inline
Input_Mode__u8 get_input_mode_of__input(
        Input *p_input) {
    return p_input->input_mode__u8;
}

static inline
void set_input_mode_of__input(
        Input *p_input,
        Input_Mode__u8 input_mode__u8) {
    p_input->input_mode__u8 =
        input_mode__u8;
}

#endif
