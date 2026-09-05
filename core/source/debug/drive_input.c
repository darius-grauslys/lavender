#include "defines.h"
#include "game.h"
#include "platform_defaults.h"
#include "process/process.h"
#include "process/process_manager.h"
#include <debug/drive_input.h>


void debug_drive_input__flag(Game *p_game, Input_Flags__u32 input_flag) {
    p_game->input.input_flags__pressed |=
        input_flag;
}

void debug_drop_input__flag(Game *p_game, Input_Flags__u32 input_flag) {
    p_game->input.input_flags__pressed &=
        ~input_flag;
}

void debug_drive_input__mouse_pos(Game *p_game, Vector__3i32 cursor__3i32) {
    p_game->input.cursor__3i32 =
        cursor__3i32;
}

void m_debug_process__click(Process *p_this_process, Game *p_game) {
    switch(p_this_process->process_valueA__i16) {
        case 0:
            // Set as pressed, then wait 1 frame
            debug_drive_input__flag(
                    p_game, 
                    INPUT_CLICK);
            p_this_process->process_valueA__i16++;
            return;
        case 1:
            // Move input into old state, since such logic is
            // turned off on the backend
            get_p_input_from__game(p_game)
                ->input_flags__pressed_old =
                get_p_input_from__game(p_game)
                ->input_flags__pressed;
            p_this_process->process_valueA__i16++;
            return;
        case 2:
            // Release
            debug_drop_input__flag(
                    p_game, 
                    INPUT_CLICK);
            p_this_process->process_valueA__i16++;
            return;
        case 3:
            // Clean up old state
            get_p_input_from__game(p_game)
                ->input_flags__pressed_old &= ~INPUT_CLICK;
            break;
    }

    // Complete process.
    // Set a breakpoint here!
    complete_process(p_this_process);
}

Process *debug_dispatch_click(Game *p_game, Vector__3i32 cursor__3i32) {
    Process *p_process = 
        run_process(
            get_p_process_manager_from__game(p_game), 
            m_debug_process__click, 
            PROCESS_PRIORITY__0_MAXIMUM, 
            PROCESS_FLAGS__NONE);
    debug_drive_input__mouse_pos(
            p_game, 
            cursor__3i32);
    p_process->process_valueA__i16 = 0;
    return p_process;
}
