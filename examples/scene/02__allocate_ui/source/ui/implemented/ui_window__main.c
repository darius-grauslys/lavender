#include "ui/implemented/ui_window__main.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "types/implemented/ui/ui_tile_kind.h"
#include "ui/ui_button.h"
#include "ui/ui_element.h"
#include "ui/ui_manager.h"
#include "ui/ui_tile.h"
#include "ui/ui_tile_span.h"
#include "vectors.h"

// The HUD is a row of 3 buttons along the top of the screen.
#define HUD_QUANTITY_OF__BUTTONS 3
#define HUD_BUTTON_WIDTH__PX 48
#define HUD_BUTTON_HEIGHT__PX 16
#define HUD_BUTTON_X_START__PX 16
#define HUD_BUTTON_X_STRIDE__PX 56
#define HUD_BUTTON_Y__PX 16

// ***) The click handler. Called by poll_ui_manager__update
// (which the scene invokes every frame) when a button's
// hitbox is strictly under the cursor and the click is released.
void m_ui_button__clicked_handler__main(
        UI_Element *p_this_button,
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    (void)p_gfx_window;
    debug_info("scene__main HUD: button %p clicked", p_this_button);
}

// ***) The UI window's load function. Invoked by
// open_ui_window() -> populate_window_with__ui() right after the
// window + ui_manager are allocated. This is where the window's
// UI_EElements are created and laid out.
bool allocate_ui_for__ui_window__main(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager,
        Identifier__u16 index_of__ui_element_offset__u16) {
    (void)p_gfx_context;
    (void)index_of__ui_element_offset__u16;

    // ***) Allocate the buttons in one call; they are linked
    // into a one-way succession via p_next.
    UI_Element *p_ui_button =
        allocate_many_ui_elements_from__ui_manager_in__succession(
                p_ui_manager,
                HUD_QUANTITY_OF__BUTTONS);

    for (Index__u32 index_of__button = 0;
            p_ui_button;
            p_ui_button = get_next__ui_element(p_ui_button),
            index_of__button++) {

        // ***) Initialize as a (non toggleable) button with our
        // custom click handler.
        initialize_ui_element_as__button(
                p_ui_button,
                m_ui_button__clicked_handler__main,
                false, // is_toggleable_or__non_toggleable
                false); // is_toggled_or__not_toggled

        // ***) Give the button a hitbox in the window's (shared)
        // hitbox manager. The hitbox size also defines the
        // button's drawn size in UI tiles (8px each):
        // 48x16 px == 6x2 UI tiles.
        //
        // NOTE the coordinate convention: the hitbox position
        // vector is the ELEMENT'S CENTER in WINDOW-CENTER-
        // RELATIVE coordinates, Y bottom-origin (the same space
        // the SDL platform puts the cursor in, see GL_process_
        // input). So "16px from the left edge, 16px from the top"
        // on a 256x256 window is center-relative
        // (16 + 48/2 - 128, 128 - (16 + 16/2)) = (-88, 104).
        allocate_hitbox_for__ui_element(
                p_game,
                p_gfx_window,
                p_ui_button,
                HUD_BUTTON_WIDTH__PX,
                HUD_BUTTON_HEIGHT__PX,
                get_vector__3i32(
                        HUD_BUTTON_X_START__PX
                            + HUD_BUTTON_X_STRIDE__PX * index_of__button
                            + HUD_BUTTON_WIDTH__PX / 2
                            - (p_gfx_window->width_of__graphics_window__u32 >> 1),
                        (p_gfx_window->height_of__graphics_window__u32 >> 1)
                            - (HUD_BUTTON_Y__PX + HUD_BUTTON_HEIGHT__PX / 2),
                        0));

        // ***) Give the button its visuals: a solid red
        // UI_Tile_Span (corners, edges and fill all RED). The
        // span's tiles are drawn from the window's tile map
        // texture by the default compose handler.
        UI_Tile ui_tile__red = { 0 };
        initialize_ui_tile(
                &ui_tile__red,
                UI_Tile_Kind__RED,
                0);
        UI_Tile_Span ui_tile_span;
        initialize_ui_tile_span(
                &ui_tile_span,
                (UI_Tile[]){
                    ui_tile__red, ui_tile__red, ui_tile__red, ui_tile__red
                },
                (UI_Tile[]){
                    ui_tile__red, ui_tile__red, ui_tile__red, ui_tile__red
                },
                ui_tile__red);
        set_ui_tile_span_of__ui_element(
                p_ui_button,
                &ui_tile_span);
    }

    return true;
}

// ***) The UI window's close function. Invoked by close_ui_window()
// when the scene unloads.
bool f_ui_window__close__main(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Game *p_game,
        UI_Manager *p_ui_manager) {
    (void)p_gfx_context;
    (void)p_gfx_window;
    (void)p_game;
    (void)p_ui_manager;
    return true;
}
