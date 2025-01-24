#ifndef TILE_LOGIC_RECORD_H
#define TILE_LOGIC_RECORD_H

#include <defines.h>

#define TILE_LOGIC_RECORD(\
        f_tile_handler__touch,\
        f_tile_handler__place,\
        f_tile_handler__destroy,\
        tile_logic_flags__u8)\
            (Tile_Logic_Record){\
                f_tile_handler__touch,\
                f_tile_handler__place,\
                f_tile_handler__destroy,\
                tile_logic_flags__u8,\
            }

void initialize_tile_logic_record(
        Tile_Logic_Record *p_tile_logic_record,
        f_Tile_Handler__Touch f_tile_handler__touch,
        f_Tile_Handler__Place f_tile_handler__place,
        f_Tile_Handler__Destroy f_tile_handler__destroy,
        Tile_Logic_Flags__u8 tile_logic_flags__u8);

static inline
void initialize_tile_logic_record_as__unused(
        Tile_Logic_Record *p_tile_logic_record) {
    initialize_tile_logic_record(
            p_tile_logic_record,
            0, 0, 0,
            TILE_LOGIC_FLAGS__NONE);
}

static inline
bool is_tile_logic_record__unpassable(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record->tile_logic_flags__u8
        & TILE_LOGIC_FLAG__IS_UNPASSABLE
        ;
}

static inline
bool is_tile_logic_record__sight_blocking(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record->tile_logic_flags__u8
        & TILE_LOGIC_FLAG__IS_SIGHT_BLOCKING
        ;
}

static inline
void invoke_tile_logic_record__touch(
        Tile_Logic_Record *p_tile_logic_record,
        Game *p_game,
        Tile *p_tile,
        Tile_Vector__3i32 tile_vector__3i32,
        Entity *p_entity) {
    p_tile_logic_record
        ->f_tile_handler__touch(
                p_game,
                p_tile,
                tile_vector__3i32,
                p_entity);
}

static inline
bool invoke_tile_logic_record__place(
        Tile_Logic_Record *p_tile_logic_record,
        Game *p_game,
        Tile *p_tile,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32) {
    return p_tile_logic_record
        ->f_tile_handler__place(
                p_game,
                p_tile,
                the_kind_of__tile,
                tile_vector__3i32);
}

static inline
bool invoke_tile_logic_record__destroy(
        Tile_Logic_Record *p_tile_logic_record,
        Game *p_game,
        Tile *p_tile,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32) {
    return p_tile_logic_record
        ->f_tile_handler__destroy(
                p_game,
                p_tile,
                the_kind_of__tile,
                tile_vector__3i32);
}

static inline
bool is_tile_logic_record_possessing__touch(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record->f_tile_handler__touch;
}

static inline
bool is_tile_logic_record_possessing__place(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record->f_tile_handler__place;
}

static inline
bool is_tile_logic_record_possessing__destroy(
        Tile_Logic_Record *p_tile_logic_record) {
    return p_tile_logic_record->f_tile_handler__destroy;
}

#endif
