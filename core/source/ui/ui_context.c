#include "ui/ui_context.h"
#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "rendering/gfx_context.h"
#include "rendering/graphics_window.h"
#include "rendering/graphics_window_manager.h"
#include "rendering/sprite_manager.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "types/implemented/graphics_window_kind.h"
#include "ui/ui_manager.h"
#include "ui/ui_window_record.h"
#include <string.h>

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

void initialize_ui_context(UI_Context *p_ui_context) {
    memset(
            p_ui_context,
            0,
            sizeof(UI_Context));
    initialize_serialization_header__contiguous_array(
            (Serialization_Header *)p_ui_context->ui_managers, 
            MAX_QUANTITY_OF__UI_MANAGERS, 
            sizeof(UI_Manager));

}

UI_Manager *allocate_p_ui_manager_from__ui_context(
        UI_Context *p_ui_context,
        Identifier__u32 uuid_of__ui_manager,
        Quantity__u16 max_quantity_of__ui_elements) {
    UI_Manager *p_ui_manager =
        (UI_Manager*)get_next_available__allocation_in__contiguous_array(
                (Serialization_Header*)p_ui_context->ui_managers, 
                MAX_QUANTITY_OF__UI_MANAGERS, 
                uuid_of__ui_manager);

    if (!p_ui_manager) {
        debug_error("allocate_p_ui_manager_from__ui_context, failed to allocate ui manager (maximum reached.)");
        return 0;
    }

    initialize_ui_manager(p_ui_manager);

    if (!allocate_ui_manager__members(
                p_ui_manager,
                max_quantity_of__ui_elements)) {
        debug_error("allocate_p_ui_manager_from__ui_context, failed to allocate ui manager members.");
        return 0;
    }

    ALLOCATE_P(p_ui_manager, uuid_of__ui_manager);
    
    return p_ui_manager;
}

UI_Manager 
*get_p_ui_manager_by__uuid_from__ui_context(
        UI_Context *p_ui_context,
        Identifier__u32 uuid_of__ui_manager__u32) {
    return (UI_Manager*)
        dehash_identitier_u32_in__contigious_array(
            (Serialization_Header *)p_ui_context->ui_managers, 
            MAX_QUANTITY_OF__UI_MANAGERS,
            uuid_of__ui_manager__u32);
}

void release_p_ui_manager_from__ui_context(
        Game *p_game,
        Identifier__u32 uuid_of__ui_manager__u32) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("release_p_ui_manager_from__ui_context, p_game == 0.");
        return;
    }
#endif

    UI_Manager *p_ui_manager =
        get_p_ui_manager_by__uuid_from__ui_context(
                get_p_ui_context_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                uuid_of__ui_manager__u32);

    if (!p_ui_manager) {
        debug_error("release_p_ui_manager_from__ui_context, ui manager was not found.");
        return;
    }

    Graphics_Window *p_graphics_window =
        get_p_graphics_window_by__uuid_from__graphics_window_manager(
                get_p_graphics_window_manager_from__gfx_context(
                    get_p_gfx_context_from__game(p_game)), 
                uuid_of__ui_manager__u32);

    if (!p_graphics_window) {
        // We have to abort here because a memory leak may be occuring.
        debug_abort("release_p_ui_manager_from__ui_context, ui manager is not paired with a graphics_window.");
        return;
    }

    release_all__ui_elements_from__ui_manager(
            p_game, 
            p_graphics_window,
            p_ui_manager);

    release_ui_manager__members(
            p_ui_manager);

    DEALLOCATE_P(p_ui_manager);
}

void register_ui_window_into__ui_context(
        UI_Context *p_ui_context,
        f_UI_Window__Load f_ui_window__load,
        f_UI_Window__Close f_ui_window__close,
        Graphics_Window_Kind the_kind_of__graphics_window,
        Signed_Quantity__i32 signed_quantity_of__sprites,
        Signed_Quantity__i16 signed_quantity_of__ui_elements) {
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
    p_ui_window_record->signed_quantity_of__sprites = 
        signed_quantity_of__sprites;
    p_ui_window_record->signed_quantity_of__ui_elements =
        signed_quantity_of__ui_elements;
}

Graphics_Window *_open_ui_window(
        Game *p_game,
        Graphics_Window_Kind the_kind_of__graphics_window_to__open,
        Identifier__u32 uuid_of__graphics_window__u32,
        Identifier__u32 uuid_of__parent_for__graphics_window__u32,
        Index__u16 index_of__ui_element_offset__u16) {
#ifndef NDEBUG
    if (!p_game) {
        debug_error("_open_ui_window, p_game == 0.");
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
        debug_error("_open_ui_window, p_ui_window_record == 0.");
        return false;
    }

    if (!is_ui_window_record__valid(p_ui_window_record)) {
        debug_warning("Did you forget to register the ui window?");
        debug_error("_open_ui_window, p_ui_window_record is invalid.");
        return false;
    }

    Graphics_Window *p_graphics_window = 0;
    if (is_identifier_u32__invalid(uuid_of__graphics_window__u32)) {
        p_graphics_window =
            allocate_graphics_window_from__graphics_window_manager(
                    p_gfx_context, 
                    get_p_graphics_window_manager_from__gfx_context(
                        p_gfx_context),
                    TEXTURE_FLAG__SIZE_256x256);
    } else {
        p_graphics_window =
            allocate_graphics_window_with__uuid_from__graphics_window_manager(
                    p_gfx_context, 
                    get_p_graphics_window_manager_from__gfx_context(
                        p_gfx_context),
                    uuid_of__graphics_window__u32,
                    TEXTURE_FLAG__SIZE_256x256);
    }

    if (!p_graphics_window) {
        debug_error("_open_ui_window, p_PLATFORM_gfx_window == 0.");
        return false;
    }

    p_graphics_window->graphics_window__parent__uuid =
        uuid_of__parent_for__graphics_window__u32;

    if (p_ui_window_record->signed_quantity_of__sprites < 0) {
        p_graphics_window->graphics_window__sprite_manager__allocation_scheme =
            Graphics_Window__Sprite_Manager__Allocation_Scheme__Is_Using_Parent_Pool;
    } else if (p_ui_window_record->signed_quantity_of__sprites == 0) {
        p_graphics_window->graphics_window__sprite_manager__allocation_scheme =
            Graphics_Window__Sprite_Manager__Allocation_Scheme__None;
    } else {
        p_graphics_window->graphics_window__sprite_manager__allocation_scheme =
            Graphics_Window__Sprite_Manager__Allocation_Scheme__Is_Allocating;
    }

    Sprite_Manager *p_sprite_manager = 0;
    switch (p_graphics_window->graphics_window__sprite_manager__allocation_scheme) {
        default:
            // TODO: add parent usage case and ensure there is available room.
            break;
        case Graphics_Window__Sprite_Manager__Allocation_Scheme__Is_Allocating:
            ;
            // Use the sprite pool of the parent window.
            // TODO: check all other children of the parent and see if the abs(sprite_quant) sum of
            // TODO: all negative quantities of children exceed the parent maximum.
            // 
            // TODO: also, maybe FORCE child windows to use parent sprite pool UNLESS maximum is exceeded.
            p_sprite_manager =
                allocate_sprite_manager_from__sprite_context(
                        get_p_sprite_context_from__gfx_context(p_gfx_context),
                        GET_UUID_P(p_graphics_window),
                        p_ui_window_record->signed_quantity_of__sprites);
            if (!p_sprite_manager) {
                debug_error("_open_ui_window, p_sprite_manager == 0.");
                release_graphics_window_from__graphics_window_manager(
                        p_game, 
                        p_graphics_window);
                return false;
            }
            break;
    }

    if (p_ui_window_record->signed_quantity_of__ui_elements < 0) {
        p_graphics_window->graphics_window__ui_manager__allocation_scheme =
            Graphics_Window__UI_Manager__Allocation_Scheme__Is_Using_Parent_Pool;
    } else if (p_ui_window_record->signed_quantity_of__ui_elements == 0) {
        p_graphics_window->graphics_window__ui_manager__allocation_scheme =
            Graphics_Window__UI_Manager__Allocation_Scheme__None;
    } else {
        p_graphics_window->graphics_window__ui_manager__allocation_scheme =
            Graphics_Window__UI_Manager__Allocation_Scheme__Is_Allocating;
    }

    UI_Manager *p_ui_manager = 0;
    switch (p_graphics_window->graphics_window__ui_manager__allocation_scheme) {
        default:
            break;
        case Graphics_Window__UI_Manager__Allocation_Scheme__Is_Using_Parent_Pool:
            // TODO: add parent usage case and ensure there is available room.
            p_ui_manager = 
                get_p_ui_manager_by__uuid_from__ui_context(
                        get_p_ui_context_from__gfx_context(p_gfx_context), 
                        p_graphics_window->graphics_window__parent__uuid);
            break;
        case Graphics_Window__UI_Manager__Allocation_Scheme__Is_Allocating:
            p_ui_manager = 
                allocate_p_ui_manager_from__ui_context(
                    p_ui_context,
                    GET_UUID_P(p_graphics_window),
                    p_ui_window_record->signed_quantity_of__ui_elements);

            if (!p_ui_manager) {
                debug_error("_open_ui_window, p_ui_manager == 0.");
                release_graphics_window_from__graphics_window_manager(
                        p_game,
                        p_graphics_window);
                return false;
            }

            break;
    }

    p_ui_window_record->f_ui_window__load(
            p_gfx_context,
            p_graphics_window,
            p_game,
            p_ui_manager,
            index_of__ui_element_offset__u16);

    set_graphics_window_as__enabled(p_graphics_window);
    set_graphics_window_as__in_need_of__composition(
            p_graphics_window);

    return p_graphics_window;
}

Graphics_Window *open_ui_window_with__this_uuid_and__parent_uuid(
        Game *p_game,
        Graphics_Window_Kind the_kind_of__graphics_window_to__open,
        Identifier__u32 uuid_of__graphics_window__u32,
        Identifier__u32 uuid_of__parent_for__graphics_window__u32) {
    return _open_ui_window(
            p_game, 
            the_kind_of__graphics_window_to__open, 
            uuid_of__graphics_window__u32, 
            uuid_of__parent_for__graphics_window__u32,
            0);
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
                p_game,
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

    release_graphics_window_from__graphics_window_manager(
            p_game, 
            p_graphics_window);
}
