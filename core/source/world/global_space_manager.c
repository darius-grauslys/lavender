#include "world/global_space_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "game_action/implemented/global_space/game_action__global_space__request.h"
#include "game_action/implemented/global_space/game_action__global_space__store.h"
#include "numerics.h"
#include "platform_defines.h"
#include "process/process.h"
#include "process/process_manager.h"
#include "serialization/hashing.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "vectors.h"
#include "world/global_space.h"

#define BIT_MASK__GLOBAL_SPACE__0_XY__u24 0b101010101010101010101010
#define BIT_MASK__GLOBAL_SPACE__1_XY__u24 0b010101010101010101010101

#define BIT_MASK__GLOBAL_SPACE__0_Z__u8 MASK(8)
#define BIT_MASK__GLOBAL_SPACE__1_Z__u8 (MASK(8) << 7)

static inline
Identifier__u64 get_uuid_for__global_space(
        Chunk_Vector__3i32 chunk_vector__3i32) {
    return
            (uint64_t)((BIT_MASK__GLOBAL_SPACE__0_XY__u24 & chunk_vector__3i32.x__i32)
                    | (BIT_MASK__GLOBAL_SPACE__1_XY__u24 & chunk_vector__3i32.y__i32))
            | (((uint64_t)(BIT_MASK__GLOBAL_SPACE__1_XY__u24 & chunk_vector__3i32.x__i32)
                    | (BIT_MASK__GLOBAL_SPACE__0_XY__u24 & chunk_vector__3i32.y__i32)) << 32)
            | ((uint64_t)(BIT_MASK__GLOBAL_SPACE__0_Z__u8 & chunk_vector__3i32.z__i32) << 24)
            | ((uint64_t)(BIT_MASK__GLOBAL_SPACE__1_Z__u8 & chunk_vector__3i32.z__i32) << 56)
            ;
}

static inline
Global_Space *get_p_global_space_by__index_from__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Index__u32 index_of__global_space) {
#ifndef NDEBUG
    if (index_of__global_space >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("get_p_global_space_by__index_from__global_space_manager, index out of range: %d/%d",
                index_of__global_space,
                QUANTITY_OF__GLOBAL_SPACE);
        return 0;
    }
#endif
    return &p_global_space_manager
        ->global_spaces[index_of__global_space];
}

void initialize_global_space_manager(
        Global_Space_Manager *p_global_space_manager) {
    initialize_serialization_header__contiguous_array__uuid_64(
            (Serialization_Header__UUID_64*)
                p_global_space_manager->global_spaces, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Global_Space));
}

Global_Space *dehash_global_space_from__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32) {
    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                chunk_vector__3i32);
    if (!is_global_space__allocated(p_global_space)) {
        return 0;
    }
    if (is_vectors_3i32__equal(
                chunk_vector__3i32, 
                p_global_space->chunk_vector__3i32)) {
        return p_global_space;
    }

    // hash missed, brute force search.
    Index__u32 start_index =
        p_global_space
        - p_global_space_manager
        ->global_spaces
        ;
    for (Index__u32 index_of__global_space = 
                (start_index+1 % QUANTITY_OF__GLOBAL_SPACE);
            index_of__global_space != start_index;
            index_of__global_space = 
                (index_of__global_space+1 % QUANTITY_OF__GLOBAL_SPACE)) {
        p_global_space = 
            get_p_global_space_by__index_from__global_space_manager(
                    p_global_space_manager, 
                    index_of__global_space);
        if (!is_global_space__allocated(
                    p_global_space)) {
            return 0;
        }
        if (is_vectors_3i32__equal(
                    chunk_vector__3i32, 
                    p_global_space->chunk_vector__3i32)) {
            return p_global_space;
        }
    }
    return 0;
}

Global_Space *allocate_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 chunk_vector__3i32) {
    Identifier__u64 uuid_64 =
        get_uuid_for__global_space(chunk_vector__3i32);
    Global_Space *p_global_space =
        (Global_Space*)dehash_identitier_u64_in__contigious_array(
                (Serialization_Header__UUID_64*)
                    &p_global_space_manager->global_spaces, 
                QUANTITY_OF__GLOBAL_SPACE, 
                uuid_64);
    if (!p_global_space || is_global_space__allocated(p_global_space)) {
        debug_error("allocate_global_space_in__global_space_manager, failed to allocate a global_space.");
        return 0;
    }

    initialize_global_space_as__allocated(
            p_global_space,
            uuid_64);
    return p_global_space;
}

void release_global_space_in__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Global_Space *p_global_space) {
#ifndef NDEBUG
    u32 index = p_global_space
        - p_global_space_manager->global_spaces;
    if (index >= QUANTITY_OF__GLOBAL_SPACE) {
        debug_error("release_global_space_in__global_space_manager, p_global_space was not allocated with this manager.");
        return;
    }
    if (p_global_space->p_chunk) {
        debug_error("release_global_space_in__global_space_manager, p_chunk must be null here.");
        return;
    }
    if (p_global_space->p_collision_node) {
        debug_error("release_global_space_in__global_space_manager, p_collision_node must be null here.");
        return;
    }
#endif

    initialize_global_space(p_global_space);
}

Global_Space *get_p_global_space_from__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Chunk_Vector__3i32 local_space_vector__3i32) {
    Global_Space *p_global_space = 
        (Global_Space*)dehash_identitier_u64_in__contigious_array(
            (Serialization_Header__UUID_64*)
                &p_global_space_manager->global_spaces, 
            QUANTITY_OF__GLOBAL_SPACE, 
            get_uuid_for__global_space(local_space_vector__3i32));
    if (!is_global_space__allocated(p_global_space))
        return 0;

    return p_global_space;
}

Global_Space *hold_global_space_within__global_space_manager(
        Game *p_game,
        Chunk_Vector__3i32 local_space_vector__3i32) {
    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__game(p_game);

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                local_space_vector__3i32);
    if (p_global_space) {
        hold_global_space(p_global_space);
        return p_global_space;
    }

    p_global_space =
        allocate_global_space_in__global_space_manager(
                p_global_space_manager,
                local_space_vector__3i32);
    if (!p_global_space) {
        debug_error("hold_global_space_within__global_space_manager, failed to allocate p_global_space.");
        return 0;
    }

    hold_global_space(p_global_space);

    bool is_dispatch__successful = 
        dispatch_game_action__global_space__request(
                p_game, 
                local_space_vector__3i32);

    if (!is_dispatch__successful) {
        debug_error("hold_global_space_within__global_space_manager, failed to dispatch process.");
        return 0;
    }

    set_global_space_as__constructing(p_global_space);

    return p_global_space;
}

void drop_global_space_within__global_space_manager(
        Game *p_game,
        Chunk_Vector__3i32 local_space_vector__3i32) {
    Global_Space_Manager *p_global_space_manager =
        get_p_global_space_manager_from__game(p_game);

    Global_Space *p_global_space =
        get_p_global_space_from__global_space_manager(
                p_global_space_manager, 
                local_space_vector__3i32);
    if (!p_global_space) {
        debug_error("drop_global_space_within__global_space_manager, p_global_space == 0.");
        return;
    }

    if (!drop_global_space(p_global_space)) {
        return;
    }

    bool is_dispatch__successful =
        dispatch_game_action__global_space__store(
                p_game, 
                local_space_vector__3i32);

    if (!is_dispatch__successful) {
        debug_error("drop_global_space_within__global_space_manager, failed to dispatch process.");
        return;
    }

    set_global_space_as__deconstructing(p_global_space);
}
