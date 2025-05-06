#include "world/serialization/world_directory.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "platform_defines.h"
#include "serialization/game_directory.h"
#include "serialization/identifiers.h"
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

static inline
void append_hex_value_to__path(
        Index__u32 *p_index_of__path_append,
        u8 hex__u4,
        char *buffer) {
    buffer[(*p_index_of__path_append)++] =
        (hex__u4 < 10)
        ? ('0' + hex__u4)
        : ('a' + (hex__u4-10))
        ;
}

void append_u32_as__hex_to__path(
        Index__u32 *p_index_of__path_append,
        u32 value,
        i32 beginning_index,
        char *buffer) {
    u32 hex__u4;
    Index__u32 index_of__hex = 0;
    for (;
            index_of__hex<(8 - beginning_index);
            index_of__hex++) {
        value <<= 4;
    }
    for (Index__u32 index_of__hex = 0;
            index_of__hex < beginning_index;
            index_of__hex++) {
        hex__u4 = ((MASK(4) << 28) & value) >> 28;
        append_hex_value_to__path(
                p_index_of__path_append, 
                hex__u4, 
                buffer);
        value <<= 4;
    }
}

Index__u32 stat_world_directory(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        IO_path p_path) {
    Index__u32 index_of__path_append = 0;

    PLATFORM_append_base_directory_to__path(
            p_PLATFORM_file_system_context,
            p_path, 
            &index_of__path_append);

    append_path(
            p_path, 
            "save");
    index_of__path_append += sizeof("save");

    PLATFORM_Directory *p_dir = 0;
    if (!(p_dir = PLATFORM_opendir(p_path))) {
        if (PLATFORM_mkdir(p_path, 0777)) {
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }

    p_path[index_of__path_append++] = PATH_SEPERATOR;
    if (index_of__path_append + WORLD_NAME_MAX_SIZE_OF
            >= MAX_LENGTH_OF__IO_PATH) {
        debug_error("stat_world_directory, path too long.");
        return 0;
    }
    strncpy(&p_path[index_of__path_append], 
            p_world->name,
            WORLD_NAME_MAX_SIZE_OF);

    index_of__path_append += 
        p_world->length_of__world_name;

    if (!(p_dir = PLATFORM_opendir(p_path))) {
        if (PLATFORM_mkdir(p_path, 0777)) {
            return 0;
        }
    } else {
        PLATFORM_closedir(p_dir);
    }

    return index_of__path_append;
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

    append_path(
            buffer, 
            "save");
    index_of__path_append += sizeof("save");

    buffer[index_of__path_append++] = PATH_SEPERATOR;

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

    buffer[index_of__path_append++] = PATH_SEPERATOR;
    buffer[index_of__path_append++] = 'r';
    buffer[index_of__path_append++] = '_';
    
    Region_Vector__3i32 region_vector__3i32 =
        get_region_that__this_global_space_is_in(
                p_global_space);

    append_u32_as__hex_to__path(
            &index_of__path_append, 
            region_vector__3i32.x__i32, 
            8,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_u32_as__hex_to__path(
            &index_of__path_append, 
            region_vector__3i32.y__i32, 
            8,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_u32_as__hex_to__path(
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

        buffer[index_of__path_append++] = PATH_SEPERATOR;
        buffer[index_of__path_append++] = 'c';
        buffer[index_of__path_append++] = '_';
        append_u32_as__hex_to__path(
                &index_of__path_append, 
                chunk_vector_descend__3i32.x__i32, 
                2,
                buffer);
        buffer[index_of__path_append++] = '_';
        append_u32_as__hex_to__path(
                &index_of__path_append, 
                chunk_vector_descend__3i32.y__i32, 
                2,
                buffer);
        buffer[index_of__path_append++] = '_';
        append_u32_as__hex_to__path(
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

    buffer[index_of__path_append++] = PATH_SEPERATOR;
    buffer[index_of__path_append++] = 'c';
    buffer[index_of__path_append++] = '_';
    append_u32_as__hex_to__path(
            &index_of__path_append, 
            chunk_vector__3i32.x__i32, 
            2,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_u32_as__hex_to__path(
            &index_of__path_append, 
            chunk_vector__3i32.y__i32, 
            2,
            buffer);
    buffer[index_of__path_append++] = '_';
    append_u32_as__hex_to__path(
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
    buffer[end_of__path] = PATH_SEPERATOR;
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

    append_path(
            buffer, 
            "save");
    index_of__path_append += sizeof("save");

    buffer[index_of__path_append++] = PATH_SEPERATOR;

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

    buffer[index_of__path_append++] = PATH_SEPERATOR;
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

Index__u32 stat_client_file(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        IO_path p_path,
        Identifier__u32 uuid_of__client,
        Index__u32 *p_OUT_index_of__path_to__file_base_directory) {
    *p_OUT_index_of__path_to__file_base_directory = 0;
    if (is_identifier_u32__invalid(
                uuid_of__client)) {
        debug_error("stat_client_file, invalid client uuid.");
        return 0;
    }
    Index__u32 index_of__path_append = 
        stat_world_directory(
                p_PLATFORM_file_system_context, 
                p_world, 
                p_path);
    if (!index_of__path_append) {
        debug_error("stat_client_file, failed to find file of world.");
        return 0;
    }

    Identifier__u32 uuid_of__client__processed = 
        uuid_of__client;
    Identifier__u32 uuid_of__client__processed_mask = 
        (Identifier__u32)-1;
    do {
        Quantity__u8 prefix_of__uuid__u4 = 
            0b1111
            & uuid_of__client__processed;
        p_path[index_of__path_append++] = PATH_SEPERATOR;
        append_hex_value_to__path(
                &index_of__path_append, 
                prefix_of__uuid__u4, 
                p_path);
        PLATFORM_Directory *p_dir;
        if (!(p_dir = PLATFORM_opendir(p_path))) {
            if (PLATFORM_mkdir(p_path, 0777)) {
                return 0;
            }
        } else {
            PLATFORM_closedir(p_dir);
        }
        uuid_of__client__processed_mask >>= 4;
        uuid_of__client__processed >>= 4;
    } while (uuid_of__client__processed_mask > MASK(4));

    *p_OUT_index_of__path_to__file_base_directory =
        index_of__path_append;

    p_path[index_of__path_append++] = PATH_SEPERATOR;
    append_hex_value_to__path(
            &index_of__path_append, 
            uuid_of__client__processed, 
            p_path);

    if (PLATFORM_access(p_path, IO_Access_Kind__File)) {
        return false;
    }

    return index_of__path_append;
}
