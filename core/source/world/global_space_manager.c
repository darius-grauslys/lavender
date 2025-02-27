#include "world/global_space_manager.h"
#include "defines.h"
#include "defines_weak.h"
#include "game.h"
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

static inline
Identifier__u64 get_uuid_for__global_space(
        Chunk_Vector__3i32 chunk_vector__3i32) {
    return
            (uint64_t)(MASK(24) & chunk_vector__3i32.x__i32)
            | ((uint64_t)(MASK(24) & chunk_vector__3i32.y__i32) << 24)
            | ((uint64_t)(MASK(16) & chunk_vector__3i32.z__i32) << 48)
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
        Global_Space_Manager *p_global_space_manager,
        m_Process m_process__construct_global_space,
        m_Process m_process__destruct_global_space) {
    initialize_serialization_header__contiguous_array__uuid_64(
            (Serialization_Header__UUID_64*)
                p_global_space_manager->global_spaces, 
            QUANTITY_OF__GLOBAL_SPACE, 
            sizeof(Global_Space));
    p_global_space_manager->m_process__construct_global_space =
        m_process__construct_global_space;
    p_global_space_manager->m_process__destruct_global_space =
        m_process__destruct_global_space;
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
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Chunk_Vector__3i32 local_space_vector__3i32) {
#ifndef NDEBUG
    if (!p_global_space_manager->m_process__construct_global_space) {
        debug_abort("hold_global_space_within__global_space_manager, m_process__construct_global_space == 0.");
        return 0;
    }
#endif

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

    Process *p_process = 
        run_process(
                p_process_manager, 
                p_global_space_manager
                ->m_process__construct_global_space, 
                PROCESS_FLAG__IS_CRITICAL);

    if (!p_process) {
        debug_error("hold_global_space_within__global_space_manager, failed to allocate process.");
        return 0;
    }

    set_global_space_as__constructing(p_global_space);
    p_process->p_process_data = p_global_space;

    return p_global_space;
}

void drop_global_space_within__global_space_manager(
        Global_Space_Manager *p_global_space_manager,
        Process_Manager *p_process_manager,
        Global_Space *p_global_space) {
#ifndef NDEBUG
    if (!p_global_space_manager->m_process__destruct_global_space) {
        debug_abort("hold_global_space_within__global_space_manager, m_process__destruct_global_space == 0.");
        return;
    }
#endif
    if (!drop_global_space(p_global_space)) {
        return;
    }
    Process *p_process =
        run_process(
            p_process_manager,
            p_global_space_manager
            ->m_process__destruct_global_space, 
            PROCESS_FLAG__IS_CRITICAL);

    if (!p_process) {
        debug_error("drop_global_space_within__global_space_manager, failed to allocate process.");
        return;
    }

    p_process->p_process_data = p_global_space;
    set_global_space_as__deconstructing(p_global_space);
}
