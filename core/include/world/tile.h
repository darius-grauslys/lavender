#ifndef TILE_H
#define TILE_H

#include "defines_weak.h"
#include <stdbool.h>
#include <stdint.h>
#include <defines.h>

void initialize_tile(Tile *tile, 
        enum Tile_Kind kind_of_tile,
        Tile_Flags__u8 flags);

Index__u16 get_tile_sheet_index_offset_for__cover_from__wall_adjacency(
        Tile_Wall_Adjacency_Code__u16 wall_adjacency);

bool is_tile_kind__illegal(
        Tile_Kind the_kind_of__tile);

static inline Index__u16 
get_tile_sheet_index_offset_for__sprite_cover_from__wall_adjacency(
        Tile_Wall_Adjacency_Code__u16 wall_adjacency) {
    return 
        TILE_SHEET_TILE_WIDTH
        * (wall_adjacency & TILE_RENDER__WALL_ADJACENCY__SPRITE_COVER_MASK);
}

static inline 
bool does_wall_adjacency_require__vflip(
        Tile_Wall_Adjacency_Code__u16 wall_adjacency) {
    return
        (bool)(wall_adjacency
                & TILE_RENDER__WALL_ADJACENCY__BIT_VFLIP);
}

static inline 
bool is_tile__unpassable(Tile *tile) {
    return (bool)(tile->tile_flags & TILE_FLAGS__BIT_IS_UNPASSABLE);
}

static inline 
void set_tile__is_unpassable(Tile *tile, bool value) {
    tile->tile_flags &= ~TILE_FLAGS__BIT_IS_UNPASSABLE;
    tile->tile_flags |= (value << TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE);
}

static inline 
void set_tile__is_sight_blocking(Tile *tile, bool value) {
    tile->tile_flags &= ~TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
    tile->tile_flags |= (value << TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING);
}

static inline 
bool is_tile__sight_blocking(Tile *tile) {
    return (bool)(tile->tile_flags & TILE_FLAGS__BIT_IS_SIGHT_BLOCKING); 
}

static inline 
void set_tile__sight_blocking(Tile *tile, bool value) {
    tile->tile_flags &= ~TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
    tile->tile_flags |= (value << TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING);
}

static inline 
bool is_tile__container(Tile *tile) {
    return (bool)(tile->tile_flags & TILE_FLAGS__BIT_IS_CONTAINER); 
}

static inline 
void set_tile__container(Tile *tile, bool value) {
    tile->tile_flags &= ~TILE_FLAGS__BIT_IS_CONTAINER;
    tile->tile_flags |= (value << TILE_FLAGS__BIT_SHIFT_IS_CONTAINER);
}

static inline
bool is_tile_with__general_purpose_data(
        Tile *p_tile) {
    return p_tile->tile_flags
        & TILE_FLAGS__BIT_GENERAL_PURPOSE_DATA_BIT
        ;
}

static inline
void set_tile__general_purpose_data(
        Tile *p_tile,
        bool value) {
    p_tile->tile_flags &=
        ~TILE_FLAGS__BIT_GENERAL_PURPOSE_DATA_BIT;
    p_tile->tile_flags |=
        (value << TILE_FLAGS__BIT_SHIFT_GENERAL_PURPOSE_DATA_BIT);
}

static inline
void set_tile_kind_of__tile(
        Tile *p_tile,
        Tile_Kind the_kind_of__tile) {
    p_tile->the_kind_of_tile__this_tile_is =
        the_kind_of__tile;
}

static inline
Tile_Kind get_tile_kind_from__tile(
        Tile *p_tile) {
    return p_tile->the_kind_of_tile__this_tile_is;
}

static inline
bool is_tile_of__this_kind(
        Tile *p_tile,
        Tile_Kind the_kind_of__tile) {
    return p_tile->the_kind_of_tile__this_tile_is
        == the_kind_of__tile;
}

// TODO: make this PLATFORM_render_tile
// TODO: make Tile_Render_Result into PLATFORM_Tile_Render_Result
Tile_Render_Result get_tile_render_result(
        Chunk_Manager__Chunk_Map_Node *chunk_node,
        Local_Tile_Vector__3u8 local_tile_vector__3u8);

bool poll_tile_for__interaction(
        Game *p_game,
        Entity *p_entity,
        Tile_Vector__3i32 tile_vector__3i32);

bool poll_tile_for__touch(
        Game *p_game,
        Entity *p_entity,
        Tile_Vector__3i32 tile_vector__3i32);

bool attempt_tile_placement(
        Game *p_game,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32);

bool remove_tile__cover(
        Game *p_game,
        Tile_Vector__3i32 tile_vector__3i32);

bool remove_tile__ground(
        Game *p_game,
        Tile_Vector__3i32 tile_vector__3i32);

#endif
