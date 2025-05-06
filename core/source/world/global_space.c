#include "world/global_space.h"
#include "client.h"
#include "collisions/collision_node.h"
#include "collisions/collision_node_pool.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "inventory/inventory.h"
#include "inventory/inventory_manager.h"
#include "platform.h"
#include "platform_defines.h"
#include "process/process_manager.h"
#include "serialization/serialization_header.h"
#include "process/process.h"
#include "vectors.h"
#include "world/chunk.h"
#include "entity/entity.h"
#include "world/chunk_pool.h"
#include "world/chunk_vectors.h"
#include "world/global_space_manager.h"
#include "world/local_space_manager.h"
#include "world/serialization/world_directory.h"
#include "world/world.h"

void initialize_global_space(
        Global_Space *p_global_space) {
    memset(p_global_space,
            0,
            sizeof(Global_Space));
    initialize_serialization_header_for__deallocated_struct__uuid_64(
            &p_global_space->_serialization_header, 
            sizeof(Global_Space));
}

void initialize_global_space_as__allocated(
        Global_Space *p_global_space,
        Identifier__u64 uuid_64) {
    memset(p_global_space,
            0,
            sizeof(Global_Space));
    initialize_serialization_header__uuid_64(
            &p_global_space->_serialization_header, 
            uuid_64, 
            sizeof(Global_Space));
    p_global_space->quantity_of__references = 1;
}

void m_process__serialize_entities_in__global_space(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)
        p_this_process->p_process_data;
    Global_Space *p_global_space =
        p_serialization_request
        ->p_data;
    Collision_Node *p_collision_node =
        get_p_collision_node_from__global_space(
                p_global_space);

    Collision_Node_Entry *p_collision_node__entry =
        p_collision_node->p_linked_list__collision_node_entries__tail;

    if (!p_collision_node__entry) {
        complete_process(p_this_process);
        return;
    }

    Identifier__u32 uuid__u32 =
        p_collision_node__entry
        ->uuid_of__hitbox__u32
        ;

    remove_entry_from__collision_node(
            get_p_collision_node_pool_from__world(
                get_p_world_from__game(p_game)), 
            p_collision_node, 
            uuid__u32);

    Entity *p_entity =
        get_p_entity_by__uuid_from__entity_manager(
                get_p_entity_manager_from__world(
                    get_p_world_from__game(p_game)), 
                uuid__u32);

    if (!p_entity) {
        debug_error("m_process__serialize_entities_in__global_space, failed to locate entity in collision_node.");
        return;
    }

    serialize_entity(
            p_game,
            p_serialization_request, 
            p_entity);
}

void m_process__deserialize_entities_in__global_space(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Global_Space *p_global_space = 
        (Global_Space*)p_serialization_request->p_data;

    Collision_Node *p_collision_node =
        get_p_collision_node_from__global_space(
                p_global_space);

    if (!p_serialization_request->quantity_of__file_contents--) {
        complete_process(p_this_process);
        return;
    }

    Entity *p_entity =
        allocate_entity_in__entity_manager(
                p_game, 
                get_p_world_from__game(p_game),
                get_p_entity_manager_from__game(p_game),
                Entity_Kind__None);

    deserialize_entity(
            p_game, 
            p_serialization_request,
            p_entity);
}

#define M_PROCESS__SERIALIZE_CONTAINERS__STEPS 32

void m_process__serialize_containers_in__global_space(
        Process *p_this_process,
        Game *p_game) {
    /*
    Serialization_Request *p_serialized_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Global_Space *p_global_space =
        (Global_Space*)p_serialized_request->p_data;

    if (!p_this_process->process_valueA__i16) {
        p_this_process->process_valueA__i16 = PLATFORM_get_position_in__file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialized_request->p_file_handler);

        Quantity__u16 quantity_of__containers = 0;
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)&quantity_of__containers, 
                sizeof(quantity_of__containers), 
                1, 
                p_serialized_request->p_file_handler);
    }

    Signed_Index__i16 *p_index_of__tile_in__chunk =
        &p_this_process
        ->process_valueB__i16;

    u16 steps_remaining = 
        M_PROCESS__SERIALIZE_CONTAINERS__STEPS;

    Signed_Index__i16 *p_quantity_of__containers_in__chunk =
        &p_this_process
        ->process_valueB__i16;

    Tile_Vector__3i32 tile_vector__3i32 =
        chunk_vector_3i32_to__vector_3i32(
                p_global_space->chunk_vector__3i32);

    for (Index__u8 z = *p_index_of__tile_in__chunk
            / (CHUNK__WIDTH * CHUNK__HEIGHT);
            z < CHUNK__DEPTH;
            z++) {
        for (Index__u8 y = *p_index_of__tile_in__chunk
                & (CHUNK__WIDTH * CHUNK__HEIGHT - 1)
                / CHUNK__WIDTH;
                y < CHUNK__HEIGHT;
                y++) {
            for (Index__u8 x = *p_index_of__tile_in__chunk
                    & (CHUNK__WIDTH-1);
                    x < CHUNK__WIDTH;
                    x++) {
                Tile_Vector__3i32 container_vector__3i32 =
                    add_vectors__3i32(
                            tile_vector__3i32,
                            get_vector__3i32(x, y, z));

                Inventory *p_inventory_of__container =
                    get_p_inventory_by__uuid_in__inventory_manager(
                            get_p_inventory_manager_from__game(p_game), 
                            get_uuid_for__container(
                                tile_vector__3i32));

                if (p_inventory_of__container) {
                    (*p_quantity_of__containers_in__chunk)++;
                    Process *p_process =
                        run_process(
                                get_p_process_manager_from__game(p_game), 
                                m_process__serialize_inventory, 
                                PROCESS_FLAGS__NONE);
                    if (!p_process) {
                        debug_error("m_process__serialize_containers_in__global_space, failed to dispatch container serialization process.");
                        // TODO: try returning, and then re-attempting instead.
                        //          while using a time-out counter.
                        fail_process(p_this_process);
                        return;
                    }
                    p_process->p_process_data =
                        p_serialized_request;
                    enqueue_process(
                            p_this_process,
                            p_process);
                    return;
                }

                (*p_index_of__tile_in__chunk)++;
                if (!steps_remaining--) {
                    return;
                }
            }
        }
    }

    Index__u32 position_of__file =
        PLATFORM_get_position_in__file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialized_request->p_file_handler);
    if (!PLATFORM_set_position_in__file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            p_this_process
            ->process_valueA__i16, 
            p_serialized_request->p_file_handler)) {
        debug_error("m_process__serialize_containers_in__global_space, failed to set position in file.");
        fail_process(p_this_process);
        return;
    }

    if (PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)p_quantity_of__containers_in__chunk, 
            sizeof(i16), 
            1, 
            p_serialized_request->p_file_handler)) {
        debug_error("m_process__serialize_containers_in__global_space, failed to write container quantity into file.");
        fail_process(p_this_process);
        return;
    }

    if (!PLATFORM_set_position_in__file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            position_of__file,
            p_serialized_request->p_file_handler)) {
        debug_error("m_process__serialize_containers_in__global_space, failed to RESET position in file.");
        fail_process(p_this_process);
        return;
    }

    complete_process(p_this_process);
    */
}

void m_process__deserialize_containers_in__global_space(
        Process *p_this_process,
        Game *p_game) {
    /*
    Serialization_Request *p_serialized_request =
        (Serialization_Request*)p_this_process->p_process_data;
    Global_Space *p_global_space =
        (Global_Space*)p_serialized_request->p_data;

    if (!p_this_process->process_valueA__i16) {
        Quantity__u32 quantity_of__bytes_read = sizeof(
                p_this_process->process_valueA__i16);
        if (PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)&p_this_process->process_valueA__i16, 
                &quantity_of__bytes_read, 
                1, 
                p_serialized_request->p_file_handler)) {
            debug_error("m_process__deserialize_containers_in__global_space, failed to read container quantity.");
            fail_process(p_this_process);
        }
    }

    if (!p_this_process->process_valueA__i16--) {
        complete_process(p_this_process);
        return;
    }

    Process *p_process =
        run_process(
                get_p_process_manager_from__game(p_game), 
                m_process__deserialize_inventory, 
                PROCESS_FLAGS__NONE);

    if (!p_process) {
        debug_error("m_process__deserialize_containers_in__global_space, failed to dispatch container deserialization process.");
        // TODO: do a retry and timeout instead
        fail_process(p_this_process);
        return;
    }

    p_process->p_process_data =
        p_serialized_request;
    enqueue_process(
            p_this_process, 
            p_process);
            */
}

typedef enum IO_Global_Space_State {
    IO_Global_Space_State__None = 0,
    IO_Global_Space_State__Chunk = IO_Global_Space_State__None,
    IO_Global_Space_State__Entities,
    IO_Global_Space_State__Containers,
    IO_Global_Space_State__Finished,
    IO_Global_Space_State__Unknown,
} IO_Global_Space_State;

void m_process__serialize_global_space(
        Process *p_this_process,
        Game *p_game) {
    Process *p_process = 0;
    Serialization_Request *p_serialization_request = 
        (Serialization_Request*)p_this_process->p_process_data;
    Global_Space *p_global_space = 
        (Global_Space*)p_serialization_request->p_data;
    Collision_Node_Entry *p_collision_node_entry = 0;
    Entity *p_entity = 0;
    if (IS_DEALLOCATED_P(p_global_space)) {
        PLATFORM_close_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
        PLATFORM_release_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
        fail_process(p_this_process);
        return;
    }
    switch (p_this_process->process_sub_state__u8) {
        default:
            debug_error("m_process__serialize_global_space, bad state(%d).",
                    p_this_process->process_sub_state__u8);
            fail_process(p_this_process);
            break;
        case IO_Global_Space_State__Chunk:
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Entities;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__serialize_chunk, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__serialize_global_space, failed to allocate process for m_process__serialize_chunk.");
                fail_process(p_this_process);
                break;
            }

            p_collision_node_entry =
                get_p_collision_node_from__global_space(p_global_space)
                ->p_linked_list__collision_node_entries__tail;
            p_entity = 0;
            while (iterate_entities_in__collision_node_entry(
                        get_p_entity_manager_from__game(p_game), 
                        &p_collision_node_entry, 
                        &p_entity)) {
                set_entity_as__disabled(p_entity);
            }

            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
        case IO_Global_Space_State__Entities:
            // We only reach this point if the subprocess has finished.
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Containers;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__serialize_entities_in__global_space, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__serialize_global_space, failed to allocate process for m_process__serialize_entities_in__global_space.");
                fail_process(p_this_process);
                break;
            }

            // TODO: in the future for multithreading, we will want to
            //       perform this write before running the process.
            //       So we first allocate the process, see if it succeeded
            //       then write the entity quantity, and finally run the process.
            Quantity__u32 quantity_of__entries = 
                get_quantity_of__entries_in__collision_node(
                        get_p_collision_node_from__global_space(p_global_space));

            // write the quantity of entities found into the file
            // before the actual entity data gets written.
            PLATFORM_write_file(
                    get_p_PLATFORM_file_system_context_from__game(
                        p_game), 
                    (u8*)&quantity_of__entries, 
                    sizeof(quantity_of__entries), 
                    1, 
                    p_serialization_request
                    ->p_file_handler);

            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
        case IO_Global_Space_State__Containers:
            // TODO: this requires Regions to be added, and we might not even want it.

            // We only reach this point if the subprocess has finished.
            /*
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Finished;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__serialize_containers_in__global_space, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__serialize_global_space, failed to allocate process for m_process__serialize_containers_in__global_space.");
                fail_process(p_this_process);
                break;
            }

            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
            */
        case IO_Global_Space_State__Finished:
            // We only reach this point if the subprocess has finished.
            PLATFORM_close_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    p_serialization_request);
            PLATFORM_release_serialization_request(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    p_serialization_request);
            if (!is_global_space__awaiting_construction(p_global_space)) {
                release_global_space(
                        get_p_world_from__game(p_game),
                        p_global_space);
            } else {
                set_global_space_as__NOT_deconstructing(p_global_space);
            }
            complete_process(p_this_process);
            break;
    }
}

void m_process__deserialize_global_space(
        Process *p_this_process,
        Game *p_game) {
    Process *p_process = 0;
    Serialization_Request *p_serialization_request = 
        (Serialization_Request*)p_this_process->p_process_data;
    Global_Space *p_global_space = 
        (Global_Space*)p_serialization_request->p_data;
    if (IS_DEALLOCATED_P(p_global_space)) {
        PLATFORM_close_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
        PLATFORM_release_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
        fail_process(p_this_process);
        return;
    }
    switch (p_this_process->process_sub_state__u8) {
        default:
            debug_error("m_process__serialize_global_space, bad state(%d).",
                    p_this_process->process_sub_state__u8);
            fail_process(p_this_process);
            break;
        case IO_Global_Space_State__Chunk:
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Entities;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__deserialize_chunk, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__deserialize_global_space, failed to allocate process for m_process__deserialize_chunk.");
                fail_process(p_this_process);
                break;
            }

            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
        case IO_Global_Space_State__Entities:
            // We only reach this point if the subprocess has finished.
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Containers;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__deserialize_entities_in__global_space, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__deserialize_global_space, failed to allocate process for m_process__deserialize_entities_in__global_space.");
                fail_process(p_this_process);
                break;
            }

            Quantity__u32 quantity_of__entities = 0;
            Quantity__u32 quantity_of__bytes_to_read = sizeof(quantity_of__entities);
            PLATFORM_read_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    (u8 *)&quantity_of__entities, 
                    &quantity_of__bytes_to_read, 
                    1, 
                    p_serialization_request->p_file_handler);

            if (quantity_of__bytes_to_read
                    != sizeof(quantity_of__entities)) {
                debug_error("m_process__deserialize_global_space, corrupt file on entity region.");
                fail_process(p_this_process);
                return;
            }

            p_serialization_request->quantity_of__file_contents =
                quantity_of__entities;

            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
        case IO_Global_Space_State__Containers:
            // We only reach this point if the subprocess has finished.
            /*
            p_this_process->process_sub_state__u8 =
                IO_Global_Space_State__Finished;
            p_process = run_process(
                    get_p_process_manager_from__game(p_game), 
                    m_process__deserialize_containers_in__global_space, 
                    PROCESS_FLAGS__NONE);
            if (!p_process) {
                debug_error("m_process__deserialize_global_space, failed to allocate process for m_process__deserialize_containers_in__global_space.");
                fail_process(p_this_process);
                break;
            }
            p_process->p_process_data =
                p_this_process->p_process_data;
            enqueue_process(
                    p_this_process, 
                    p_process);
            break;
            */
        case IO_Global_Space_State__Finished:
            // We only reach this point if the subprocess has finished.
            set_global_space_as__NOT_constructing(
                    p_global_space);
            PLATFORM_close_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    p_serialization_request);
            PLATFORM_release_serialization_request(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    p_serialization_request);
            complete_process(p_this_process);
            break;
    }
}

Process *dispatch_process__deserialize_global_space(
        Game *p_game,
        Global_Space *p_global_space) {
    Serialization_Request *p_serialization_request =
        PLATFORM_allocate_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(p_game));

    if (!p_serialization_request) {
        debug_error("dispatch_process__deserialize_global_space, failed to allocate p_serialization_request.");
        return 0;
    }

    p_serialization_request->p_data =
        p_global_space;

    IO_path path_to__chunk_file;
    stat_chunk_file__tiles(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            get_p_world_from__game(p_game), 
            p_global_space, 
            path_to__chunk_file);

    PLATFORM_Open_File_Error error =
        PLATFORM_open_file(
                get_p_PLATFORM_file_system_context_from__game(p_game),
                path_to__chunk_file,
                "rb",
                p_serialization_request);

    if (error) {
        path_to__chunk_file[MAX_LENGTH_OF__IO_PATH-1] = 0;
        PLATFORM_release_serialization_request(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                p_serialization_request);
        debug_error("dispatch_process__deserialize_global_space, failed to open(%d) global_space file: %s",
                error,
                path_to__chunk_file);
        return 0;
    }

    Process *p_process = 
        run_process(
                get_p_process_manager_from__game(p_game), 
                m_process__deserialize_global_space, 
                PROCESS_FLAGS__NONE);

    p_process->p_process_data =
        p_serialization_request;

    set_global_space_as__constructing(
            p_global_space);

    return p_process;
}

