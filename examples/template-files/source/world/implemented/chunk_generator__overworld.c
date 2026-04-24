#include "world/implemented/chunk_generator__overworld.h"
#include "defines.h"
#include "game.h"
#include "world/global_space.h"
#include "world/global_space_manager.h"
#include "process/process.h"


// GEN-WORKSPACE-BEGIN
// GEN-WORKSPACE-END

i32 get_natural_world_height_at__xy_for__overworld(
        Repeatable_Psuedo_Random *p_random,
        i32 x,
        i32 y) {
    // GEN-HEIGHT-BEGIN
    return 0;
    // GEN-HEIGHT-END
}

// GEN-FORWARD-BEGIN
void m_process__chunk_generator__post_process(
        Process *p_this_process,
        Game *p_game);
// GEN-FORWARD-END

void m_process__chunk_generator__overworld(
        Process *p_this_process,
        Game *p_game) {
    Global_Space *p_global_space = p_this_process->p_process_data;
    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);
    Chunk_Vector__3i32 chunk_pos = p_global_space->chunk_vector__3i32;

    switch (p_this_process->process_value_bytes__u8[0]) {
        default:
        case Chunk_Generation__State__Terrain:
            break;
        case Chunk_Generation__State__Awaiting_Neighbors:
            p_this_process->process_value_bytes__u8[1] =
                poll_global_space_neighbors(
                        p_game, 
                        p_global_space);

            if (p_this_process->process_value_bytes__u8[1]
                    != (u8)-1) {
                // never timeout, but check for awaiting deconstruction
                if (is_global_space__awaiting_deconstruction(
                            p_global_space)) {
                    complete_process(p_this_process);
                }
                return;
            }

            p_this_process->m_process_run__handler =
                m_process__chunk_generator__post_process;
            return;
    }

    // GEN-MAIN-BEGIN
    // GEN-MAIN-END

    set_global_space_as__finished_terrain(p_global_space);
    p_this_process->process_value_bytes__u8[0] =
        Chunk_Generation__State__Awaiting_Neighbors;
}

void m_process__chunk_generator__post_process(
        Process *p_this_process,
        Game *p_game) {
    Global_Space_Manager *p_global_space_manager = 
        get_p_global_space_manager_from__game(p_game);
    Global_Space *p_global_space = p_this_process->p_process_data;
    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);

    p_this_process->process_value_bytes__u8[1] =
        poll_global_space_neighbors(
                p_game, 
                p_global_space);

    if (is_global_space__awaiting_deconstruction(
                p_global_space)
        || (p_this_process->process_value_bytes__u8[1]
            != (u8)-1)) {
        complete_process(p_this_process);
        return;
    }

    // NOTE: Be sure to include the following if these chunks
    // NOTE: have been modified.
    //
    // set_chunk_as__visually_updated(ptr_array_of__chunk__neighbors[1]);
    // set_chunk_as__visually_updated(ptr_array_of__chunk__neighbors[3]);
    // set_chunk_as__visually_updated(ptr_array_of__chunk__neighbors[4]);
    // set_chunk_as__visually_updated(ptr_array_of__chunk__neighbors[6]);

    // GEN-POST-BEGIN
    // GEN-POST-END

    set_chunk_as__active(p_chunk);
    complete_process(p_this_process);
}
