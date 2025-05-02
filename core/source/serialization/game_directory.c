#include "game.h"
#include <serialization/game_directory.h>
#include "core_string.h"
#include "platform_defines.h"
#include <unistd.h>

Index__u32 stat_game_data_file(
        Game *p_game,
        char *buffer) {
    Index__u32 index_of__path_append = 0;

    PLATFORM_append_base_directory_to__path(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            buffer, 
            &index_of__path_append);

    buffer[index_of__path_append++] = '/';

    index_of__path_append += 
        strncpy_returns__strlen(
                &buffer[index_of__path_append], 
                "game_data", 
                MAX_LENGTH_OF__IO_PATH
                - index_of__path_append);

    if (access(buffer, F_OK)) {
        return false;
    }
    
    return index_of__path_append;
}

void append_path(
        IO_path p_path,
        IO_path p_appended_path) {
    Index__u32 length_of__path =
        strnlen(p_path, MAX_LENGTH_OF__IO_PATH);
    if (length_of__path >= MAX_LENGTH_OF__IO_PATH)
        return;
    p_path[length_of__path] = PATH_SEPERATOR;

    strncpy(&p_path[length_of__path+1],
            p_appended_path,
            MAX_LENGTH_OF__IO_PATH - length_of__path - 1);
}
