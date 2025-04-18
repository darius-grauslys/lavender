#include "client.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity.h"
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
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity) {
    PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_entity->entity_data, 
            sizeof(Entity_Data), 
            1, 
            p_serialized_request->p_file_handler);

    if (p_entity
            ->p_const_entity_functions
            ->m_entity_serialize_handler) {
        p_entity
            ->p_const_entity_functions
            ->m_entity_serialize_handler(
                    p_entity,
                    p_game,
                    get_p_PLATFORM_file_system_context_from__game(p_game),
                    get_p_world_from__game(p_game),
                    p_serialized_request);
    }
}

void deserialize_entity(
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity) {
    Quantity__u32 quantity_of__bytes_read =
        sizeof(Serialization_Header) + sizeof(Entity_Data);

    PLATFORM_read_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_entity, 
            &quantity_of__bytes_read, 
            1, 
            p_serialized_request->p_file_handler);

    // precaution
    p_entity->_serialization_header.size_of__struct = sizeof(Entity);
    set_entity_functions(
            get_p_entity_manager_from__game(p_game), 
            p_entity);

    if (p_entity
            ->p_const_entity_functions
            ->m_entity_deserialize_handler) {
        p_entity
            ->p_const_entity_functions
            ->m_entity_deserialize_handler(
                    p_entity,
                    p_game,
                    get_p_PLATFORM_file_system_context_from__game(p_game),
                    get_p_world_from__game(p_game),
                    p_serialized_request);
    }

    if (quantity_of__bytes_read
            != sizeof(Entity_Data)) {
        debug_error("m_process__deserialize_entity, corrupt file.");
    }
}
