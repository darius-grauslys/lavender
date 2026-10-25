#include "ui/implemented/ui_window_registrar.h"
#include "defines.h"
#include "defines_weak.h"
#include "rendering/gfx_context.h"
#include "types/implemented/rendering/graphics_window_kind.h"
#include "ui/implemented/ui_window__main.h"
#include "ui/ui_context.h"
// GEN-INCLUDE-BEGIN
// GEN-INCLUDE-END

void register_ui_windows(Gfx_Context *p_gfx_context) {
    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);
    // GEN-BEGIN
    // ***) Register the HUD window: its load function (which
    // builds the UI elements), its close function, its
    // Graphics_Window_Kind, and the pool quantities.
    //   signed_quantity_of__sprites:
    //     > 0 = allocate a sprite manager of this size for the
    //           window (sprite-based UI)
    //     < 0 = use the parent window's sprite manager
    //     = 0 = no sprites (we use UI tile spans instead)
    //   signed_quantity_of__ui_elements:
    //     > 0 = allocate a ui_manager of this capacity
    //     < 0 = use the parent window's ui_manager
    //     = 0 = no ui elements (a pure pass-through window)
    register_ui_window_into__ui_context(
            p_ui_context,
            allocate_ui_for__ui_window__main,
            f_ui_window__close__main,
            Graphics_Window_Kind__UI__Hud,
            0,  // signed_quantity_of__sprites
            16); // signed_quantity_of__ui_elements
    // GEN-END
}
