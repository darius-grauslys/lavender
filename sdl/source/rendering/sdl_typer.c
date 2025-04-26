#include "rendering/sdl_typer.h"
#include "sdl_defines.h"
#include "rendering/sdl_gfx_context.h"

void PLATFORM_put_char_in__typer(
        Gfx_Context *p_gfx_context,
        Typer *p_typer,
        unsigned char letter) {
    f_SDL_Put_Char_In__Typer f_SDL_put_char_in__typer = 
        p_gfx_context
        ->p_PLATFORM_gfx_context
        ->SDL_gfx_sub_context__wrapper
        .f_SDL_put_char_in__typer;
#ifndef NDEBUG
    if (!f_SDL_put_char_in__typer) {
        debug_warning("Did you forget to render a graphics backend?");
        debug_abort("SDL::PLATFORM_put_char_in__typer, f_SDL_put_char_in__typer == 0.");
        return;
    }
#endif
    f_SDL_put_char_in__typer(
            p_gfx_context,
            p_typer,
            letter);
}
