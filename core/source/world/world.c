#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/handlers/entity_handlers.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/graphics_window.h"
#include "serialization/serialization_request.h"
#include "serialization/serializer.h"
#include "world/camera.h"
#include "world/chunk_vectors.h"
#include "world/serialization/world_directory.h"
#include "world/tile_logic_manager.h"
#include <world/world.h>
#include <game.h>
#include <entity/entity_manager.h>
#include <collisions/collision_manager.h>
#include <world/chunk_manager.h>
#include <world/world_parameters.h>
#include "serialization/serialized_field.h"

#include <entity/entity.h>
#include <debug/debug.h>
#include <vectors.h>

void m_serialize_handler__world(
        Game *p_game,
        Serialization_Request *p_serialization_request,
        Serializer *p_this_serializer);
void m_deserialize_handler__world(
        Game *p_game,
        Serialization_Request *p_serialization_request,
        Serializer *p_this_serializer);

void initialize_world(
        Game *p_game,
        World *p_world,
        f_Chunk_Generator f_chunk_generator) {

    intialize_serializer(
            &p_world->_serializer, 
            sizeof(World), 
            0, 
            m_serialize_handler__world, 
            m_deserialize_handler__world);

    initialize_repeatable_psuedo_random(
            &p_world->repeatable_pseudo_random, 
            (u32)p_game);

    // TODO: take world name in by world_parameters
    strncpy(p_world->name, "default_world", WORLD_NAME_MAX_SIZE_OF);
    p_world->length_of__world_name = strnlen(p_world->name, WORLD_NAME_MAX_SIZE_OF);

    initialize_world_parameters(
            &p_world->world_parameters, 
            f_chunk_generator);
    initialize_entity_manager(&p_world->entity_manager);
    initialize_collision_manager(&p_world->collision_manager);
    set_collision_manager__center_chunk(
            &p_world->collision_manager, 
            0, 
            0);
    initialize_tile_logic_manager(
            get_p_tile_logic_manager_from__world(p_world));
    initialize_chunk_manager(
            p_game,
            get_p_chunk_manager_from__world(p_world));
    register_core_tile_logic_handlers(
            get_p_tile_logic_manager_from__world(p_world));
}

void manage_world(
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    if (poll_chunk_manager_for__serialization(
                p_game, 
                get_p_chunk_manager_from__game(p_game))) {
        return;
    }
    manage_world__entities(p_game);

    if (poll_world_for__scrolling(
                p_game, 
                &p_game->world,
                p_gfx_window)) {
        set_collision_manager__center_chunk(
                &p_game->world.collision_manager,
                p_game->world.chunk_manager.x__center_chunk__signed_index_i32,
                p_game->world.chunk_manager.y__center_chunk__signed_index_i32);
    }
}

void manage_world__entity(
        Game *p_game,
        Entity *p_entity) {
    debug_warning("manage_world__entity, requires impl.");
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
        if (!is_entity__allocated(p_entity)) {
            continue;
        }

        manage_world__entity(
                p_game,
                p_entity);
    }
}

void render_world__entity(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        Entity *p_entity) {
    debug_warning("render_world__entity, impl");
}

void render_entities_in__world(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        World *p_world) {
    Entity_Manager *p_entity_manager =
        get_p_entity_manager_from__world(p_world);

    for (Quantity__u16 i=0;
            i<ENTITY_MAXIMUM_QUANTITY_OF;i++) {
        Entity *p_entity =
            get_p_entity_from__entity_manager(
                    p_entity_manager, i);
        if (!is_entity__allocated(p_entity)) {
            continue;
        }

        render_world__entity(
                p_gfx_context,
                p_gfx_window,
                p_entity);
    }
}

bool poll_world_for__scrolling(
        Game *p_game,
        World *p_world,
        Graphics_Window *p_gfx_window) {
    bool is_chunks_moved =
        poll_chunk_manager_for__chunk_movement(
                p_game,
                &p_world->chunk_manager,
                p_gfx_window->p_camera->position);

    return is_chunks_moved;
}

void teleport_player(
        Game *p_game,
        Vector__3i32F4 position__3i32F4) {
    World *p_world = get_p_world_from__game(p_game);
    Chunk_Vector__3i32 chunk_vector__3i32 =
        vector_3i32F4_to__chunk_vector_3i32(
                position__3i32F4);
#warning [***] teleport_player, manage player
    // remove_entity_from__collision_manager(
    //         get_p_collision_manager_from__world(p_world), 
    //         get_p_local_player_from__world(p_world));
    move_chunk_manager_to__chunk_position(
            p_game,
            get_p_chunk_manager_from__world(p_world), 
            chunk_vector__3i32);
    // set_hitbox__position_with__3i32F4(
    //         &get_p_local_player_from__world(
    //             p_world)->hitbox,
    //         position__3i32F4);
    set_collision_manager__center_chunk(
            &p_world->collision_manager,
            p_world->chunk_manager.x__center_chunk__signed_index_i32,
            p_world->chunk_manager.y__center_chunk__signed_index_i32);
    // add_entity_to__collision_manager(
    //         get_p_collision_manager_from__world(p_world), 
    //         get_p_local_player_from__world(p_world));
}

void save_world(
        PLATFORM_File_System_Context *p_PLATFORM_file_system_context,
        World *p_world) {
    save_all_chunks(
            p_PLATFORM_file_system_context,
            p_world,
            get_p_chunk_manager_from__world(p_world));

    char path[MAX_LENGTH_OF__IO_PATH];
    stat_world_header_file(
            p_PLATFORM_file_system_context, 
            p_world,
            path);

    Serialization_Request *p_serialization_request =
        PLATFORM_allocate_serialization_request(
                p_PLATFORM_file_system_context);

    if (!p_serialization_request) {
        debug_error("save_world, failed to allocated p_serialization_request.");
        return;
    }

    enum PLATFORM_Open_File_Error error =
        PLATFORM_open_file(
                p_PLATFORM_file_system_context,
                path, 
                "wb", 
                p_serialization_request);

    if (error) {
        PLATFORM_release_serialization_request(
                p_PLATFORM_file_system_context,
                p_serialization_request);
        debug_error("save_world, IO error: %d", error);
        return;
    }
    
    set_serialization_request_as__fire_and_forget(
            p_serialization_request);
    set_serialization_request_as__using_serializer(
            p_serialization_request);
    set_serialization_request_as__write(
            p_serialization_request);
    p_serialization_request->p_serializer =
        &p_world->_serializer;
}

void load_world(Game *p_game) {
    Gfx_Context *p_gfx_context =
        get_p_gfx_context_from__game(p_game);
    PLATFORM_File_System_Context *p_PLATFORM_file_system_context =
        get_p_PLATFORM_file_system_context_from__game(p_game);
    World *p_world =
        get_p_world_from__game(p_game);
    char path[MAX_LENGTH_OF__IO_PATH];
    Index__u32 index_of__path_append =
        stat_world_header_file(
                p_PLATFORM_file_system_context, 
                p_world,
                path);
    
    if (!index_of__path_append) {
#warning [***] load_world, manage player
        // this is a fresh world.
        // Entity *p_player =
        //     allocate_entity_into__world(
        //             p_game,
        //             Entity_Kind__Player, 
        //             VECTOR__3i32F4__0_0_0);

        // p_world->entity_manager.p_local_player =
        //     p_player;
        return;
    }

    Serialization_Request *p_serialization_request =
        PLATFORM_allocate_serialization_request(
                p_PLATFORM_file_system_context);

    if (!p_serialization_request) {
        debug_error("load_world, failed to allocated p_serialization_request.");
        return;
    }

    enum PLATFORM_Open_File_Error error =
        PLATFORM_open_file(
                p_PLATFORM_file_system_context,
                path, 
                "rb", 
                p_serialization_request);

    if (error) {
        PLATFORM_release_serialization_request(
                p_PLATFORM_file_system_context,
                p_serialization_request);
        debug_error("load_world, IO error: %d", error);
        return;
    }
    
    set_serialization_request_as__fire_and_forget(
            p_serialization_request);
    set_serialization_request_as__using_serializer(
            p_serialization_request);
    set_serialization_request_as__read(
            p_serialization_request);
    p_serialization_request->p_serializer =
        &p_world->_serializer;
}

Entity *get_p_entity_from__world_using__3i32F4(
        World *p_world,
        Vector__3i32F4 position__3i32F4) {
    Serialized_Field *ps_field =
        get_s_record_from__collision_manager_with__3i32F4(
            get_p_collision_manager_from__world(p_world), 
            position__3i32F4);

    if (is_p_serialized_field__linked(
                ps_field)) {
        return ps_field->p_serialized_field__entity;
    }

    return 0;
}

void m_serialize_handler__world(
        Game *p_game,
        Serialization_Request *p_serialization_request,
        Serializer *p_this_serializer) {
    World *p_world = get_p_world_from__game(p_game);

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

    // TODO: save other players if any.
    Entity *p_local_player =
        get_p_local_player_from__game(p_game);

    p_local_player->_serializer.m_serialize_handler(
            p_game,
            p_serialization_request,
            &p_local_player->_serializer);
}

void m_deserialize_handler__world(
        Game *p_game,
        Serialization_Request *p_serialization_request,
        Serializer *p_this_serializer) {
    World *p_world = get_p_world_from__game(p_game);
#warning [***] load_world, manage player
    Entity *p_player = 0;
    // Entity *p_player =
    //     allocate_entity_into__world(
    //             p_game, 
    //             Entity_Kind__Player, 
    //             VECTOR__3i32F4__0_0_0);

    p_world->entity_manager.p_local_player =
        p_player;

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

    if (!p_player) {
        debug_abort("m_deserialize_handler__world, failed to allocate player.");
        return;
    }

    p_player->_serializer.m_deserialize_handler(
            p_game,
            p_serialization_request,
            &p_player->_serializer);
}
