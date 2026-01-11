#include "client.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/entity.h"
#include "entity/entity_manager.h"
#include "game.h"
#include "platform.h"
#include "rendering/sprite_manager.h"
#include "serialization/serialization_header.h"
#include "world/chunk_vectors.h"
#include "world/local_space_manager.h"
#include "inventory/inventory_manager.h"
#include "inventory/inventory.h"
#include "rendering/sprite_manager.h"
#include "rendering/graphics_window.h"
#include "world/world.h"

void m_entity_dispose_handler__default(
        Entity *p_this_entity,
        Game *p_game,
        World *p_world) {
    Sprite *p_sprite =
        get_p_sprite_by__uuid_from__sprite_manager(
                get_p_sprite_manager_from__graphics_window(
                    p_game,
                    get_p_graphics_window_from__world(
                        p_world)), 
                GET_UUID_P(p_this_entity));
    if (p_sprite) {
        release_sprite_from__sprite_manager(
                get_p_gfx_context_from__game(p_game), 
                get_p_sprite_manager_from__graphics_window(
                    p_game,
                    get_p_graphics_window_from__world(
                        p_world)), 
                p_sprite);
    }

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_this_entity);

    if (p_hitbox_aabb) {
        release_hitbox_aabb_from__hitbox_aabb_manager(
                p_game,
                get_p_hitbox_aabb_manager_from__game(
                    p_game), 
                p_hitbox_aabb);
    }
}

void initialize_entity(
        Entity *p_entity, 
        enum Entity_Kind kind_of_entity) {
    memset(p_entity, 0, sizeof(Entity));
    initialize_serialization_header(
            &p_entity->_serialization_header,
            p_entity->_serialization_header.uuid,
            sizeof(Entity));
    p_entity->entity_functions.m_entity_dispose_handler =
        m_entity_dispose_handler__default;
}

PLATFORM_Write_File_Error serialize_entity(
        Game *p_game,
        Serialization_Request *p_serialized_request,
        Entity *p_entity) {
    if (p_entity
            ->entity_functions
            .m_entity_serialize_handler) {
        return 
            p_entity
            ->entity_functions
            .m_entity_serialize_handler(
                    p_entity,
                    p_game,
                    get_p_PLATFORM_file_system_context_from__game(p_game),
                    get_p_world_from__game(p_game),
                    p_serialized_request);
    }

    return PLATFORM_Write_File_Error__None;
}

PLATFORM_Read_File_Error deserialize_entity(
        Game *p_game,
        Serialization_Request *p_serialization_request,
        Entity *p_entity) {

    Quantity__u32 quantity_of__bytes_read =
        sizeof(Serialization_Header);

    PLATFORM_Read_File_Error error =
        PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8 *)&p_entity->_serialization_header, 
                &quantity_of__bytes_read, 
                1, 
                p_serialization_request->p_file_handler);

    p_entity->_serialization_header.size_of__struct = sizeof(Entity);

    if (error) {
        debug_error("deserialize_entity, failed to read entity serialization header.");
        return error;
    }

    quantity_of__bytes_read =
        sizeof(Entity_Data);

    error =
        PLATFORM_read_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8 *)&p_entity->entity_data, 
                &quantity_of__bytes_read, 
                1, 
                p_serialization_request->p_file_handler);

    if (error) {
        debug_error("deserialize_entity, failed to read entity data.");
        return error;
    }

    sanitize_entity_functions(
            get_p_entity_manager_from__game(
                p_game), 
            p_entity);

    if (p_entity
            ->entity_functions
            .m_entity_deserialize_handler) {
        return p_entity
            ->entity_functions
            .m_entity_deserialize_handler(
                    p_entity,
                    p_game,
                    get_p_PLATFORM_file_system_context_from__game(p_game),
                    get_p_world_from__game(p_game),
                    p_serialization_request);
    }

    // precaution
    p_entity->_serialization_header.size_of__struct = sizeof(Entity);

    return PLATFORM_Read_File_Error__None;
}

PLATFORM_Write_File_Error m_entity_serialization_handler__default(
        Entity *p_entity_self, 
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Serialization_Request *p_serialization_request) {
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(
                    p_game), 
                GET_UUID_P(p_entity_self));

    if (p_hitbox_aabb) {
        p_entity_self->entity_data.entity_flags |=
            ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION;
    }

    Inventory *p_inventory =
        get_inventory_by__uuid_in__inventory_manager(
                get_p_inventory_manager_from__game(
                    p_game), 
                GET_UUID_P(p_entity_self));

    if (p_inventory) {
        p_entity_self->entity_data.entity_flags |=
            ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION;
    }

    PLATFORM_Write_File_Error error =
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)p_entity_self, 
                sizeof(Serialization_Header), 
                1, 
                p_serialization_request->p_file_handler);

    if (error) {
        debug_error("m_entity_serialization_handler__default, IO failed on entity header: %d", error);
        return error;
    }

    error =
        PLATFORM_write_file(
                get_p_PLATFORM_file_system_context_from__game(p_game), 
                (u8*)&p_entity_self->entity_data, 
                sizeof(Entity_Data), 
                1, 
                p_serialization_request->p_file_handler);

    if (error) {
        debug_error("m_entity_serialization_handler__default, IO failed on entity data: %d", error);
        return error;
    }

    if (p_hitbox_aabb) {
        error =
            PLATFORM_write_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    (u8*)p_hitbox_aabb, 
                    sizeof(Hitbox_AABB), 
                    1, 
                    p_serialization_request->p_file_handler);

        if (error) {
            debug_error("m_entity_serialization_handler__default, IO failed on hitbox: %d", error);
            return error;
        }
    }

    if (p_inventory) {
        error =
            serialize_inventory(
                    get_p_PLATFORM_file_system_context_from__game(
                        p_game), 
                    p_serialization_request, 
                    p_inventory);
        if (error) {
            debug_error("m_entity_serialization_handler__default, IO failed on inventory: %d", error);
            return error;
        }
    }

    return error;
}

PLATFORM_Read_File_Error m_entity_deserialization_handler__default(
        Entity *p_this_entity, 
        Game *p_game,
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world,
        Serialization_Request *p_serialization_request) {
    Quantity__u32 quantity_of__bytes_read = 0;
    PLATFORM_Read_File_Error error = 0;

    if (p_this_entity->entity_data.entity_flags
            & ENTITY_FLAG__IS_WITH_HITBOX__SERIALIZATION) {
        Hitbox_AABB *p_hitbox_aabb =
            allocate_hitbox_aabb_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__game(
                        p_game), 
                    GET_UUID_P(p_this_entity));

        if (!p_hitbox_aabb) {
            debug_error("m_entity_deserialization_handler__default, failed to allocate hitbox for entity.");
            return PLATFORM_Read_File_Error__Unknown;
        }

        quantity_of__bytes_read = sizeof(Hitbox_AABB);
        error =
            PLATFORM_read_file(
                    get_p_PLATFORM_file_system_context_from__game(p_game), 
                    (u8*)p_hitbox_aabb, 
                    &quantity_of__bytes_read, 
                    1, 
                    p_serialization_request->p_file_handler);

        if (error) {
            debug_error("m_entity_deserialization_handler__default, IO error on hitbox: %d",
                    error);
            return error;
        }
    }

    if (p_this_entity->entity_data.entity_flags
            & ENTITY_FLAG__IS_WITH_INVENTORY__SERIALIZATION) {
        Inventory *p_inventory =
            allocate_p_inventory_using__this_uuid_in__inventory_manager(
                    get_p_inventory_manager_from__game(p_game), 
                    GET_UUID_P(p_this_entity));

        if (!p_inventory) {
            debug_error("m_entity_deserialization_handler__default, failed to allocate inventory for entity.");
            return PLATFORM_Read_File_Error__Unknown;
        }

        error =
            deserialize_inventory(
                    get_p_PLATFORM_file_system_context_from__game(
                        p_game), 
                    get_p_item_manager_from__game(p_game), 
                    p_serialization_request, 
                    p_inventory);

        if (error) {
            debug_error("m_entity_deserialization_handler__default, IO error on inventory: %d",
                    error);
            return error;
        }
    }

    set_entity_as__enabled(p_this_entity);
    return PLATFORM_Read_File_Error__None;
}
