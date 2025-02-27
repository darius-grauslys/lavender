#include "collisions/hitbox_aabb.h"
#include "defines.h"
#include "defines_weak.h"
#include "entity/handlers/entity_handlers.h"
#include "platform.h"
#include "platform_defines.h"
#include "rendering/graphics_window.h"
#include "serialization/serialization_request.h"
#include "world/camera.h"
#include "world/chunk_vectors.h"
#include "world/serialization/world_directory.h"
#include "world/tile_logic_manager.h"
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
            (u32)p_game);

    // TODO: take world name in by world_parameters
    strncpy(p_world->name, "default_world", WORLD_NAME_MAX_SIZE_OF);
    p_world->length_of__world_name = strnlen(p_world->name, WORLD_NAME_MAX_SIZE_OF);

    initialize_world_parameters(
            &p_world->world_parameters, 
            f_chunk_generator);
    initialize_entity_manager(&p_world->entity_manager);
    initialize_tile_logic_manager(
            get_p_tile_logic_manager_from__world(p_world));
    register_core_tile_logic_handlers(
            get_p_tile_logic_manager_from__world(p_world));
}

void manage_world(
        Game *p_game,
        Graphics_Window *p_gfx_window) {
    manage_world__entities(p_game);

    if (poll_world_for__scrolling(
                p_game, 
                &p_game->world,
                p_gfx_window)) {
#warning put local_space centering code here.
        // set_collision_manager__center_chunk(
        //         &p_game->world.collision_manager,
        //         p_game->world.chunk_manager.x__center_chunk__signed_index_i32,
        //         p_game->world.chunk_manager.y__center_chunk__signed_index_i32);
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
    debug_abort("get_p_entity_from__world_using__3i32F4, impl");
    // Serialized_Field *ps_field =
    //     get_s_record_from__collision_manager_with__3i32F4(
    //         get_p_collision_manager_from__world(p_world), 
    //         position__3i32F4);

    // if (is_p_serialized_field__linked(
    //             ps_field)) {
    //     return ps_field->p_serialized_field__entity;
    // }

    return 0;
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

    // TODO: save other players if any.
    Entity *p_local_player =
        get_p_local_player_from__game(p_game);

#warning serialize player as sub_process
    // p_local_player->_serializer.m_serialize_handler(
    //         p_game,
    //         p_serialization_request,
    //         &p_local_player->_serializer);
}

void m_process__deserialize_world(
        Process *p_this_process,
        Game *p_game) {
    Serialization_Request *p_serialization_request =
        (Serialization_Request*)p_this_process->p_process_data;

    World *p_world = 
        (World*)p_serialization_request->p_data;
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

#warning TODO: deserialize player as sub process
    // p_player->_serializer.m_deserialize_handler(
    //         p_game,
    //         p_serialization_request,
    //         &p_player->_serializer);
}
