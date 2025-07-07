#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "inventory/inventory.h"
#include "inventory/inventory_manager.h"
#include "platform.h"
#include "platform_defines.h"
#include "serialization/serialized_field.h"
#include "serialization/serialization_header.h"
#include "vectors.h"
#include "world/global_space.h"
#include "world/tile.h"
#include <world/chunk.h>
#include "process/process.h"
#include "process/process_manager.h"

void initialize_chunk(
        Chunk *p_chunk,
        Identifier__u64 uuid__u64) {
    memset(p_chunk,0,sizeof(Chunk));
    initialize_serialization_header__uuid_64(
            &p_chunk->_serialization_header, 
            uuid__u64,
            sizeof(Chunk));
}

void m_process__serialize_chunk(
        Process *p_this_process,
        Game *p_game) {

    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process
        ->p_process_data;

    Global_Space *p_global_space = 
        p_serialization_request->p_data;

    if (!p_global_space) {
        debug_error("m_process__serialize_chunk [%p], p_global_space == 0.",
                p_this_process);
        fail_process(p_this_process);
        return;
    }

    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);

    if (!p_chunk) {
        fail_process(p_this_process);
        return;
    }

    void *p_file_handler =
        p_serialization_request
        ->p_file_handler;

    enum PLATFORM_Write_File_Error error = 
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)p_chunk->tiles, 
                sizeof(p_chunk->tiles), 
                1, 
                p_file_handler);

    if (!error) {
        complete_process(p_this_process);
        return;
    }

    debug_error("m_proces__serialize_chunk, failed error: %d", error);
    set_chunk_as__inactive(p_chunk);
    set_chunk_as__visually_updated(p_chunk);
    fail_process(p_this_process);
}

void m_process__deserialize_chunk(
        Process *p_this_process,
        Game *p_game) {

    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process
        ->p_process_data;

    Global_Space *p_global_space = 
        p_serialization_request->p_data;

    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);

    if (!p_chunk) {
        fail_process(p_this_process);
        return;
    }

    void *p_file_handler =
        p_serialization_request->p_file_handler;

    Quantity__u32 length_of__read =
        sizeof(p_chunk->tiles);

    enum PLATFORM_Read_File_Error error = 
        PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)p_chunk->tiles, 
                &length_of__read,
                1, 
                p_file_handler);
    if (error) {
        debug_error("m_process__deserialize_chunk, failed error: %d", error);
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        fail_process(p_this_process);
        return;
    }

    if (length_of__read
            != sizeof(p_chunk->tiles)) {
        debug_error("m_process__deserialize_chunk, bad read length: %d/%d", 
                length_of__read,
                sizeof(p_chunk->tiles));
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        fail_process(p_this_process);
        return;
    }

    debug_info__verbose("m_process__deserialize_chunk, finish: %p",
            p_serialization_request);

    set_chunk_as__active(p_chunk);
    complete_process(p_this_process);
}
