#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "input/input.h"
#include "platform.h"
#include "platform_defaults.h"
#include "platform_defines.h"
#include <SDL2/SDL_keyboard.h>
#include <SDL2/SDL_keycode.h>
#include <SDL2/SDL_mouse.h>
#include <SDL2/SDL_scancode.h>
#include <SDL2/SDL_video.h>
#include <input/sdl_input.h>
#include "sdl_defines.h"

enum Input_Binding_Kind {
    Input_Binding_Kind__None,
    Input_Binding_Kind__Keyboard,
    Input_Binding_Kind__Mouse,
};

typedef struct {
    Input_Code__u32 input_code__u32;
    Input_Flags__u32 input_flag__u32;

    enum Input_Binding_Kind the_kind_of__input_binding;
    union {
        SDL_Scancode sdl_scancode;
        u32 sdl_mouse_button;
    };
} Input_Binding;

Input_Binding __SDL_INPUT_BINDINGS[SDL_QUANTITY_OF__INPUTS];

const char __SDL_ASCII_MAP[2][SDL_NUM_SCANCODES] = {
        {
        [SDL_SCANCODE_A] = 'a',
        [SDL_SCANCODE_B] = 'b',
        [SDL_SCANCODE_C] = 'c',
        [SDL_SCANCODE_D] = 'd',
        [SDL_SCANCODE_E] = 'e',
        [SDL_SCANCODE_F] = 'f',
        [SDL_SCANCODE_G] = 'g',
        [SDL_SCANCODE_H] = 'h',
        [SDL_SCANCODE_I] = 'i',
        [SDL_SCANCODE_J] = 'j',
        [SDL_SCANCODE_K] = 'k',
        [SDL_SCANCODE_L] = 'l',
        [SDL_SCANCODE_M] = 'm',
        [SDL_SCANCODE_N] = 'n',
        [SDL_SCANCODE_O] = 'o',
        [SDL_SCANCODE_P] = 'p',
        [SDL_SCANCODE_Q] = 'q',
        [SDL_SCANCODE_R] = 'r',
        [SDL_SCANCODE_S] = 's',
        [SDL_SCANCODE_T] = 't',
        [SDL_SCANCODE_U] = 'u',
        [SDL_SCANCODE_V] = 'v',
        [SDL_SCANCODE_W] = 'w',
        [SDL_SCANCODE_X] = 'x',
        [SDL_SCANCODE_Y] = 'y',
        [SDL_SCANCODE_Z] = 'z',

        [SDL_SCANCODE_1] = '1',
        [SDL_SCANCODE_2] = '2',
        [SDL_SCANCODE_3] = '3',
        [SDL_SCANCODE_4] = '4',
        [SDL_SCANCODE_5] = '5',
        [SDL_SCANCODE_6] = '6',
        [SDL_SCANCODE_7] = '7',
        [SDL_SCANCODE_8] = '8',
        [SDL_SCANCODE_9] = '9',
        [SDL_SCANCODE_0] = '0',

        [SDL_SCANCODE_RETURN] = '\n',
        [SDL_SCANCODE_ESCAPE] = 27,
        [SDL_SCANCODE_DELETE] = 127,
        [SDL_SCANCODE_BACKSPACE] = '\b',
        [SDL_SCANCODE_TAB] = '\t',
        [SDL_SCANCODE_SPACE] = ' ',

        [SDL_SCANCODE_MINUS] = '-',
        [SDL_SCANCODE_EQUALS] = '=',
        [SDL_SCANCODE_LEFTBRACKET] = '[',
        [SDL_SCANCODE_RIGHTBRACKET] = ']',
        [SDL_SCANCODE_BACKSLASH] = '\\',
        [SDL_SCANCODE_NONUSBACKSLASH] = '\\',
        [SDL_SCANCODE_SEMICOLON] = ';',
        [SDL_SCANCODE_APOSTROPHE] = '\'',
        [SDL_SCANCODE_GRAVE] = '`',
        [SDL_SCANCODE_COMMA] = ',',
        [SDL_SCANCODE_PERIOD] = '.',
        [SDL_SCANCODE_SLASH] = '/',
    },

    // Shifted (index 1)
    {
        [SDL_SCANCODE_A] = 'A',
        [SDL_SCANCODE_B] = 'B',
        [SDL_SCANCODE_C] = 'C',
        [SDL_SCANCODE_D] = 'D',
        [SDL_SCANCODE_E] = 'E',
        [SDL_SCANCODE_F] = 'F',
        [SDL_SCANCODE_G] = 'G',
        [SDL_SCANCODE_H] = 'H',
        [SDL_SCANCODE_I] = 'I',
        [SDL_SCANCODE_J] = 'J',
        [SDL_SCANCODE_K] = 'K',
        [SDL_SCANCODE_L] = 'L',
        [SDL_SCANCODE_M] = 'M',
        [SDL_SCANCODE_N] = 'N',
        [SDL_SCANCODE_O] = 'O',
        [SDL_SCANCODE_P] = 'P',
        [SDL_SCANCODE_Q] = 'Q',
        [SDL_SCANCODE_R] = 'R',
        [SDL_SCANCODE_S] = 'S',
        [SDL_SCANCODE_T] = 'T',
        [SDL_SCANCODE_U] = 'U',
        [SDL_SCANCODE_V] = 'V',
        [SDL_SCANCODE_W] = 'W',
        [SDL_SCANCODE_X] = 'X',
        [SDL_SCANCODE_Y] = 'Y',
        [SDL_SCANCODE_Z] = 'Z',

        [SDL_SCANCODE_1] = '!',
        [SDL_SCANCODE_2] = '@',
        [SDL_SCANCODE_3] = '#',
        [SDL_SCANCODE_4] = '$',
        [SDL_SCANCODE_5] = '%',
        [SDL_SCANCODE_6] = '^',
        [SDL_SCANCODE_7] = '&',
        [SDL_SCANCODE_8] = '*',
        [SDL_SCANCODE_9] = '(',
        [SDL_SCANCODE_0] = ')',

        [SDL_SCANCODE_RETURN] = '\n',
        [SDL_SCANCODE_ESCAPE] = 27,
        [SDL_SCANCODE_DELETE] = 127,
        [SDL_SCANCODE_BACKSPACE] = '\b',
        [SDL_SCANCODE_TAB] = '\t',
        [SDL_SCANCODE_SPACE] = ' ',

        [SDL_SCANCODE_MINUS] = '_',
        [SDL_SCANCODE_EQUALS] = '+',
        [SDL_SCANCODE_LEFTBRACKET] = '{',
        [SDL_SCANCODE_RIGHTBRACKET] = '}',
        [SDL_SCANCODE_BACKSLASH] = '|',
        [SDL_SCANCODE_NONUSBACKSLASH] = '|',
        [SDL_SCANCODE_SEMICOLON] = ':',
        [SDL_SCANCODE_APOSTROPHE] = '"',
        [SDL_SCANCODE_GRAVE] = '~',
        [SDL_SCANCODE_COMMA] = '<',
        [SDL_SCANCODE_PERIOD] = '>',
        [SDL_SCANCODE_SLASH] = '?',
    }
};

void SDL_initialize_input_bindings() {
    __SDL_INPUT_BINDINGS[INPUT_CODE_NONE] = (Input_Binding){
        INPUT_CODE_NONE,
        INPUT_NONE,
        Input_Binding_Kind__None,
        SDL_NUM_SCANCODES
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_FORWARD] = (Input_Binding){
        INPUT_CODE_FORWARD,
        INPUT_FORWARD,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_W
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_LEFT] = (Input_Binding){
        INPUT_CODE_LEFT,
        INPUT_LEFT,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_A
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_RIGHT] = (Input_Binding){
        INPUT_CODE_RIGHT,
        INPUT_RIGHT,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_D
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_BACKWARD] = (Input_Binding){
        INPUT_CODE_BACKWARD,
        INPUT_BACKWARD,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_S
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_GAME_SETTINGS] = (Input_Binding){
        INPUT_CODE_GAME_SETTINGS,
        INPUT_GAME_SETTINGS,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_ESCAPE
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_LOCKON] = (Input_Binding){
        INPUT_CODE_LOCKON,
        INPUT_LOCKON,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_TAB
    };
    // TODO: have a sense of UI_Focus between gamespace and UI.
    //       allow for input.c to acknowledge the state.
    __SDL_INPUT_BINDINGS[INPUT_CODE_USE] = (Input_Binding){
        INPUT_CODE_USE,
        INPUT_USE,
        Input_Binding_Kind__Mouse,
        SDL_BUTTON(1)
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_USE_SECONDARY] = (Input_Binding){
        INPUT_CODE_USE_SECONDARY,
        INPUT_USE_SECONDARY,
        Input_Binding_Kind__Mouse,
        SDL_BUTTON(3)
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_EXAMINE] = (Input_Binding){
        INPUT_CODE_EXAMINE,
        INPUT_EXAMINE,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_F
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_CONSUME] = (Input_Binding){
        INPUT_CODE_CONSUME,
        INPUT_CONSUME,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_LEFT
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_TURN_RIGHT] = (Input_Binding){
        INPUT_CODE_TURN_RIGHT,
        INPUT_TURN_RIGHT,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_Q
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_TURN_LEFT] = (Input_Binding){
        INPUT_CODE_TURN_LEFT,
        INPUT_TURN_LEFT,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_E
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_CLICK] = (Input_Binding){
        INPUT_CODE_CLICK,
        INPUT_CLICK,
        Input_Binding_Kind__Mouse,
        SDL_BUTTON(1)
    };
    __SDL_INPUT_BINDINGS[INPUT_CODE_LOCKON] = (Input_Binding){
        INPUT_CODE_LOCKON,
        INPUT_LOCKON,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_CAPSLOCK
    };
    __SDL_INPUT_BINDINGS[SDL_INPUT_CODE_EQUIP] = (Input_Binding){
        SDL_INPUT_CODE_EQUIP,
        SDL_INPUT_EQUIP,
        Input_Binding_Kind__Keyboard,
        SDL_SCANCODE_TAB
    };
}

i32F20 __SDL_writing_hold_timer = 0;
i32F20 __SDL_writing_up_timer = 0;

void SDL_poll_input__writing(
        Game *p_game,
        Input *p_input) {

    const u8 *p_keys = SDL_GetKeyboardState(0);
    SDL_Keymod sdl_mod__state = SDL_GetModState();

    bool caps = 
        (sdl_mod__state & KMOD_CAPS)
        | (sdl_mod__state & (KMOD_LSHIFT | KMOD_RSHIFT))
        ;
    bool key_pressed = false;
    for (Index__u32 index_of__scan_code =
            SDL_SCANCODE_UNKNOWN + 1;
            index_of__scan_code
            < SDL_NUM_SCANCODES;
            index_of__scan_code++) {
        char symbol = 
            __SDL_ASCII_MAP[caps][index_of__scan_code];
        char symbol_caps_conjugate = 
            __SDL_ASCII_MAP[!caps][index_of__scan_code];
        if (p_keys[index_of__scan_code] 
                && symbol) {
            if (symbol !=
                    get_last_symbol_of__input_for__writing(p_input)
                    && symbol_caps_conjugate !=
                    get_last_symbol_of__input_for__writing(p_input)) {
                __SDL_writing_hold_timer = 0;
            }
            if (!__SDL_writing_hold_timer) {
                buffer_input_for__writing(
                        p_input, 
                        symbol);
                __SDL_writing_hold_timer = 1;
            }
            key_pressed = true;
            break;
        }
    }
    if (!key_pressed) {
        __SDL_writing_hold_timer = 0;
    } else {
        __SDL_writing_up_timer = 0;
    }
    if (__SDL_writing_hold_timer){
        if (__SDL_writing_hold_timer < (BIT(17) | BIT(12))) {
            __SDL_writing_hold_timer += get_elapsed_time__u32F20_of__game(p_game);
        } else {
            __SDL_writing_hold_timer = 0;
        }
    }
}

void PLATFORM_poll_input(
        Game *p_game,
        Input *p_input) {
    const u8 *p_keys = SDL_GetKeyboardState(0);

    p_input->input_flags__pressed_old =
        p_input->input_flags__pressed;

    clear_input(p_input);

    u32 mouse_button_state = 
        SDL_GetMouseState(
                &p_input->cursor__3i32.x__i32, 
                &p_input->cursor__3i32.y__i32);

    for (Index__u8 index=0;
            index<SDL_QUANTITY_OF__INPUTS;
            index++) {
        Input_Binding *p_input_binding =
            &__SDL_INPUT_BINDINGS[index];
        switch(p_input_binding->the_kind_of__input_binding) {
            default:
                continue;
            case Input_Binding_Kind__Keyboard:
                switch (get_input_mode_of__input(p_input)) {
                    default:
                    case INPUT_MODE__NORMAL:
                        if (p_keys[p_input_binding->sdl_scancode])
                            p_input->input_flags__pressed |=
                                p_input_binding->input_flag__u32
                                ;
                        break;
                    case INPUT_MODE__WRITING:
                        break;
                }
                break;
            case Input_Binding_Kind__Mouse:
                if (mouse_button_state & 
                        p_input_binding->sdl_mouse_button)
                    p_input->input_flags__pressed |=
                        p_input_binding->input_flag__u32
                        ;
                break;
        }
    }

    switch (get_input_mode_of__input(p_input)) {
        default:
            break;
        case INPUT_MODE__WRITING:
            SDL_poll_input__writing(
                    p_game, 
                    p_input);
            break;
    }

    p_input->input_flags__held =
        p_input->input_flags__pressed_old
        & p_input->input_flags__pressed
        ;
    
    p_input->input_flags__released =
        (~p_input->input_flags__pressed)
        & p_input->input_flags__pressed_old
        ;

    PLATFORM_Gfx_Context *p_PLATFORM_gfx_context =
        get_p_PLATFORM_gfx_context_from__game(p_game);
    f_SDL_Process_Input f_SDL_process_input =
        p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_process_input
        ;
    if (!f_SDL_process_input)
        return;

    f_SDL_process_input(
            p_game,
            p_input);
}
