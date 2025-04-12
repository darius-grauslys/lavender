#include "ui/implemented/ui_window_registrar.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/gfx_context.h"
#include "ui/handlers/ui_gfx_window__closer__default.h"
#include "ui/ui_context.h"

void register_ui_windows(Gfx_Context *p_gfx_context) {
    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);
    debug_warning("register_ui_windows, impl");
}
