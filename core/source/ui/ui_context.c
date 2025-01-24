#include "ui/ui_context.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "ui/ui_manager.h"

void initialize_ui_context(UI_Context *p_ui_context) {
    memset(
            p_ui_context,
            0,
            sizeof(UI_Context));
}

UI_Manager *allocate_p_ui_manager_from__ui_context(
        UI_Context *p_ui_context) {
    for (Index__u32 index_of__ui_manager = 0;
            index_of__ui_manager
            < MAX_QUANTITY_OF__UI_MANAGERS;
            index_of__ui_manager++) {
        UI_Manager *p_ui_manager =
            p_ui_context->pM_ui_managers[index_of__ui_manager];
        if (p_ui_manager) {
            continue;
        }

        p_ui_manager =
            malloc(sizeof(UI_Manager));

        initialize_ui_manager(p_ui_manager);

        p_ui_context->pM_ui_managers[index_of__ui_manager] =
            p_ui_manager;

        return p_ui_manager;
    }

    debug_error("allocate_pM_ui_manager_from__ui_context, too many managers allocated.");
    return 0;
}

void release_p_ui_manager_from__ui_context(
        UI_Context *p_ui_context,
        UI_Manager *p_ui_manager) {
    for (Index__u32 index_of__ui_manager = 0;
            index_of__ui_manager
            < MAX_QUANTITY_OF__UI_MANAGERS;
            index_of__ui_manager++) {
        if (p_ui_context->pM_ui_managers[index_of__ui_manager]
                == p_ui_manager) {
            free(p_ui_context->pM_ui_managers[index_of__ui_manager]);
            p_ui_context->pM_ui_managers[index_of__ui_manager] = 0;
            return;
        }
    }

    debug_error("release_p_ui_manager_from__ui_context, ui_manager not allocated from this ui_context.");
}

void register_ui_window__loader_into__ui_context(
        UI_Context *p_ui_context,
        f_UI_Window__Load f_ui_window__load,
        Graphics_Window_Kind the_kind_of__window) {
    // TODO: validate args
#warning validate args
    p_ui_context->F_ui_window__loaders[
        the_kind_of__window] = f_ui_window__load;
}

void register_ui_window__closer_into__ui_context(
        UI_Context *p_ui_context,
        f_UI_Window__Close f_ui_window__close,
        Graphics_Window_Kind the_kind_of__window) {
    // TODO: validate args
#warning validate args
    p_ui_context->F_ui_window__closers[
        the_kind_of__window] = f_ui_window__close;
}

Graphics_Window *open_ui(
        Game *p_game,
        Graphics_Window_Kind the_kind_of__window_to__open) {
    // TODO: validate args
#warning validate args
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);
    
    f_UI_Window__Load f_ui_window__load =
        p_ui_context->F_ui_window__loaders[
            the_kind_of__window_to__open];

    if (!f_ui_window__load) {
        debug_warning("Did you forget to register the window?");
        debug_error("open_ui, f_ui_window__load == 0.");
        return false;
    }

    Graphics_Window *p_graphics_window =
        allocate_graphics_window_with__graphics_window_manager(
                p_gfx_context, 
                get_p_graphics_window_manager_from__gfx_context(
                    p_gfx_context),
                TEXTURE_FLAG__SIZE_256x256);

    if (!p_graphics_window) {
        debug_error("open_ui, p_PLATFORM_gfx_window == 0.");
        return false;
    }

    UI_Manager *p_ui_manager =
        allocate_p_ui_manager_from__ui_context(
                p_ui_context);

    if (!p_ui_manager) {
        debug_error("open_ui, p_ui_manager == 0.");
        release_graphics_window_from__graphics_window_manager(
                p_gfx_context, 
                p_graphics_window);
        return false;
    }

    set_p_ui_manager_of__graphics_window(
            p_graphics_window, 
            p_ui_manager);

    f_ui_window__load(
            p_gfx_context,
            p_graphics_window,
            p_game,
            p_ui_manager);

    return p_graphics_window;
}

void close_ui(
        Game *p_game,
        Graphics_Window_Kind the_kind_of__window_to__close) {
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    // TODO: validate args
#warning validate args
    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);
    
    f_UI_Window__Close f_ui_window__close =
        p_ui_context->F_ui_window__closers[
            the_kind_of__window_to__close];

    if (!f_ui_window__close) {
        debug_warning("Did you forget to register the window?");
        debug_error("close_ui, f_ui_window__close == 0.");
        return;
    }

    Graphics_Window *ptr_array_of__windows[
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS];

    Quantity__u8 quantity_of__graphics_windows =
        get_graphics_windows_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    p_gfx_context),
                &ptr_array_of__windows[0],
                MAX_QUANTITY_OF__GRAPHICS_WINDOWS,
                the_kind_of__window_to__close);

    if (!quantity_of__graphics_windows) {
        return;
    }

    for (Index__u32 index_of__graphics_window = 0;
            index_of__graphics_window 
            < quantity_of__graphics_windows;
            index_of__graphics_window++) {
        Graphics_Window *p_graphics_window =
            ptr_array_of__windows[index_of__graphics_window];
        f_ui_window__close(
                p_gfx_context,
                ptr_array_of__windows[index_of__graphics_window],
                p_game,
                p_graphics_window->p_ui_manager);
        if (is_graphics_window_with__ui_manager(
                    p_graphics_window)) {
            release_p_ui_manager_from__ui_context(
                    get_p_ui_context_from__gfx_context(
                        p_gfx_context), 
                    p_graphics_window->p_ui_manager);
        }
    }
}
