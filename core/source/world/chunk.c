#include "collisions/collision_manager.h"
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
#include "world/tile.h"
#include <world/chunk.h>
#include "process/process.h"
#include "process/process_manager.h"

void initialize_chunk(Chunk *p_chunk) {
    initialize_serialization_header(
            &p_chunk->_serialization_header, 
            get_uuid__chunk(p_chunk), 
            sizeof(Chunk));
}

typedef enum Process_Sub_State__Chunk_Serialize {
    Sub_State__Chunk_Serialize__Write_Tiles,
    Sub_State__Chunk_Serialize__Write_Inventories,
    Sub_State__Chunk_Serialize__Write_Entities,
    Sub_State__Chunk_Serialize__Finish
} Process_Sub_State__Chunk_Serialize;

void m_process__serialize_chunk(
        Process *p_this_process,
        Game *p_game) {

    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process
        ->p_process_data;

    Chunk *p_chunk = (Chunk*)p_serialization_request
        ->p_data;

    void *p_file_handler =
        p_serialization_request
        ->p_file_handler;

    switch (p_this_process->process_sub_state__u8) {
        default:
            goto serialize_chunk__finish;
        case Sub_State__Chunk_Serialize__Write_Tiles:
            break;
        case Sub_State__Chunk_Serialize__Write_Inventories:
            goto serialize_chunk__inventories;
        case Sub_State__Chunk_Serialize__Write_Entities:
            goto serialize_chunk__entities;
    }

    enum PLATFORM_Write_File_Error error = 
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)p_chunk->tiles, 
                sizeof(p_chunk->tiles), 
                1, 
                p_file_handler);
    if (error) {
        goto serialize_chunk__error;
    }

    set_process__sub_state(
            p_this_process, 
            Sub_State__Chunk_Serialize__Write_Entities);
    return;
serialize_chunk__inventories:
    Process *p_sub_process =
        p_this_process->p_queued_process;

    if (!p_sub_process) {
        p_sub_process = allocate_process_in__process_manager(
                get_p_process_manager_from__game(p_game));
        if (!p_sub_process) {
            // try again later.
            // TODO: increment an error level
            return;
        }
        enqueue_process(
                p_this_process, 
                p_sub_process);
        return;
    }

    Quantity__u8 quantity_of__serialized__containers = 0;

    Index__u32 position_of__container_quantity_in__file =
        PLATFORM_get_position_in__file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_file_handler);

    error = PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game),
            &quantity_of__serialized__containers,
            1,
            1,
            p_file_handler);
    if (error) {
        goto serialize_chunk__error;
    }

    // foreach_p_inventory_container_in__chunk_vector(
    //         get_p_inventory_manager_from__game(p_game), 
    //         p_serialization_request->position_of__serialization_3i32, 
    //         f_foreach_inventory_container__serialize_into__chunk, 
    //         p_game, 
    //         p_sub_process);

    Index__u32 position_of__entity_quantity_in__file =
        PLATFORM_get_position_in__file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_file_handler);

    // error = PLATFORM_write_file(
    //         get_p_PLATFORM_file_system_context_from__game(p_game),
    //         &quantity_of__serialized__entities,
    //         1,
    //         1,
    //         p_file_handler);
    // if (error) {
    //     goto serialize_chunk__error;
    // }
    set_process__sub_state(
            p_this_process, 
            Sub_State__Chunk_Serialize__Write_Entities);
serialize_chunk__entities:

    // center hitbox to the center of the chunk.
    // Vector__3i32F4 position_of__hitbox_3i32F4 =
    //     get_vector__3i32F4_using__i32(
    //             (p_serialization_request
    //                 ->position_of__serialization_3i32.x__i32
    //                 * CHUNK_WIDTH__IN_TILES * TILE_WIDTH__IN_PIXELS)
    //             + (CHUNK_WIDTH__IN_TILES * TILE_WIDTH__IN_PIXELS >> 1),
    //             (p_serialization_request
    //                 ->position_of__serialization_3i32.y__i32
    //                 * CHUNK_WIDTH__IN_TILES * TILE_WIDTH__IN_PIXELS)
    //             + (CHUNK_WIDTH__IN_TILES * TILE_WIDTH__IN_PIXELS >> 1),
    //             (p_serialization_request
    //                 ->position_of__serialization_3i32.z__i32
    //                 * CHUNK_DEPTH__IN_TILES * TILE_WIDTH__IN_PIXELS)
    //             + (CHUNK_WIDTH__IN_TILES * TILE_WIDTH__IN_PIXELS >> 1)
    //             );

    // Hitbox_AABB serialization_hitbox;
    // initialize_hitbox(
    //         &serialization_hitbox, 
    //         TILE_WIDTH__IN_PIXELS
    //         * CHUNK_WIDTH__IN_TILES, 
    //         TILE_WIDTH__IN_PIXELS
    //         * CHUNK_WIDTH__IN_TILES, 
    //         position_of__hitbox_3i32F4);

    // foreach_p_entity_within__hitbox(
    //         get_p_collision_manager_from__game(p_game), 
    //         &serialization_hitbox, 
    //         f_foreach_entity__serialize_into__chunk, 
    //         p_game, 
    //         p_serialization_request);

    Index__u32 position_at__end_of__file =
        PLATFORM_get_position_in__file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_file_handler);


    // PLATFORM_set_position_in__file(
    //         get_p_PLATFORM_file_system_context_from__game(p_game), 
    //         position_of__container_quantity_in__file, 
    //         p_file_handler);
    // error = PLATFORM_write_file(
    //         get_p_PLATFORM_file_system_context_from__game(p_game),
    //         &quantity_of__serialized__containers,
    //         1,
    //         1,
    //         p_file_handler);
    // if (error) {
    //     goto serialize_chunk__error;
    // }

    // PLATFORM_set_position_in__file(
    //         get_p_PLATFORM_file_system_context_from__game(p_game), 
    //         position_of__entity_quantity_in__file, 
    //         p_file_handler);
    // error = PLATFORM_write_file(
    //         get_p_PLATFORM_file_system_context_from__game(p_game),
    //         &quantity_of__serialized__entities,
    //         1,
    //         1,
    //         p_file_handler);
    // if (error) {
    //     goto serialize_chunk__error;
    // }

    PLATFORM_set_position_in__file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            position_at__end_of__file, 
            p_file_handler);

    set_process__sub_state(
            p_this_process,
            Sub_State__Chunk_Serialize__Finish);
    return;
serialize_chunk__finish:
    clear_chunk_flags(p_chunk);
    return;

serialize_chunk__error:
    debug_error("m_serialize__chunk, failed error: %d", error);
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

    Chunk *p_chunk =
        (Chunk*)p_serialization_request
        ->p_data;

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
        debug_error("m_serialize__chunk, failed error: %d", error);
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        return;
    }

    if (length_of__read
            != sizeof(p_chunk->tiles)) {
        // debug_error("m_serialize__chunk, bad read length: %d/%d", 
        //         length_of__read,
        //         sizeof(p_chunk->tiles));
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        return;
    }

    length_of__read = 1;
    u8 quantity_of__serialized__containers = 0;
    error = PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                &quantity_of__serialized__containers, 
                &length_of__read,
                1, 
                p_file_handler);
    if (error) {
        debug_error("m_serialize__chunk, failed error: %d", error);
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        return;
    }

    for (Index__u8 index_of__serialized_container = 0;
            index_of__serialized_container < quantity_of__serialized__containers;
            index_of__serialized_container++) {
        Serialization_Header serialization_header;

        length_of__read = sizeof(Serialization_Header);
        error = PLATFORM_read_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    (u8*)&serialization_header, 
                    &length_of__read,
                    1, 
                    p_file_handler);
        if (error) {
            debug_error("m_serialize__chunk, failed error: %d", error);
            set_chunk_as__inactive(p_chunk);
            set_chunk_as__visually_updated(p_chunk);
            return;
        }

        Inventory *p_inventory =
            allocate_p_inventory_using__this_uuid_in__inventory_manager(
                    get_p_inventory_manager_from__game(p_game),
                    serialization_header.uuid);
        initialize_inventory(
                p_inventory, 
                serialization_header.uuid);
        if (!p_inventory) {
            debug_error("m_deserialize__chunk, p_inventory is null. IM full?");
            break;
        }

#warning TODO: deserialize using sub-process
    }

    length_of__read = 1;
    u8 quantity_of__serialized__entities = 0;
    error = PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                &quantity_of__serialized__entities, 
                &length_of__read,
                1, 
                p_file_handler);
    if (error) {
        debug_error("m_serialize__chunk, failed error: %d", error);
        set_chunk_as__inactive(p_chunk);
        set_chunk_as__visually_updated(p_chunk);
        return;
    }

    set_chunk_as__active(p_chunk);
}

Identifier__u32 get_uuid__chunk(
        Chunk *p_chunk) {
    return 1337;
    // TODO: impl
}
