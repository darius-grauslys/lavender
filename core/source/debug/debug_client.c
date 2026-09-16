#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/game_action.h"
#include "game_action/game_action_logic_table.h"
#include "game_action/game_action_manager.h"
#include "platform_defines.h"
#include "vectors.h"
#include <debug/debug_client.h>

DEBUG_Client_Scanner __DEBUG_client_scanner = {0};

///
/// Returns false if the client pointer was moved.
/// Precondition: __DEBUG_scene_scanner.p_game != 0
///
bool __debug_resolve_tracked_client_in__scanner() {
    Game *p_game =
        __DEBUG_client_scanner.p_game;

    if (__DEBUG_client_scanner.p_client__current) {
        Index__u32 index_of__p_client =
            __DEBUG_client_scanner
            .p_client__current
            - p_game
            ->pM_clients
            ;
        if (index_of__p_client
                >= MAX_QUANTITY_OF__CLIENTS) {
            // TODO: warn about corrupt memory
            debug_warning("[DEBUG] __debug_resolve_tracked_client_in__scanner, p_client out of bounds.");
            debug_warning("[DEBUG] moving pointer to start of bounds.");
            debug_warning("[DEBUG] memory might be corrupt!");
            __DEBUG_client_scanner.p_client__current =
                &p_game
                ->pM_clients[0];
            return true;
        }
    } 

    if (!__DEBUG_client_scanner.p_client__current) {
        __DEBUG_client_scanner.p_client__current =
            &p_game
            ->pM_clients[0]
            ;
        return true;
    }
}

bool __resolve_game_action__with_respect_to__game_action_manager(
        Game_Action **p_ptr_game_action,
        Game_Action_Manager *p_game_action_manager) {
    Index__u32 index_of__inbound_game_action =
        *p_ptr_game_action
        - p_game_action_manager
        ->game_actions
        ;
   
    if (index_of__inbound_game_action
            >= MAX_QUANTITY_OF__GAME_ACTIONS) {
        debug_warning("__resolve_game_action__with_respect_to__game_action_manager, p_ptr_game_action out of bounds.");
        debug_warning("Resetting point to start of game_action manager.");
        debug_warning("Memory might be corrupted!");
        *p_ptr_game_action =
            p_game_action_manager
            ->game_actions
            ;
        return false;
    }

    return true;
}

DEBUG_Client_Scanner __m_debug_client_scanner__refresh() {
    Game *p_game =
        __DEBUG_client_scanner.p_game;
    if (!p_game) {
        debug_warning("[DEBUG] __m_debug_client_scanner__refresh, must call debug_get_client_scanner at least once.");
        goto exit;
    }

    __debug_resolve_tracked_client_in__scanner();

    __DEBUG_client_scanner.quantity_of__clients =
        get_quantity_of__clients_connect_to__game(p_game);

    Client *p_client = __DEBUG_client_scanner.p_client__current;

    if (!p_client) {
        __DEBUG_client_scanner.uuid_of__client__current =
            IDENTIFIER__UNKNOWN__u32;
        __DEBUG_client_scanner.p_game_action__inbound__current = 0;
        __DEBUG_client_scanner.p_game_action__outbound__current = 0;
        memset(&__DEBUG_client_scanner.game_actions,
                0,
                sizeof(__DEBUG_client_scanner.game_actions));
        __DEBUG_client_scanner.current_client__local_space__center__3i32 =
            VECTOR__3i32__OUT_OF_BOUNDS;
        __DEBUG_client_scanner.current_client__client_flags__u16 =
            CLIENT_FLAGS__NONE;
    } else {
        __DEBUG_client_scanner.uuid_of__client__current =
            GET_UUID_P(p_client);
        __DEBUG_client_scanner.current_client__client_flags__u16 =
            p_client->client_flags__u16;
        __DEBUG_client_scanner.current_client__local_space__center__3i32 =
            p_client->local_space_manager
            .center_of__local_space_manager__3i32;

        if (!__resolve_game_action__with_respect_to__game_action_manager(
                    &__DEBUG_client_scanner.p_game_action__inbound__current, 
                    &__DEBUG_client_scanner.p_client__current
                    ->game_action_manager__inbound)) {
            debug_warning("__m_debug_client_scanner__refresh, resolution error on inbound game_action manager.");
        }

        if (!__resolve_game_action__with_respect_to__game_action_manager(
                    &__DEBUG_client_scanner.p_game_action__outbound__current, 
                    &__DEBUG_client_scanner.p_client__current
                    ->game_action_manager__outbound)) {
            debug_warning("__m_debug_client_scanner__refresh, resolution error on outbound game_action manager.");
        }

        if (__DEBUG_client_scanner.p_game_action__inbound__current
                && is_game_action__allocated(
                    __DEBUG_client_scanner.p_game_action__inbound__current)) {
            __DEBUG_client_scanner.game_actions
                .game_action_header__inbound__current =
                __DEBUG_client_scanner.p_game_action__inbound__current
                ->_game_action_header;
            __DEBUG_client_scanner.game_actions
                .quantity_of__game_actions__inbound =
                get_quantity_of__game_actions_in__game_action_manager(
                        &__DEBUG_client_scanner
                        .p_client__current->game_action_manager__inbound);
            Game_Action_Logic_Entry *p_game_action_logic_entry__inbound =
                get_p_game_action_logic_entry_by__game_action_kind(
                        get_p_game_action_logic_table_from__game(p_game), 
                        __DEBUG_client_scanner
                        .p_game_action__inbound__current
                        ->the_kind_of_game_action__this_action_is);

            if (!p_game_action_logic_entry__inbound) {
                memset(&__DEBUG_client_scanner.game_actions
                        .game_action_logic_entry__inbound__current,
                        0,
                        sizeof(__DEBUG_client_scanner
                            .game_actions
                            .game_action_logic_entry__inbound__current));
            } else {
                __DEBUG_client_scanner.game_actions
                    .game_action_logic_entry__inbound__current =
                    *p_game_action_logic_entry__inbound;
            }
        } else {
            memset(&__DEBUG_client_scanner
                    .game_actions
                    .game_action_header__inbound__current,
                    0,
                    sizeof(__DEBUG_client_scanner
                        .game_actions
                        .game_action_header__inbound__current));
            memset(&__DEBUG_client_scanner
                    .game_actions
                    .game_action_logic_entry__inbound__current,
                    0,
                    sizeof(__DEBUG_client_scanner
                        .game_actions
                        .game_action_logic_entry__inbound__current));
        }

        if (__DEBUG_client_scanner.p_game_action__outbound__current
                && is_game_action__allocated(
                    __DEBUG_client_scanner.p_game_action__outbound__current)) {
            __DEBUG_client_scanner.game_actions
                .game_action_header__outbound__current =
                __DEBUG_client_scanner.p_game_action__outbound__current
                ->_game_action_header;
            __DEBUG_client_scanner.game_actions
                .quantity_of__game_actions__outbound =
                get_quantity_of__game_actions_in__game_action_manager(
                        &__DEBUG_client_scanner
                        .p_client__current->game_action_manager__outbound);
            Game_Action_Logic_Entry *p_game_action_logic_entry__outbound =
                get_p_game_action_logic_entry_by__game_action_kind(
                        get_p_game_action_logic_table_from__game(p_game), 
                        __DEBUG_client_scanner
                        .p_game_action__outbound__current
                        ->the_kind_of_game_action__this_action_is);

            if (!p_game_action_logic_entry__outbound) {
                memset(&__DEBUG_client_scanner.game_actions
                        .game_action_logic_entry__outbound__current,
                        0,
                        sizeof(__DEBUG_client_scanner
                            .game_actions
                            .game_action_logic_entry__outbound__current));
            } else {
                __DEBUG_client_scanner.game_actions
                    .game_action_logic_entry__outbound__current =
                    *p_game_action_logic_entry__outbound;
            }
        } else {
            memset(&__DEBUG_client_scanner
                    .game_actions
                    .game_action_header__outbound__current,
                    0,
                    sizeof(__DEBUG_client_scanner
                        .game_actions
                        .game_action_header__outbound__current));
            memset(&__DEBUG_client_scanner
                    .game_actions
                    .game_action_logic_entry__outbound__current,
                    0,
                    sizeof(__DEBUG_client_scanner
                        .game_actions
                        .game_action_logic_entry__outbound__current));
        }
    }
exit:
    // Module post condition is inforced here.
    return __DEBUG_client_scanner;
}

DEBUG_Client_Scanner __m_debug_client_scanner__next_client() {
    if (!__DEBUG_client_scanner.p_game) {
        debug_warning("[DEBUG] __m_debug_client_scanner__next_client, must call debug_get_client_scanner at least once.");
        goto exit;
    }

    __debug_resolve_tracked_client_in__scanner();

    Index__u32 index_of__client =
        __DEBUG_client_scanner.p_client__current
        - __DEBUG_client_scanner.p_game->pM_clients;
    if (index_of__client >= MAX_QUANTITY_OF__CLIENTS) {
        __DEBUG_client_scanner.p_client__current = 
            &__DEBUG_client_scanner
            .p_game
            ->pM_clients[0];
        debug_warning("[DEBUG] __m_debug_client_scanner__next_client, client pointer out of bounds.");
        debug_warning("[DEBUG] memory might be corrupted!");
        goto exit;
    }

    index_of__client = (index_of__client+1) % MAX_QUANTITY_OF__CLIENTS;
    __DEBUG_client_scanner.p_client__current =
        get_p_client_by__index_from__game(
                __DEBUG_client_scanner.p_game, 
                index_of__client);
exit:
    __m_debug_client_scanner__refresh(); // Module post condition
    return __DEBUG_client_scanner;
}

Game_Action *__debug_resolve_next_game_action(
        Game_Action **p_ptr_game_action,
        Game_Action_Manager *p_game_action_manager) {
    __debug_resolve_tracked_client_in__scanner();
    if (!__resolve_game_action__with_respect_to__game_action_manager(
            p_ptr_game_action,
            p_game_action_manager)) {
        debug_warning("__debug_resolve_next_game_action, game_action resolution failure.");
    }

    Index__u32 index_of__game_action__u32 =
        *p_ptr_game_action
        - p_game_action_manager
        ->game_actions
        ;

    Game_Action *p_game_action = 0;
    for (Index__u32 offset_of__game_action__u32 = 1;
            offset_of__game_action__u32 < MAX_QUANTITY_OF__GAME_ACTIONS-1;
            offset_of__game_action__u32++) {
        Index__u32 normalized_index = 
            (index_of__game_action__u32
            + offset_of__game_action__u32)
            % MAX_QUANTITY_OF__GAME_ACTIONS
            ;
        p_game_action = 
            &p_game_action_manager
            ->game_actions[normalized_index]
            ;
        if (p_game_action && is_game_action__allocated(p_game_action)) {
            break;
        }
    }

    if (!p_game_action) {
        p_game_action =
            *p_ptr_game_action;
    }

    return p_game_action;
}

DEBUG_Client_Scanner __m_debug_client_scanner__next_game_action__inbound() {
    if (!__DEBUG_client_scanner.p_game) {
        debug_warning("[DEBUG] __m_debug_client_scanner__next_game_action__inbound, must call debug_get_client_scanner at least once.");
        goto exit;
    }

    Game_Action *p_game_action =
        __debug_resolve_next_game_action(
                &__DEBUG_client_scanner
                .p_game_action__inbound__current, 
                &__DEBUG_client_scanner
                .p_client__current
                ->game_action_manager__inbound);

    __DEBUG_client_scanner.p_game_action__inbound__current =
        p_game_action;
exit:
    __m_debug_client_scanner__refresh(); // Module post condition
    return __DEBUG_client_scanner;
}

DEBUG_Client_Scanner __m_debug_client_scanner__next_game_action__outbound() {
    if (!__DEBUG_client_scanner.p_game) {
        debug_warning("[DEBUG] __m_debug_client_scanner__next_game_action__outbound, must call debug_get_client_scanner at least once.");
        goto exit;
    }

    Game_Action *p_game_action =
        __debug_resolve_next_game_action(
                &__DEBUG_client_scanner
                .p_game_action__outbound__current, 
                &__DEBUG_client_scanner
                .p_client__current
                ->game_action_manager__outbound);

    __DEBUG_client_scanner.p_game_action__outbound__current =
        p_game_action;
exit:
    __m_debug_client_scanner__refresh(); // Module post condition
    return __DEBUG_client_scanner;
}

DEBUG_Client_Scanner debug_get_client_scanner(Game *p_game) {
    if (!get_p_world_from__game(p_game)) {
        debug_warning("[DEBUG] debug_get_client_scanner, p_world == 0.");
        debug_warning("[DEBUG] cannot acquire p_client_manager.");
        debug_info("[DEBUG] is a world loaded?");
        goto error;
    }

    __DEBUG_client_scanner.p_game = p_game;
    __DEBUG_client_scanner.p_client__current = p_game->pM_clients;
    __DEBUG_client_scanner.m_refresh = __m_debug_client_scanner__refresh;
    __DEBUG_client_scanner.m_next_client = __m_debug_client_scanner__next_client;
    __DEBUG_client_scanner.m_next_game_action__inbound = __m_debug_client_scanner__next_game_action__inbound;
    __DEBUG_client_scanner.m_next_game_action__outbound = __m_debug_client_scanner__next_game_action__outbound;

    if (__DEBUG_client_scanner.p_client__current) {
        __DEBUG_client_scanner.p_game_action__inbound__current =
            &__DEBUG_client_scanner.p_client__current
            ->game_action_manager__inbound
            .game_actions[MAX_QUANTITY_OF__GAME_ACTIONS-1]
            ;
        __DEBUG_client_scanner.p_game_action__outbound__current =
            &__DEBUG_client_scanner.p_client__current
            ->game_action_manager__outbound
            .game_actions[MAX_QUANTITY_OF__GAME_ACTIONS-1]
            ;
        __m_debug_client_scanner__next_game_action__inbound();
        __m_debug_client_scanner__next_game_action__outbound();
    }

exit:
    __m_debug_client_scanner__refresh(); // Module post condition
    return __DEBUG_client_scanner;
error:
    return (DEBUG_Client_Scanner){0};
}
