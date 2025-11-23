#include "ui/ui_context.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "serialization/serialization_header.h"
#include "types/implemented/graphics_window_kind.h"
#include "ui/ui_manager.h"

static inline
UI_Window_Record *get_p_ui_window_record_from__ui_context(
        UI_Context *p_ui_context,
        Graphics_Window_Kind the_kind_of__graphics_window) {
    if ((u32)the_kind_of__graphics_window>= Graphics_Window_Kind__Unknown) {
        debug_error("get_p_ui_window_record_from__ui_context, the_kind_of__graphics_window >= Graphics_Window_Kind__Unknown");
        return 0;
    }
    return &p_ui_context->ui_window_record[the_kind_of__graphics_window];
}

static inline
bool is_ui_window_record__valid(
        UI_Window_Record *p_ui_window_record) {
    return p_ui_window_record->f_ui_window__load 
        && p_ui_window_record->f_ui_window__close;
}

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
        p_ui_manager->ui_manager__allocation_index =
            index_of__ui_manager;

        p_ui_context->pM_ui_managers[index_of__ui_manager] =
            p_ui_manager;

        return p_ui_manager;
    }

    debug_error("allocate_pM_ui_manager_from__ui_context, too many managers allocated.");
    return 0;
}

void release_p_ui_manager_from__ui_context(
        Game *p_game,
        UI_Context *p_ui_context,
        Graphics_Window *p_graphics_window,
        UI_Manager *p_ui_manager) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("release_p_ui_manager_from__ui_context, p_game == 0.");
        return;
    }
    if (!p_ui_context) {
        debug_error("release_p_ui_manager_from__ui_context, p_ui_context == 0.");
        return;
    }
    if (!p_graphics_window) {
        debug_error("release_p_ui_manager_from__ui_context, p_graphics_window == 0.");
        return;
    }
    if (!p_ui_manager) {
        debug_error("release_p_ui_manager_from__ui_context, p_ui_manager == 0.");
        return;
    }
    if (p_ui_manager != get_p_ui_manager_from__graphics_window(
                p_graphics_window)) {
        debug_error("release_p_ui_manager_from__ui_context, p_ui_manager is not owned by this graphics window");
        return;
    }
#endif

    for (Index__u32 index_of__ui_manager = 0;
            index_of__ui_manager
            < MAX_QUANTITY_OF__UI_MANAGERS;
            index_of__ui_manager++) {
        if (p_ui_context->pM_ui_managers[index_of__ui_manager]
                == p_ui_manager) {
            release_all__ui_elements_from__ui_manager(
                    p_game, 
                    p_graphics_window, 
                    p_ui_manager);
            DEALLOCATE_P(p_ui_context->pM_ui_managers[index_of__ui_manager]);
            free(p_ui_context->pM_ui_managers[index_of__ui_manager]);
            p_ui_context->pM_ui_managers[index_of__ui_manager] = 0;
            return;
        }
    }

    debug_error("release_p_ui_manager_from__ui_context, ui_manager not allocated from this ui_context.");
}

void register_ui_window_into__ui_context(
        UI_Context *p_ui_context,
        f_UI_Window__Load f_ui_window__load,
        f_UI_Window__Close f_ui_window__close,
        Graphics_Window_Kind the_kind_of__graphics_window) {
#ifndef NDEBUG
    if (!p_ui_context) {
        debug_error("register_ui_window_into__ui_context, p_ui_context == 0.");
        return;
    }
    if (!f_ui_window__load) {
        debug_error("register_ui_window_into__ui_context, f_ui_window__load == 0.");
        return;
    }
#endif
    UI_Window_Record *p_ui_window_record =
        get_p_ui_window_record_from__ui_context(
                p_ui_context, 
                the_kind_of__graphics_window);
    if (!p_ui_window_record) {
        debug_error("register_ui_window_into__ui_context, p_ui_window_record == 0.");
        return;
    }

    p_ui_window_record->f_ui_window__load = f_ui_window__load;
    p_ui_window_record->f_ui_window__close = f_ui_window__close;
}

Graphics_Window *open_ui_window(
        Game *p_game,
        Sprite_Manager *p_OPTIONAL_sprite_manager,
        Graphics_Window_Kind the_kind_of__graphics_window_to__open) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("open_ui_window, p_game == 0.");
        return 0;
    }
#endif

    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);
    
    UI_Window_Record *p_ui_window_record =
        get_p_ui_window_record_from__ui_context(
                p_ui_context, 
                the_kind_of__graphics_window_to__open);

    if (!p_ui_window_record) {
        debug_error("open_ui_window, p_ui_window_record == 0.");
        return false;
    }

    if (!is_ui_window_record__valid(p_ui_window_record)) {
        debug_warning("Did you forget to register the ui window?");
        debug_error("open_ui_window, p_ui_window_record is invalid.");
        return false;
    }

    Graphics_Window *p_graphics_window =
        allocate_graphics_window_from__graphics_window_manager(
                p_gfx_context, 
                get_p_graphics_window_manager_from__gfx_context(
                    p_gfx_context),
                TEXTURE_FLAG__SIZE_256x256);

    if (!p_graphics_window) {
        debug_error("open_ui_window, p_PLATFORM_gfx_window == 0.");
        return false;
    }
    
    if (p_OPTIONAL_sprite_manager) {
        share_sprite_manager_with__graphics_window(
                p_graphics_window, 
                p_OPTIONAL_sprite_manager);
    } else {
        Sprite_Manager *p_sprite_manager =
            allocate_sprite_manager_from__gfx_context(
                    p_gfx_context, 
                    p_graphics_window);
        if (!p_sprite_manager) {
            debug_error("open_ui_window, p_sprite_manager == 0.");
            release_graphics_window_from__graphics_window_manager(
                    p_game, 
                    p_graphics_window);
            return false;
        }
    }

    UI_Manager *p_ui_manager =
        allocate_p_ui_manager_from__ui_context(
                p_ui_context);

    if (!p_ui_manager) {
        debug_error("open_ui_window, p_ui_manager == 0.");
        release_graphics_window_from__graphics_window_manager(
                p_game,
                p_graphics_window);
        return false;
    }

    set_p_ui_manager_of__graphics_window(
            p_graphics_window, 
            p_ui_manager);

    p_ui_window_record->f_ui_window__load(
            p_gfx_context,
            p_graphics_window,
            p_game,
            p_ui_manager);

    set_graphics_window_as__enabled(p_graphics_window);
    set_graphics_window_as__in_need_of__composition(
            p_graphics_window);

    return p_graphics_window;
}

void close_ui_window(
        Game *p_game,
        Identifier__u32 uuid_of__graphics_window) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("close_ui, p_game == 0.");
        return;
    }
#endif
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);

    UI_Context *p_ui_context =
        get_p_ui_context_from__gfx_context(p_gfx_context);

    Graphics_Window *ptr_array_of__windows[
        MAX_QUANTITY_OF__GRAPHICS_WINDOWS];

    Graphics_Window *p_graphics_window =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    p_gfx_context),
                uuid_of__graphics_window);

    if (!p_graphics_window) {
        debug_error("close_ui_window, p_graphics_window == 0.");
        return;
    }

    UI_Manager *p_ui_manager =
        get_p_ui_manager_from__graphics_window(
                p_graphics_window);

    if (!p_ui_manager) {
        debug_error("close_ui_window, p_graphics_window lacks ui_manager.");
        return;
    }

    Graphics_Window_Kind the_kind_of__graphics_window =
        get_kind_of__p_graphics_window(p_graphics_window);

    UI_Window_Record *p_ui_window_record =
        get_p_ui_window_record_from__ui_context(
                p_ui_context, 
                the_kind_of__graphics_window);

    if (!p_ui_window_record) {
        debug_error("close_ui_window, p_ui_window_record == 0.");
        return;
    }

    if (!is_ui_window_record__valid(p_ui_window_record)) {
        debug_warning("Did you forget to register the ui window?");
        debug_error("close_ui_window, p_ui_window_record is invalid.");
        return;
    }

    p_ui_window_record->f_ui_window__close(
            p_gfx_context,
            p_graphics_window,
            p_game,
            p_ui_manager);

    // TODO: ensure that window is deallocated?
}
