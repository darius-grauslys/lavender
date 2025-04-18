#include "world/serialization/world_directory.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "vectors.h"
#include "world/region.h"
#include "sys/stat.h"
#include "sys/types.h"
#include <string.h>
#include "world/region.h"

const char *_base64_lexicon = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-";

void append_base64_value_to__path(
        Index__u32 *p_index_of__path_append,
        u32 value,
        i32 beginning_index,
        char *buffer) {
    u32 b64;
    Index__u32 index_of__hex = 0;
    for (;
            index_of__hex<(8 - beginning_index);
            index_of__hex++) {
        value <<= 4;
    }
    for (Index__u32 index_of__hex = 0;
            index_of__hex < beginning_index;
            index_of__hex++) {
        b64 = ((MASK(6) << 26) & value) >> 26;
        buffer[(*p_index_of__path_append)++] =
            _base64_lexicon[value];
        value <<= 6;
    }
}

void append_hex_value_to__path(
        Index__u32 *p_index_of__path_append,
        u32 value,
        i32 beginning_index,
        char *buffer) {
    u32 hex;
    Index__u32 index_of__hex = 0;
    for (;
            index_of__hex<(8 - beginning_index);
            index_of__hex++) {
        value <<= 4;
    }
    for (Index__u32 index_of__hex = 0;
            index_of__hex < beginning_index;
            index_of__hex++) {
        hex = ((MASK(4) << 28) & value) >> 28;
        buffer[(*p_index_of__path_append)++] =
            (hex < 10)
            ? ('0' + hex)
            : ('a' + (hex-10))
            ;
        value <<= 4;
    }
}

Index__u32 stat_chunk_directory(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer) {
    // assume buffer is of minimium length:
    // WORLD_NAME_MAX_SIZE_OF + "/r_XXXXXX" + "/c_XXXX" + "/c_X" + "/F\0"
    // == WORLD_NAME_MAX_SIZE_OF + 9 + 7 + 4 + 3
    // == WORLD_NAME_MAX_SIZE_OF + 23

    Index__u32 index_of__path_append = 0;

    PLATFORM_append_base_directory_to__path(
            p_PLATFORM_file_system_context,
            buffer, 
            &index_of__path_append);

    buffer[index_of__path_append++] = PATH_SEPERATOR[0];

    // TODO: bounds check index_of__path_append + WORLD_NAME_MAX_SIZE_OF
    //                      < MAX_LENGTH_OF__IO_PATH
    strncpy(&buffer[index_of__path_append], 
            p_world->name,
            WORLD_NAME_MAX_SIZE_OF);

    index_of__path_append += 
        p_world->length_of__world_name;

    PLATFORM_Directory *p_dir;
    if (!(p_dir = PLATFORM_opendir(buffer))) {
        if (PLATFORM_mkdir(buffer, 0777)) {
            debug_error("stat_chunk_directory, failed default_world");
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }

    buffer[index_of__path_append++] = PATH_SEPERATOR[0];
    buffer[index_of__path_append++] = 'r';
    buffer[index_of__path_append++] = '_';
    
    Region_Vector__3i32 region_vector__3i32 =
        get_region_that__this_global_space_is_in(
                p_global_space);

    append_hex_value_to__path(
            &index_of__path_append, 
            region_vector__3i32.x__i32, 
            8,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_hex_value_to__path(
            &index_of__path_append, 
            region_vector__3i32.y__i32, 
            8,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_hex_value_to__path(
            &index_of__path_append, 
            region_vector__3i32.z__i32, 
            8,
            buffer);

    if (!(p_dir = PLATFORM_opendir(buffer))) {
        if (PLATFORM_mkdir(buffer, 0777)) {
            debug_error("stat_chunk_directory, failed region");
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }
    
    Chunk_Vector__3i32 chunk_vector__3i32 =
        p_global_space->chunk_vector__3i32;
    chunk_vector__3i32.x__i32 &= MASK(8);
    chunk_vector__3i32.y__i32 &= MASK(8);

    Chunk_Vector__3i32 chunk_vector_quad__3i32 =
        get_vector__3i32(128, 128, 128);

    Chunk_Vector__3i32 chunk_vector_descend__3i32 =
        get_vector__3i32(127, 127, 127);

    for(Quantity__u32 level_of__recursion = 0;
            level_of__recursion < 6;
            level_of__recursion++) {
        if (chunk_vector__3i32.x__i32
                > chunk_vector_descend__3i32.x__i32) {
            chunk_vector_descend__3i32.x__i32 +=
                chunk_vector_quad__3i32.x__i32;
        } else {
            chunk_vector_descend__3i32.x__i32 -=
                chunk_vector_quad__3i32.x__i32;
        }
        if (chunk_vector__3i32.y__i32
                > chunk_vector_descend__3i32.y__i32) {
            chunk_vector_descend__3i32.y__i32 +=
                chunk_vector_quad__3i32.y__i32;
        } else {
            chunk_vector_descend__3i32.y__i32 -=
                chunk_vector_quad__3i32.y__i32;
        }

        buffer[index_of__path_append++] = PATH_SEPERATOR[0];
        buffer[index_of__path_append++] = 'c';
        buffer[index_of__path_append++] = '_';
        append_hex_value_to__path(
                &index_of__path_append, 
                chunk_vector_descend__3i32.x__i32, 
                2,
                buffer);
        buffer[index_of__path_append++] = '_';
        append_hex_value_to__path(
                &index_of__path_append, 
                chunk_vector_descend__3i32.y__i32, 
                2,
                buffer);
        buffer[index_of__path_append++] = '_';
        append_hex_value_to__path(
                &index_of__path_append, 
                chunk_vector_descend__3i32.z__i32, 
                2,
                buffer);
        if (!(p_dir = PLATFORM_opendir(buffer))) {
            if (PLATFORM_mkdir(buffer, 0777)) {
            debug_error("stat_chunk_directory, failed recur: %d, %d",
                    chunk_vector_descend__3i32.x__i32,
                    chunk_vector_descend__3i32.y__i32);
                return 0;
            }
        } else {
            PLATFORM_closedir(p_dir);
        }
        chunk_vector_quad__3i32.x__i32 >>= 1;
        chunk_vector_quad__3i32.y__i32 >>= 1;
    }

    buffer[index_of__path_append++] = PATH_SEPERATOR[0];
    buffer[index_of__path_append++] = 'c';
    buffer[index_of__path_append++] = '_';
    append_hex_value_to__path(
            &index_of__path_append, 
            chunk_vector__3i32.x__i32, 
            2,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_hex_value_to__path(
            &index_of__path_append, 
            chunk_vector__3i32.y__i32, 
            2,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_hex_value_to__path(
            &index_of__path_append, 
            chunk_vector__3i32.z__i32, 
            2,
            buffer);
    if (!(p_dir = PLATFORM_opendir(buffer))) {
        if (PLATFORM_mkdir(buffer, 0777)) {
            debug_error("stat_chunk_directory, leaf directory");
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }

    //TODO: recur by Z-axis

    return 
        index_of__path_append;
}

Index__u32 stat_chunk_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer,
        char file_character) {
    Index__u32 end_of__path = 
        stat_chunk_directory(
                p_PLATFORM_file_system_context, 
                p_world,
                p_global_space, 
                buffer);
    if (!end_of__path) {
        debug_abort("stat_chunk_file__tile, directories do not exist: %s",
                buffer);
        return false;
    }
    buffer[end_of__path] = PATH_SEPERATOR[0];
    buffer[end_of__path+1] = file_character;

    if (PLATFORM_access(buffer, IO_Access_Kind__File)) {
        return false;
    }

    return end_of__path+2;
}

Index__u32 stat_world_header_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        char *buffer) {
    Index__u32 index_of__path_append = 0;

    PLATFORM_append_base_directory_to__path(
            p_PLATFORM_file_system_context,
            buffer, 
            &index_of__path_append);

    buffer[index_of__path_append++] = PATH_SEPERATOR[0];

    // TODO: bounds check index_of__path_append + WORLD_NAME_MAX_SIZE_OF
    //                      < MAX_LENGTH_OF__IO_PATH
    strncpy(&buffer[index_of__path_append], 
            p_world->name,
            WORLD_NAME_MAX_SIZE_OF);

    index_of__path_append += 
        p_world->length_of__world_name;

    PLATFORM_Directory *p_dir;
    if (!(p_dir = PLATFORM_opendir(buffer))) {
        if (PLATFORM_mkdir(buffer, 0777)) {
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }

    buffer[index_of__path_append++] = PATH_SEPERATOR[0];
    buffer[index_of__path_append++] = 'h';

    if (PLATFORM_access(buffer, IO_Access_Kind__File)) {
        return false;
    }
    
    return index_of__path_append;
}

Index__u32 stat_chunk_file__tiles(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer) {
    return stat_chunk_file(
            p_PLATFORM_file_system_context,
            p_world,
            p_global_space,
            buffer,
            't');
}

Index__u32 stat_chunk_file__entities(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer) {
    return stat_chunk_file(
            p_PLATFORM_file_system_context,
            p_world,
            p_global_space,
            buffer,
            'e');
}

Index__u32 stat_chunk_file__inventories(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Global_Space *p_global_space,
        char *buffer) {
    return stat_chunk_file(
            p_PLATFORM_file_system_context,
            p_world,
            p_global_space,
            buffer,
            'i');
}
