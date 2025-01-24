#ifndef WORLD_H
#define WORLD_H

#include "collisions/collision_manager.h"
#include "defines_weak.h"
#include "world/chunk_manager.h"
#include <defines.h>

void initialize_world(
        Game *p_game,
        World *p_world,
        f_Chunk_Generator f_chunk_generator);

void manage_world(
        Game *p_game,
        Graphics_Window *p_gfx_window);
void manage_world__entities(Game *p_game);

Entity *allocate_entity_into__world(
        Game *p_game,
        enum Entity_Kind the_kind_of_entity,
        Vector__3i32F4 position__3i32F4);

void render_entities_in__world(
        Gfx_Context *p_gfx_context,
        Graphics_Window *p_gfx_window,
        World *p_world);

bool poll_world_for__scrolling(
        Game *p_game,
        World *p_world,
        Graphics_Window *p_gfx_window);

void teleport_player(
        Game *p_game,
        Vector__3i32F4 position__3i32F4);

///
/// Only call this when leaving the world and returning to main menu.
///
void save_world(
        PLATFORM_File_System_Context *p_PLATOFRM_file_system_context,
        World *p_world);

///
/// Only call this from the main menu.
///
void load_world(Game *p_game);

Entity *get_p_entity_from__world_using__3i32F4(
        World *p_world,
        Vector__3i32F4 position__3i32F4);


static inline
Camera *get_p_camera_from__world(World *p_world) {
    return &p_world->camera;
}

static inline
Inventory_Manager *get_p_inventory_manager_from__world(World *p_world) {
    return &p_world->inventory_manager;
}

static inline
Item_Manager *get_p_item_manager_from__world(World *p_world) {
    return &p_world->item_manager;
}

static inline
Item_Recipe_Manager *get_p_item_recipe_manager_from__world(World *p_world) {
    return &p_world->item_recipe_manager;
}

static inline
Station_Manager *get_p_station_manager_from__world(World *p_world) {
    return &p_world->station_manager;
}

static inline 
Entity_Manager *get_p_entity_manager_from__world(World *p_world) {
    return &p_world->entity_manager;
}

static inline 
Chunk_Manager *get_p_chunk_manager_from__world(World *p_world) {
    return &p_world->chunk_manager;
}

static inline
Tile_Logic_Manager *get_p_tile_logic_manager_from__world(World *p_world) {
    return &p_world->tile_logic_manager;
}

static inline
Collision_Manager *get_p_collision_manager_from__world(World *p_world) {
    return &p_world->collision_manager;
}

static World_Parameters inline
*get_p_world_parameters_from__world(World *p_world) {
    return &p_world->world_parameters;
}

static Entity inline
*get_p_local_player_from__world(World *p_world) {
    return p_world->entity_manager.p_local_player;
}

static inline
Repeatable_Psuedo_Random *get_p_repeatable_psuedo_random_from__world(
        World *p_world) {
    return &p_world->repeatable_pseudo_random;
}

#endif
