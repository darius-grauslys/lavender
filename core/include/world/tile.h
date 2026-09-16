#ifndef TILE_H
#define TILE_H

#include "defines_weak.h"
#include <stdbool.h>
#include <stdint.h>
#include <defines.h>

static inline 
bool is_tile__unpassable(Tile_Flags__u8 tile_flags__u8) {
    return (bool)(tile_flags__u8 & TILE_FLAGS__BIT_IS_UNPASSABLE);
}

static inline 
void set_tile__is_unpassable(Tile_Flags__u8 *p_tile_flags__u8, bool value) {
#ifndef NDEBUG
    if (!p_tile_flags__u8) {
        debug_abort("set_tile__is_unpassable, p_tile_flags__u8 == 0.");
    }
#endif
    *p_tile_flags__u8 &= ~TILE_FLAGS__BIT_IS_UNPASSABLE;
    *p_tile_flags__u8 |= (value << TILE_FLAGS__BIT_SHIFT_IS_UNPASSABLE);
}

static inline 
void set_tile__is_sight_blocking(Tile_Flags__u8 *p_tile_flags__u8, bool value) {
#ifndef NDEBUG
    if (!p_tile_flags__u8) {
        debug_abort("set_tile__is_sight_blocking, p_tile_flags__u8 == 0.");
    }
#endif
    *p_tile_flags__u8  &= ~TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
    *p_tile_flags__u8  |= (value << TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING);
}

static inline 
bool is_tile__sight_blocking(Tile_Flags__u8 tile_flags__u8) {
    return (bool)(tile_flags__u8 & TILE_FLAGS__BIT_IS_SIGHT_BLOCKING); 
}

static inline 
void set_tile__sight_blocking(Tile_Flags__u8 *p_tile_flags__u8, bool value) {
#ifndef NDEBUG
    if (!p_tile_flags__u8) {
        debug_abort("set_tile__sight_blocking, p_tile_flags__u8 == 0.");
    }
#endif
    *p_tile_flags__u8 &= ~TILE_FLAGS__BIT_IS_SIGHT_BLOCKING;
    *p_tile_flags__u8 |= (value << TILE_FLAGS__BIT_SHIFT_IS_SIGHT_BLOCKING);
}

static inline
void set_tile_kind_of__tile(
        Tile *p_tile,
        Tile_Kind the_kind_of__tile) {
#ifndef NDEBUG
    if (!p_tile) {
        debug_abort("set_tile_kind_of__tile, p_tile == 0.");
    }
#endif
    p_tile->the_kind_of__tile =
        the_kind_of__tile;
}

static inline
Tile_Kind get_tile_kind_from__tile(
        Tile *p_tile) {
#ifndef NDEBUG
    if (!p_tile) {
        debug_abort("get_tile_kind_from__tile, p_tile == 0.");
    }
#endif
    return p_tile->the_kind_of__tile;
}

static inline
bool is_tile_of__this_kind(
        Tile *p_tile,
        Tile_Kind the_kind_of__tile) {
#ifndef NDEBUG
    if (!p_tile) {
        debug_abort("is_tile_of__this_kind, p_tile == 0.");
    }
#endif
    return p_tile->the_kind_of__tile
        == the_kind_of__tile;
}

static inline
bool is_tile_kind__illegal(
        Tile_Kind the_kind_of__tile) {
    return
        the_kind_of__tile < Tile_Kind__None
        || the_kind_of__tile >= Tile_Kind__Unknown
        ;
}

#endif
