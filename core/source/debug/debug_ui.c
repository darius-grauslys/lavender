#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "rendering/gfx_context.h"
#include "serialization/serialization_header.h"
#include "ui/ui_manager.h"
#include <debug/debug_ui.h>

DEBUG_UI_Scanner __DEBUG_ui_scanner = {0};

DEBUG_UI_Scanner __m_debug_ui_scanner__next_ui_manager() {
    if (!__DEBUG_ui_scanner.p_ui_context) {
        debug_warning("[DEBUG] __m_debug_ui_scanner__next_ui_manager, must call debug_get_ui_scanner at least once.");
        goto exit;
    }

    Index__u32 index_of__ui_manager = 
        __DEBUG_ui_scanner.p_ui_manager__current
        - __DEBUG_ui_scanner
        .p_ui_context
        ->ui_managers
        ;

    __DEBUG_ui_scanner.p_ptr_ui_element__current = 0;

    if (index_of__ui_manager >= MAX_QUANTITY_OF__UI_MANAGERS) {
        debug_warning("[DEBUG] __m_debug_ui_scanner__next_ui_manager, p_ui_manager out of bounds.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto exit;
    }

    for (Index__u32 offset_of__ui_manager = 1;
            offset_of__ui_manager < MAX_QUANTITY_OF__UI_MANAGERS;
            offset_of__ui_manager++) {
        Index__u32 index_normalized = 
            (index_of__ui_manager + offset_of__ui_manager)
            % MAX_QUANTITY_OF__UI_MANAGERS
            ;

        if (IS_DEALLOCATED(__DEBUG_ui_scanner.p_ui_context[index_normalized])) {
            continue;
        }

        __DEBUG_ui_scanner.p_ui_manager__current =
            &__DEBUG_ui_scanner
            .p_ui_context
            ->ui_managers[index_normalized]
            ;
        break;
    }

exit:
    return __DEBUG_ui_scanner;
}

DEBUG_UI_Scanner __m_debug_ui_scanner__next_ui_element() {
    if (!__DEBUG_ui_scanner.p_ui_context) {
        debug_warning("[DEBUG] __m_debug_ui_scanner__next_ui_element, must call debug_get_ui_scanner at least once.");
        goto exit;
    }

    Index__u32 index_of__p_ptr = 
        __DEBUG_ui_scanner.p_ptr_ui_element__current
        - __DEBUG_ui_scanner.p_ui_manager__current->pM_ptr_array_of__ui_elements;

    if (index_of__p_ptr >=
            __DEBUG_ui_scanner
            .p_ui_manager__current
            ->max_quantity_of__ui_elements) {
        __DEBUG_ui_scanner.p_ptr_ui_element__current =
            __DEBUG_ui_scanner.p_ui_manager__current->pM_ptr_array_of__ui_elements;

        debug_warning("[DEBUG] __m_debug_ui_scanner__next_ui_element, p_ptr_ui_element__current out of bounds.");
        debug_warning("[DEBUG] recovering to start of ptr array.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto exit;
    }

    index_of__p_ptr = (index_of__p_ptr+1)
        % __DEBUG_ui_scanner
        .p_ui_manager__current
        ->max_quantity_of__ui_elements
        ;

    UI_Element *p_ui_element = __DEBUG_ui_scanner
        .p_ui_manager__current
        ->pM_ptr_array_of__ui_elements[index_of__p_ptr];

    if (!p_ui_element) {
        __DEBUG_ui_scanner.p_ptr_ui_element__current =
            __DEBUG_ui_scanner
            .p_ui_manager__current
            ->pM_ptr_array_of__ui_elements;
    } else {
        __DEBUG_ui_scanner.p_ptr_ui_element__current =
            &__DEBUG_ui_scanner
            .p_ui_manager__current
            ->pM_ptr_array_of__ui_elements[index_of__p_ptr];
    }

exit:
    return __DEBUG_ui_scanner;
}

DEBUG_UI_Scanner debug_get_ui_scanner(Game *p_game) {
    UI_Context *p_ui_context = 
        get_p_ui_context_from__gfx_context(
                get_p_gfx_context_from__game(
                    p_game));
    if (!p_ui_context) {
        debug_warning("[DEBUG] debug_get_ui_scanner, p_ui_context == 0.");
        debug_warning("[DEBUG] cannot acquire p_ui_context.");
        debug_warning("[DEBUG] memory might be corrupted!");
        return (DEBUG_UI_Scanner){0};
    }

    UI_Manager *p_ui_manager = 0;
    for (Index__u32 index_of__ui_manager = 0;
            index_of__ui_manager < MAX_QUANTITY_OF__UI_MANAGERS;
            index_of__ui_manager++) {
        Serialization_Header *p_serialization_header__ui_manager = 
            (Serialization_Header*)&p_ui_context->ui_managers[index_of__ui_manager];
        if (!IS_DEALLOCATED_P(p_serialization_header__ui_manager))
            p_ui_manager = (UI_Manager*)p_serialization_header__ui_manager;
    }

    if (!p_ui_manager) {
        debug_warning("[DEBUG] debug_get_ui_scanner, cannot acquire p_ui_manager.");
        debug_info("[DEBUG] are any ui_managers allocated yet?");
        return (DEBUG_UI_Scanner){0};
    }

    __DEBUG_ui_scanner.p_ui_context = p_ui_context;
    __DEBUG_ui_scanner.p_ui_manager__current = p_ui_manager;
    __DEBUG_ui_scanner.p_ptr_ui_element__current =
        p_ui_manager->pM_ptr_array_of__ui_elements;
    __DEBUG_ui_scanner.m_next_manager = __m_debug_ui_scanner__next_ui_manager;
    __DEBUG_ui_scanner.m_next_element = __m_debug_ui_scanner__next_ui_element;

    return __DEBUG_ui_scanner;
}
