#ifndef WORLD_H
#define WORLD_H

#include "defines_weak.h"
#include <defines.h>

void initialize_world(
        Game *p_game,
        World *p_world);

void manage_world(
        Game *p_game,
        Graphics_Window *p_gfx_window);
void manage_world__entities(Game *p_game);

Entity *allocate_entity_into__world(
        Game *p_game,
        enum Entity_Kind the_kind_of_entity,
        Vector__3i32F4 position__3i32F4);

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
Process *load_world(Game *p_game);

Entity *get_p_entity_from__world_using__3i32F4(
        World *p_world,
        Vector__3i32F4 position__3i32F4);

void set_name_of__world(
        World *p_world,
        World_Name_String name_of__world);

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
Entity_Manager *get_p_entity_manager_from__world(World *p_world) {
    return &p_world->entity_manager;
}

static inline
Tile_Logic_Table_Manager *get_p_tile_logic_table_manager_from__world(World *p_world) {
    return &p_world->tile_logic_table_manager;
}

static inline
Chunk_Generator_Table *get_p_chunk_generation_table_from__world(World *p_world) {
    return &p_world->chunk_generator_table;
}

static inline
Global_Space_Manager *get_p_global_space_manager_from__world(
        World *p_world) { 
    return &p_world->global_space_manager;
}

static inline
Hitbox_AABB_Manager *get_p_hitbox_aabb_manager_from__world(
        World *p_world) {
    return &p_world->hitbox_aabb_manager;
}

static inline
Collision_Node_Pool *get_p_collision_node_pool_from__world(
        World *p_world) {
    return &p_world->collision_node_pool;
}

static inline
Chunk_Pool *get_p_chunk_pool_from__world(
        World *p_world) {
    return &p_world->chunk_pool;
}

static inline
Repeatable_Psuedo_Random *get_p_repeatable_psuedo_random_from__world(
        World *p_world) {
    return &p_world->repeatable_pseudo_random;
}

static inline
Graphics_Window *get_p_graphics_window_from__world(
        World *p_world) {
    return p_world->p_graphics_window_for__world;
}

#endif
