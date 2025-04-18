#include "client.h"
#include "collisions/collision_node.h"
#include "collisions/collision_node_pool.h"
#include "collisions/hitbox_aabb.h"
#include "collisions/hitbox_aabb_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/handlers/entity_handlers.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/graphics_window.h"
#include "serialization/serialization_request.h"
#include "world/camera.h"
#include "world/chunk_pool.h"
#include "world/chunk_vectors.h"
#include "world/global_space_manager.h"
#include "world/local_space_manager.h"
#include "world/serialization/world_directory.h"
#include <world/world.h>
#include <game.h>
#include <entity/entity_manager.h>
#include <world/world_parameters.h>
#include "serialization/serialized_field.h"

#include <entity/entity.h>
#include <debug/debug.h>
#include <vectors.h>

void m_process__serialize_world(
        Process *p_this_process,
        Game *p_game);
void m_process__deserialize_world(
        Process *p_this_process,
        Game *p_game);

void initialize_world(
        Game *p_game,
        World *p_world,
        f_Chunk_Generator f_chunk_generator) {

    initialize_serialization_header(
            &p_world->_serialization_header, 
            0,
            sizeof(World));

    initialize_repeatable_psuedo_random(
            &p_world->repeatable_pseudo_random, 
            (u32)(u64)p_game);

    // TODO: take world name in by world_parameters
    strncpy(p_world->name, "default_world", WORLD_NAME_MAX_SIZE_OF);
    p_world->length_of__world_name = strnlen(p_world->name, WORLD_NAME_MAX_SIZE_OF);

    initialize_world_parameters(
            &p_world->world_parameters, 
            f_chunk_generator);
    initialize_hitbox_aabb_manager(
            get_p_hitbox_aabb_manager_from__world(p_world));
    initialize_entity_manager(&p_world->entity_manager);

    initialize_collision_node_pool(
            get_p_collision_node_pool_from__world(p_world));
    initialize_chunk_pool(
            get_p_chunk_pool_from__world(p_world));

    initialize_global_space_manager(
            get_p_global_space_manager_from__world(p_world));
}

void manage_world(
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    manage_world__entities(p_game);

    World *p_world = 
        get_p_world_from__game(p_game);

    for (Index__u32 index_of__client = 0;
            index_of__client
            < get_quantity_of__clients_connect_to__game(p_game);
            index_of__client++) {
        Client *p_client = 
            get_p_client_by__index_from__game(
                    p_game, 
                    index_of__client);

        if (!is_p_serialized_field__linked(
                    &p_client->s_entity_of__client)) {
            continue;
        }

        Hitbox_AABB *p_hitbox_aabb = 
            get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager(
                    get_p_hitbox_aabb_manager_from__world(
                        p_world), 
                    p_client->s_entity_of__client.p_serialized_field__entity);

        poll_local_space_for__scrolling(
                get_p_local_space_manager_from__client(p_client), 
                p_game, 
                get_p_global_space_manager_from__world(
                    get_p_world_from__game(p_game)), 
                vector_3i32F4_to__chunk_vector_3i32(
                    p_hitbox_aabb->position__3i32F4));
    }
}

void manage_world__entities(Game *p_game) {
    World *p_world =
        &p_game->world;
    Entity_Manager *p_entity_manager =
        &p_game->world.entity_manager;

    for (Quantity__u16 i=0;
            i<ENTITY_MAXIMUM_QUANTITY_OF;i++) {
        Entity *p_entity =
            get_p_entity_from__entity_manager(
                    p_entity_manager, i);
        if (!is_entity__allocated(p_entity)
                || !is_entity__enabled(p_entity)) {
            continue;
        }

        if (p_entity->p_const_entity_functions->m_entity_update_handler) {
            p_entity->p_const_entity_functions->m_entity_update_handler(
                    p_entity,
                    p_game,
                    p_world);
        }
    }
}

bool poll_world_for__scrolling(
        Game *p_game,
        World *p_world,
        Graphics_Window *p_gfx_window) {
    debug_abort("poll_world_for__scrolling, impl");
    return false;
}

void teleport_player(
        Game *p_game,
        Vector__3i32F4 position__3i32F4) {
    debug_abort("teleport_player, impl");
}

void save_world(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world) {
    debug_abort("save_world, impl");
}

void load_world(Game *p_game) {
    debug_abort("load_world, impl");
}

Entity *get_p_entity_from__world_using__3i32F4(
        World *p_world,
        Vector__3i32F4 position__3i32F4) {
    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                get_p_global_space_manager_from__world(p_world), 
                vector_3i32F4_to__chunk_vector_3i32(position__3i32F4));

    Collision_Node *p_collision_node =
        get_p_collision_node_by__uuid_64_from__collision_node_pool(
                get_p_collision_node_pool_from__world(p_world), 
                p_global_space->_serialization_header.uuid);

    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_at__vector_3i32F4_from__collision_node(
                get_p_hitbox_aabb_manager_from__world(p_world),
                p_collision_node, 
                position__3i32F4);

    if (!p_hitbox_aabb)
        return 0;

    return get_p_entity_by__uuid_from__entity_manager(
                get_p_entity_manager_from__world(p_world), 
                GET_UUID_P(p_hitbox_aabb));
}

void m_process__serialize_world(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    World *p_world = 
        (World*)p_serialization_request->p_data;

    Quantity__u32 length_of__read = WORLD_NAME_MAX_SIZE_OF;
    PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)p_world->name, 
            length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);

    // TODO: verify the read lengths for errors.
    length_of__read = sizeof(
            p_game->world.repeatable_pseudo_random.seed__initial);
    PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_game->world.repeatable_pseudo_random.seed__initial, 
            length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);

    length_of__read = sizeof(
            p_game->world.repeatable_pseudo_random.seed__current_random);
    PLATFORM_write_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_game->world.repeatable_pseudo_random.seed__current_random, 
            length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);
}

void m_process__deserialize_world(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    World *p_world = 
        (World*)p_serialization_request->p_data;

    Quantity__u32 length_of__read = WORLD_NAME_MAX_SIZE_OF;
    PLATFORM_read_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)p_world->name, 
            &length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);

    // TODO: verify the read lengths for errors.
    length_of__read = sizeof(
            p_game->world.repeatable_pseudo_random.seed__initial);
    PLATFORM_read_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_game->world.repeatable_pseudo_random.seed__initial, 
            &length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);

    length_of__read = sizeof(
            p_game->world.repeatable_pseudo_random.seed__current_random);
    PLATFORM_read_file(
            get_p_PLATFORM_file_system_context_from__game(p_game), 
            (u8*)&p_game->world.repeatable_pseudo_random.seed__current_random, 
            &length_of__read, 
            1, 
            p_serialization_request
            ->p_file_handler);
}
