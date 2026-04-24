#ifndef TILE_LOGIC_RECORD_H
#define TILE_LOGIC_RECORD_H

#include "defines.h"

static inline
bool is_tile_logic_record__unpassable(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 
        & TILE_LOGIC_FLAG__IS_UNPASSABLE
        ;
}

static inline
bool set_tile_logic_record_as__unpassable(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 |=
        TILE_LOGIC_FLAG__IS_UNPASSABLE
        ;
}

static inline
bool set_tile_logic_record_as__passable(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 &=
        ~TILE_LOGIC_FLAG__IS_UNPASSABLE
        ;
}

static inline
bool is_tile_logic_record__sight_blocking(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 
        & TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING
        ;
}

static inline
bool set_tile_logic_record_as__sight_blocking(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 |= 
        TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING
        ;
}

static inline
bool set_tile_logic_record_as__NOT_sight_blocking(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 &= 
        ~TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING
        ;
}

static inline
bool is_tile_logic_record__without_ground(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 
        & TILE_LOGIC_FLAG__IS_WITHOUT_GROUND
        ;
}

static inline
bool set_tile_logic_record_as__without_ground(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 |=
        TILE_LOGIC_FLAG__IS_WITHOUT_GROUND
        ;
}

static inline
bool set_tile_logic_record_as__with_ground(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record
        ->tile_logic_flags__u8 &=
        ~TILE_LOGIC_FLAG__IS_WITHOUT_GROUND
        ;
}

#endif
