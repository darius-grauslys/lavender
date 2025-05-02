#ifndef FILESYSTEM_GAME_ACTION_PROCESS_H
#define FILESYSTEM_GAME_ACTION_PROCESS_H

#include "defines.h"

void initialize_process_as__filesystem_process(
        Process *p_process,
        Serialization_Request *p_serialization_request,
        void *p_serialization_request__data);

///
/// NOTE: process is failed if fail to open file.
/// NOTE: returns true if successful.
/// 
bool initialize_process_as__filesystem_process__open_file(
        Game *p_game,
        Process *p_process,
        IO_path path_to__file,
        const char *p_file_descriptors,
        void *p_serialization_request__data,
        bool is_accepting__non_existing_file);

#endif
