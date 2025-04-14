#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "platform.h"
#include "serialization/serialization_header.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity) {
    memset(p_entity, 0, sizeof(Entity));
    initialize_serialization_header(
            &p_entity->_serialization_header,
            p_entity->_serialization_header.uuid,
            sizeof(Entity));
}

void serialize_entity(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Serialization_Request *p_serialized_request,
        Entity *p_entity) {
    PLATFORM_write_file(
            p_PLATFORM_file_system_context, 
            (u8*)&p_entity->entity_data, 
            sizeof(Entity_Data), 
            1, 
            p_serialized_request->p_file_handler);
}

void deserialize_entity(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        Game *p_game,
        Serialization_Request *p_serialized_request) {
    Entity *p_entity =
        allocate_entity_in__entity_manager(
                p_game, 
                get_p_world_from__game(p_game),
                get_p_entity_manager_from__game(p_game),
                Entity_Kind__None,
                chunk_vector_3i32_to__vector_3i32F4(
                    get_center_of__local_space_manager(
                        get_p_local_space_manager_from__client(
                            get_p_local_client_by__from__game(p_game)))));

    Quantity__u32 quantity_of__bytes_read =
        sizeof(Serialization_Header) + sizeof(Entity_Data);

    PLATFORM_read_file(
            p_PLATFORM_file_system_context, 
            (u8*)&p_entity, 
            &quantity_of__bytes_read, 
            1, 
            p_serialized_request->p_file_handler);

    // precaution
    p_entity->_serialization_header.size_of__struct = sizeof(Entity);

    if (quantity_of__bytes_read
            != sizeof(Entity_Data)) {
        debug_error("m_process__deserialize_entity, corrupt file.");
    }
}
