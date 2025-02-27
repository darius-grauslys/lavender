#include "defines_weak.h"
#include "game.h"
#include "platform.h"
#include "world/chunk.h"
#include "world/tile_logic_manager.h"
#include "world/tile_logic_record.h"
#include "world/world.h"
#include <world/tile.h>
#include <defines.h>
#include <vectors.h>

void initialize_tile(Tile *tile, 
        enum Tile_Kind kind_of_tile,
        Tile_Flags__u8 flags) {
    tile->tile_flags = flags;
    tile->the_kind_of_tile__this_tile_is =
        kind_of_tile;
}

Index__u16 get_tile_sheet_index_offset_for__cover_from__wall_adjacency(
        Tile_Wall_Adjacency_Code__u16 wall_adjacency) {
    return 
        TILE_SHEET_TILE_WIDTH
        * (4
        * (1 + (wall_adjacency & TILE_RENDER__WALL_ADJACENCY__COVER_MASK))
        - 1)
        ;
}

bool is_tile_kind__illegal(
        Tile_Kind the_kind_of__tile) {
    return
        the_kind_of__tile < Tile_Kind__None
        || the_kind_of__tile >= Tile_Kind__Unknown
        ;
}

static inline 
Tile *get_p_tile_from__chunk_node_for__tile_render(
        Chunk_Manager__Chunk_Map_Node *p_chunk_node,
        Local_Tile_Vector__3u8 local_tile_vector__3u8,
        Tile_Render_Result *p_render_result) {
//     Index__u8 x__local = local_tile_vector__3u8.x__u8;
//     Index__u8 y__local = local_tile_vector__3u8.y__u8;
//     Tile *p_tile =
//         get_p_tile_from__chunk_node(
//                 p_chunk_node,
//                 local_tile_vector__3u8);
// 
//     Tile *p_north, *p_east, *p_south, *p_west;
// 
//     //TODO: this is a pretty glaring problem
//     //with how the chunk_nodes are connected
//     p_north =
//         (y__local == 0)
//         ? get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node->p_north__chunk_map_node,
//                 x__local, 
//                 CHUNK_WIDTH__IN_TILES - 1)
//         : get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node,
//                 x__local, 
//                 y__local - 1)
//         ;
//     p_south =
//         (y__local == CHUNK_WIDTH__IN_TILES - 1)
//         ? get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node->p_south__chunk_map_node,
//                 x__local, 
//                 0)
//         : get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node,
//                 x__local, 
//                 y__local + 1)
//         ;
//     p_west =
//         (x__local == 0)
//         ? get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node->p_west__chunk_map_node,
//                 CHUNK_WIDTH__IN_TILES - 1, y__local)
//         : get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node,
//                 x__local - 1, 
//                 y__local)
//         ;
//     p_east =
//         (x__local == CHUNK_WIDTH__IN_TILES - 1)
//         ? get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node->p_east__chunk_map_node,
//                 0, 
//                 y__local)
//         : get_p_tile_from__chunk_node_using__u8(
//                 p_chunk_node,
//                 x__local + 1, 
//                 y__local)
//         ;
// 
//     Tile_Wall_Adjacency_Code__u16 wall_adjacency = 0;
// #warning [***] preserver wall adjacency code
//     // if (is_tile_cover__a_wall(p_north->the_kind_of_tile_cover__this_tile_has)) {
//     //     wall_adjacency +=
//     //         TILE_RENDER__WALL_ADJACENCY__NORTH;
//     // }
//     // if (is_tile_cover__a_wall(p_east->the_kind_of_tile_cover__this_tile_has)) {
//     //     wall_adjacency +=
//     //         TILE_RENDER__WALL_ADJACENCY__EAST;
//     // }
//     // if (is_tile_cover__a_wall(p_south->the_kind_of_tile_cover__this_tile_has)) {
//     //     wall_adjacency +=
//     //         TILE_RENDER__WALL_ADJACENCY__SOUTH;
//     // }
//     // if (is_tile_cover__a_wall(p_west->the_kind_of_tile_cover__this_tile_has)) {
//     //     wall_adjacency +=
//     //         TILE_RENDER__WALL_ADJACENCY__WEST;
//     // }
// 
//     p_render_result->wall_adjacency = wall_adjacency;
// 
//     return p_tile;
    return 0;
}

static inline 
void get_tile_texture_sheet_index(
        Tile *p_tile,
        Tile_Render_Result *p_render_result) {
    switch (p_tile->the_kind_of_tile__this_tile_is) {
        default:
            p_render_result->tile_index__ground =
                (uint32_t)p_tile->the_kind_of_tile__this_tile_is;
            return;
    }
tile_structure:
    ;
    uint32_t index = 0;
    switch (p_tile->the_kind_of_tile__this_tile_is) {
        default:
			break;
    }
    //TODO: look into why we have to add 1.
    index += 1;
    p_render_result->tile_index__ground = index;
}

// TODO: prim wrap
// TODO: move this to nds
Tile_Render_Result get_tile_render_result(
        Chunk_Manager__Chunk_Map_Node *p_chunk_node,
        Local_Tile_Vector__3u8 local_tile_vector__3u8) {
    Tile_Render_Result render_result;
    return render_result;
}

bool poll_tile_for__touch(
        Game *p_game,
        Entity *p_entity,
        Tile_Vector__3i32 tile_vector__3i32) {
    debug_abort("poll_tile_for__touch, impl");
    // Tile *p_tile = 
    //     get_p_tile_from__chunk_manager_with__tile_vector_3i32(
    //             get_p_chunk_manager_from__game(p_game),
    //             tile_vector__3i32);

    // Tile_Logic_Manager *p_tile_logic_manager =
    //     get_p_tile_logic_manager_from__world(
    //             get_p_world_from__game(p_game));

    // Tile_Logic_Record *p_tile_logic_record =
    //     get_p_tile_logic_record_for__ground_kind_from__tile_logic_manager(
    //             p_tile_logic_manager, 
    //             get_tile_kind_from__tile(p_tile));

    // if (p_tile_logic_record
    //         && is_tile_logic_record_possessing__touch(
    //             p_tile_logic_record)) {
    //     invoke_tile_logic_record__touch(
    //             p_tile_logic_record,
    //             p_game,
    //             p_tile,
    //             tile_vector__3i32,
    //             p_entity);
    //             
    //     return true;
    // }

    return false;
}

bool attempt_tile_placement_for__this_tile_logic_record(
        Tile_Logic_Record *p_tile_logic_record,
        Game *p_game,
        Tile *p_tile,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32) {
    bool is_placement__successful = true;
    if (p_tile_logic_record
            && is_tile_logic_record_possessing__place(
                p_tile_logic_record)) {
        is_placement__successful = invoke_tile_logic_record__place(
                p_tile_logic_record, 
                p_game, 
                p_tile, 
                the_kind_of__tile,
                tile_vector__3i32);
    } else if (the_kind_of__tile
            != Tile_Kind__None) {
        set_tile_kind_of__tile(
                p_tile, 
                the_kind_of__tile);
    } else {
        return false;
    }

    return is_placement__successful;
}

bool attempt_tile_placement__ground(
        Game *p_game,
        Tile *p_tile,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32) {
    Tile_Logic_Record *p_tile_logic_record =
        get_p_tile_logic_record_for__ground_kind_from__tile_logic_manager(
                get_p_tile_logic_manager_from__world(
                    get_p_world_from__game(p_game)), 
                the_kind_of__tile);

    if (!is_tile_of__this_kind(
                p_tile,
                Tile_Kind__None)) {
        return false;
    }

    bool is_placement__successful =
        attempt_tile_placement_for__this_tile_logic_record(
            p_tile_logic_record, 
            p_game, 
            p_tile, 
            the_kind_of__tile, 
            tile_vector__3i32);

    if (is_placement__successful) {
        set_tile__is_unpassable( // TODO: passability rules
                p_tile, 
                false);
    }

    return is_placement__successful;
}

bool attempt_tile_placement(
        Game *p_game,
        Tile_Kind the_kind_of__tile,
        Tile_Vector__3i32 tile_vector__3i32) {
    debug_abort("attempt_tile_placement, impl");
    return false;
    // Tile *p_tile = 
    //     get_p_tile_from__chunk_manager_with__tile_vector_3i32(
    //             get_p_chunk_manager_from__game(p_game),
    //             tile_vector__3i32);

    // if (!p_tile)
    //     return false;

    // bool is_placing__ground_or_cover =
    //     the_kind_of__tile != Tile_Kind__None;

    // Tile_Logic_Record *p_tile_logic_record = 0;
    // if (is_placing__ground_or_cover) {
    //     p_tile_logic_record =
    //         get_p_tile_logic_record_for__ground_kind_from__tile_logic_manager(
    //                 get_p_tile_logic_manager_from__world(
    //                     get_p_world_from__game(p_game)), 
    //                 the_kind_of__tile);
    // } else {
    // }

    // if (!p_tile_logic_record)
    //     return false;

    // bool result_of__placement = false;
    // if (is_tile_logic_record_possessing__place(
    //             p_tile_logic_record)) {
    //     result_of__placement = 
    //         invoke_tile_logic_record__place(
    //             p_tile_logic_record, 
    //             p_game, 
    //             p_tile, 
    //             the_kind_of__tile, 
    //             tile_vector__3i32);        
    // } else {
    // }

    // if (result_of__placement) {
    //     determine_tile_flags(
    //             get_p_tile_logic_manager_from__world(
    //                 get_p_world_from__game(p_game)), 
    //             p_tile);
    // }

    // return result_of__placement;
}

bool remove_tile__ground(
        Game *p_game,
        Tile_Vector__3i32 tile_vector__3i32) {
    debug_abort("remove_tile__ground, impl");
    return false;
    // Tile *p_tile = 
    //     get_p_tile_from__chunk_manager_with__tile_vector_3i32(
    //             get_p_chunk_manager_from__game(p_game),
    //             tile_vector__3i32);

    // Tile_Logic_Record *p_logic_record =
    //     get_p_tile_logic_record_for__ground_kind_from__tile_logic_manager(
    //             get_p_tile_logic_manager_from__world(
    //                 get_p_world_from__game(p_game)), 
    //             get_tile_kind_from__tile(p_tile));

    // if (!p_logic_record
    //         || !is_tile_logic_record_possessing__destroy(
    //             p_logic_record)) {
    //     set_tile_kind_of__tile(
    //             p_tile, 
    //             Tile_Kind__None);
    // } else {
    //     if (!invoke_tile_logic_record__destroy(
    //             p_logic_record, 
    //             p_game, 
    //             p_tile, 
    //             get_tile_kind_from__tile(p_tile), 
    //             tile_vector__3i32)) {
    //         return false;
    //     }
    // }

    // determine_tile_flags(
    //         get_p_tile_logic_manager_from__world(
    //             get_p_world_from__game(p_game)), 
    //         p_tile);

    // update_chunk_at__tile_vector__3i32(
    //         p_game, 
    //         tile_vector__3i32);
    // return true;
}
