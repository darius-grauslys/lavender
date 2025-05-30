#ifndef WORLD_DIRECTORY_H
#define WORLD_DIRECTORY_H

#include "defines_weak.h"
#include <defines.h>

Index__u32 stat_chunk_directory(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer);

// TODO: rename to just stat_chunk_file
Index__u32 stat_chunk_file__tiles(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer);

///
/// This holds data such as world seed, and player entity data.
///
Index__u32 stat_world_header_file(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        World *p_world,
        char *buffer);

Index__u32 stat_world_directory(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        IO_path p_path);

Index__u32 stat_client_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        IO_path p_path,
        Identifier__u32 uuid_of__client,
        Index__u32 *p_OUT_index_of__path_to__file_base_directory);

// Index__u32 stat_chunk_file__entities(
//         Game *p_game,
//         Chunk_Manager__Chunk_Map_Node *p_chunk_map_node,
//         char *buffer);
// 
// Index__u32 stat_chunk_file__inventories(
//         Game *p_game,
//         Chunk_Manager__Chunk_Map_Node *p_chunk_map_node,
//         char *buffer);

static inline
bool append_chunk_file__tiles_to__path(
        char *buffer,
        Quantity__u16 length_of__path,
        Quantity__u16 max_length_of__path) {
    if (length_of__path + 2 > max_length_of__path)
        return false;

    buffer[length_of__path] = PATH_SEPERATOR;
    buffer[length_of__path+1] = 't';
    return true;
}

// static inline
// bool append_chunk_file__entities_to__path(
//         char *buffer,
//         Quantity__u16 length_of__path,
//         Quantity__u16 max_length_of__path) {
//     if (length_of__path + 2 > max_length_of__path)
//         return false;
// 
//     buffer[length_of__path] = PATH_SEPERATOR[0];
//     buffer[length_of__path+1] = 'e';
//     return true;
// }
// 
// static inline
// bool append_chunk_file__inventories_to__path(
//         char *buffer,
//         Quantity__u16 length_of__path,
//         Quantity__u16 max_length_of__path) {
//     if (length_of__path + 2 > max_length_of__path)
//         return false;
// 
//     buffer[length_of__path] = PATH_SEPERATOR[0];
//     buffer[length_of__path+1] = 'i';
//     return true;
// }

#endif
