#include "defines_weak.h"
#include "game.h"
#include "platform_defines.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "sdl_defines.h"
#include "serialization/sdl_filesystem_defines.h"
#include "serialization/serialization_request.h"
#include <serialization/sdl_filesystem.h>

PLATFORM_File_System_Context __SDL_file_system_context;

Quantity__u32 PLATFORM_get_base_directory(IO_path path) {
    memset(path, 0, sizeof(IO_path));
    SDL_get_path_to__the_game(path);
    return strnlen(path, MAX_LENGTH_OF__IO_PATH);
}

void PLATFORM_initialize_file_system_context(
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context) {
    for (Index__u16 index_of__serialization_request = 0;
            index_of__serialization_request 
            < MAX_QUANTITY_OF__SERIALIZATION_REQUESTS;
            index_of__serialization_request++) {
        Serialization_Request *p_serialization_request =
            &p_PLATOFRM_file_system_context
            ->SDL_serialization_requests[
                index_of__serialization_request];

        initialize_serialization_request(p_serialization_request);
    }

    SDL_get_path_to__the_game(
            p_PLATOFRM_file_system_context
            ->path_to__base_directory);
    p_PLATOFRM_file_system_context
        ->size_of__path_to__base_directory =
        strnlen(
                p_PLATOFRM_file_system_context->path_to__base_directory,
                MAX_LENGTH_OF__IO_PATH);

    Process *p_serialization_process =
        run_process(
                get_p_process_manager_from__game(p_game),
                m_SDL_process__serialization,
                PROCESS_PRIORITY__0_MAXIMUM,
                PROCESS_FLAG__IS_CRITICAL);
    if (!p_serialization_process) {
        debug_abort("SDL::PLATFORM_initialize_file_system_context, failed to allocate p_serialization_process.");
        return;
    }
}

void PLATFORM_append_base_directory_to__path(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        char *p_c_str_path,
        Index__u32 *p_index_of__path_end) {
    strncpy(
            &p_c_str_path[*p_index_of__path_end],
            p_PLATFORM_file_system_context
            ->path_to__base_directory,
            MAX_LENGTH_OF__IO_PATH);
    *p_index_of__path_end +=
        p_PLATFORM_file_system_context
        ->size_of__path_to__base_directory;
}

Serialization_Request *PLATFORM_allocate_serialization_request(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context) {
    for (Index__u16 index_of__serialization_request = 0;
            index_of__serialization_request 
            < MAX_QUANTITY_OF__SERIALIZATION_REQUESTS;
            index_of__serialization_request++) {
        Serialization_Request *p_serialization_request =
            &p_PLATOFRM_file_system_context
            ->SDL_serialization_requests[
                index_of__serialization_request];

        if (is_serialization_request__active(
                p_serialization_request)) {
            continue;
        }

        set_serialization_request_as__active(
                p_serialization_request);
        return p_serialization_request;
    }
    return 0;
}

void PLATFORM_release_serialization_request(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        Serialization_Request *p_serialization_request) {
#ifndef NDEBUG
    int index = 
        p_serialization_request
        - p_PLATOFRM_file_system_context->SDL_serialization_requests;
    if (index < 0 || index >= MAX_QUANTITY_OF__SERIALIZATION_REQUESTS) {
        debug_abort("SDL::PLATFORM_release_serialization_request, p_serialization_request is not allocated from this PLATFORM_filesystem_context.");
        return;
    }
#endif

    memset(p_serialization_request,
            0,
            sizeof(Serialization_Request));
    set_serialization_request_as__inactive(
            p_serialization_request);
}

enum PLATFORM_Open_File_Error PLATFORM_open_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        const char *p_path,
        const char *p_flags,
        Serialization_Request *p_serialization_request) {
    FILE *p_file = fopen(p_path, p_flags);

    if (!p_file) {
        initialize_serialization_request(p_serialization_request);
        return PLATFORM_Open_File_Error__File_Not_Found;
    }

    p_serialization_request
        ->p_file_handler = p_file;

    return PLATFORM_Open_File_Error__None;
}

void PLATFORM_close_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialization_request) {
    FILE *p_file = (FILE*)p_serialization_request->p_file_handler;

    if (p_file) {
        fclose(p_file);
    }

    deactivate_serialization_request(
            p_PLATFORM_file_system_context,
            p_serialization_request);
}

enum PLATFORM_Write_File_Error PLATFORM_write_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        u8 *source,
        Quantity__u32 length_of__data,
        Quantity__u32 quantity_of__writes,
        void *p_file_handler) {
#ifndef NDEBUG
    if (!p_file_handler) {
        debug_abort("SDL::PLATFORM_write_file, p_file_handler is null.");
        return PLATFORM_Write_File_Error__Unknown;
    }
#endif

    FILE *p_file = p_file_handler;
    Quantity__u32 size_of__write = fwrite(
            source,
            length_of__data,
            quantity_of__writes,
            p_file);

    return PLATFORM_Write_File_Error__None;
}

enum PLATFORM_Read_File_Error PLATFORM_read_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        u8 *destination,
        Quantity__u32 *p_length_of__data_to_read,
        Quantity__u32 quantity_of__reads,
        void *p_file_handler) {
#ifndef NDEBUG
    if (!p_file_handler) {
        debug_abort("SDL::PLATFORM_read_file, p_file_handler is null.");
        return PLATFORM_Read_File_Error__Unknown;
    }
#endif

    FILE *p_file = p_file_handler;
    Quantity__u32 size_of__read = 
        fread(
            destination,
            *p_length_of__data_to_read,
            quantity_of__reads,
            p_file);

    *p_length_of__data_to_read = 
        size_of__read
        * *p_length_of__data_to_read;
    
    if (!*p_length_of__data_to_read)
        return PLATFORM_Read_File_Error__End_Of_File;

    return PLATFORM_Read_File_Error__None;
}

///
/// Returns -1 on error.
///
Index__u32 PLATFORM_get_position_in__file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        void *p_file_handler) {
#ifndef NDEBUG
    if (!p_file_handler) {
        debug_abort("SDL::PLATFORM_read_file, p_file_handler is null.");
        return PLATFORM_Read_File_Error__Unknown;
    }
#endif

    FILE *p_file = p_file_handler;

    return ftell(p_file);
}

bool PLATFORM_set_position_in__file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Index__u32 position_in__file_u32,
        void *p_file_handler) {
#ifndef NDEBUG
    if (!p_file_handler) {
        debug_abort("SDL::PLATFORM_read_file, p_file_handler is null.");
        return PLATFORM_Read_File_Error__Unknown;
    }
#endif

    FILE *p_file = p_file_handler;

    return !fseek(p_file, position_in__file_u32, SEEK_SET);
}

Quantity__u32 PLATFORM_get_quantity_of__active_serialization_requests(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context) {
    Quantity__u32 quantity_of__active_serialization_requests = 0;
    for (Index__u32 index_of__serialization_request = 0;
            index_of__serialization_request
            < MAX_QUANTITY_OF__SERIALIZATION_REQUESTS;
            index_of__serialization_request++ ){
        Serialization_Request *p_serialization_request =
            &p_PLATFORM_file_system_context
            ->SDL_serialization_requests[
                index_of__serialization_request];

        if (is_serialization_request__active(
                    p_serialization_request)) {
            quantity_of__active_serialization_requests++;
        }
    }
    return quantity_of__active_serialization_requests;
}

void m_SDL_process__serialization(
        Process *p_this_process,
        Game *p_game) {
    PLATFORM_File_System_Context *p_PLATFORM_file_system_context =
        get_p_PLATFORM_file_system_context_from__game(p_game);

#ifndef NDEBUG
    if (!p_PLATFORM_file_system_context) {
        debug_error("m_SDL_process__serialization, p_PLATOFRM_file_system_context is null.");
        fail_process(p_this_process);
        return;
    }
#endif

    for (Index__u32 index_of__serialization_request = 0;
            index_of__serialization_request
            < MAX_QUANTITY_OF__SERIALIZATION_REQUESTS;
            index_of__serialization_request++) {
        Serialization_Request *p_serialization_request =
            &p_PLATFORM_file_system_context
            ->SDL_serialization_requests[
                index_of__serialization_request];

        if (!is_serialization_request__allocated(p_serialization_request)) {
            continue;
        }
        if (!is_serialization_request__active(p_serialization_request)) {
            PLATFORM_release_serialization_request(
                    p_PLATFORM_file_system_context, 
                    p_serialization_request);
        }
    }
}
