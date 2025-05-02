#include "process/filesystem_process.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "process/game_action_process.h"
#include "process/process.h"

void m_process__dispose_handler__filesystem__default(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    if (!p_serialization_request)
        return;

    if (p_serialization_request->p_file_handler) {
        PLATFORM_close_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
    }
    PLATFORM_release_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_serialization_request);
}

void m_process__dispose_handler__filesystem_game_action__default(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    if (!p_serialization_request)
        return;

    Game_Action *p_game_action =
        (Game_Action*)p_serialization_request->p_data;
    if (p_game_action) {
        resolve_game_action(
                p_game, 
                GA_UUID_SOURCE(p_game_action),
                p_game_action);
    }

    if (p_serialization_request->p_file_handler) {
        PLATFORM_close_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
    }
    PLATFORM_release_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_serialization_request);
}

void m_process__dispose_handler__filesystem_client__default(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    if (!p_serialization_request)
        return;

    Game_Action *p_game_action =
        (Game_Action*)p_serialization_request->p_data;
    if (p_game_action) {
        resolve_game_action(
                p_game, 
                GA_UUID_SOURCE(p_game_action),
                p_game_action);
    }

    if (p_serialization_request->p_file_handler) {
        PLATFORM_close_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
    }
    PLATFORM_release_serialization_request(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_serialization_request);
}

void initialize_process_as__filesystem_process(
        Process *p_process,
        Serialization_Request *p_serialization_request,
        void *p_serialization_request__data) {
    p_process->p_process_data =
        p_serialization_request;
    p_serialization_request->p_data =
        p_serialization_request__data;
    set_process__dispose_handler(
            p_process, 
            m_process__dispose_handler__filesystem__default);
}

bool initialize_process_as__filesystem_process__open_file(
        Game *p_game,
        Process *p_process,
        IO_path path_to__file,
        const char *p_file_descriptors,
        void *p_serialization_request__data,
        bool is_accepting__non_existing_file) {

    if (!p_process) {
        debug_error("initialize_process_as__filesystem_process__open_file, p_process == 0.");
        return false;
    }

    Serialization_Request *p_serialization_request =
        PLATFORM_allocate_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(
                    p_game));

    if (!p_serialization_request) {
        debug_error("initialize_process_as__filesystem_process__open_file, failed to allocate serialization request.");
        fail_process(p_process);
        return false;
    }

    PLATFORM_Open_File_Error error = 
        PLATFORM_open_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                path_to__file, 
                p_file_descriptors,
                p_serialization_request);

    switch (error) {
        case PLATFORM_Open_File_Error__File_Not_Found:
            if (is_accepting__non_existing_file)
                break;
        default:
            debug_error("initialize_process_as__filesystem_process__open_file, open file error: %d", error);
            PLATFORM_release_serialization_request(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    p_serialization_request);
            fail_process(p_process);
            return false;
        case PLATFORM_Open_File_Error__None:
            break;
    }

    initialize_process_as__filesystem_process(
            p_process, 
            p_serialization_request,
            p_serialization_request__data);

    return true;
}
