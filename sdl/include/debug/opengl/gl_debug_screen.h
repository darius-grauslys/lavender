#ifndef GL_DEBUG_SCREEN_H
#define GL_DEBUG_SCREEN_H

/*
 * gl_debug_screen gives indirect screen access by writing
 * the contents of a given framebuffer to ./build/sdl/screen.png
 */

#include <defines.h>
#include <rendering/opengl/gl_defines.h>

#ifndef NDEBUG
///
/// Takes a screen cap of the main buffer
/// and saves it to ./build/sdl/screen.png
///
/// Returns false only if failure occurs.
///
bool gl_debug_screencap(Game *p_game);

///
/// Takes a screen cap of the provided buffer
/// and saves it to ./build/sdl/screen.png
///
/// Returns false only if failure occurs.
///
bool gl_debug_screencap__framebuffer(Game *p_game, GL_Framebuffer *p_gl_framebuffer);
#endif

#endif
