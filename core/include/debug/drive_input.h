#ifndef DRIVE_INPUT_H
#define DRIVE_INPUT_H

/*
 * drive_input.h gives useful gdb access to manipulating Input of p_game.
 *
 * NOTE: -DDEBUG_INPUT must be given as a debug flag for
 * input to be properly driven by this module. It is a flag
 * used by Lavender backends to withhold from clearing
 * the input on each frame.
 */

#include "defines_weak.h"
#include <defines.h>

#ifndef NDEBUG
void debug_drive_input__flag(Game *p_game, Input_Flags__u32 input_flag);
void debug_drive_input__mouse_pos(Game *p_game, Vector__3i32 cursor__3i32);

///
/// Spawns a process to perform a 2 frame click.
/// Set a breakpoint on the complete_process() of 
/// m_debug_process__click to get immediate game state
/// prior to any engine logic processing the click release.
///
/// This process utilizes process_valueA__i16 to 
/// track click state between frames.
///
/// Returns a pointer to the process if the process was made.
///
Process *debug_dispatch_click(Game *p_game, Vector__3i32 cursor__3i32);

#endif

#endif
