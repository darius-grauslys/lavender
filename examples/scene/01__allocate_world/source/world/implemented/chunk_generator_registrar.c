#include "world/implemented/chunk_generator_registrar.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "process/process.h"
#include "world/chunk.h"
#include "world/chunk_generator_table.h"
#include "world/global_space.h"

// 1) Define our chunk generator.
void m_process__generate_chunk(
        Process *p_this_process,
        Game *p_game) {
    // We can assume our process_data is a pointer
    // to a global space.
    Global_Space *p_global_space =
        (Global_Space*)p_this_process->p_process_data;

    // Make sure our global space managed to acquire a
    // chunk from memory.
    Chunk *p_chunk =
        get_p_chunk_from__global_space(p_global_space);
    if (!p_chunk) {
        debug_error("m_process__chunk_generator__castle, p_chunk == 0.");
        fail_process(p_this_process);
        return;
    }

    // We can use process data holding fields (always init to 0)
    // to persist state between process invocations.
    //
    // Lavender is a non-preemptive task scheduling game engine.
    // So it is our responsibility to not take too much time in
    // a process.
    //
    // Generally, for 8x8x8 we don't need to do this.
    // For educational purposes we demonstrate it here.
    for (Index__u8 *p_z=&p_this_process->process_value_bytes__u8[1];
            *p_z < CHUNK__DEPTH;) {
        for (Index__u8 y=0;
                y < CHUNK__HEIGHT;
                y++) {
            for (Index__u8 x=0;
                    x < CHUNK__WIDTH;
                    x++) {
                p_chunk->tiles[x + y * CHUNK__WIDTH + (
                        *p_z * CHUNK__WIDTH * CHUNK__HEIGHT)]
                    .the_kind_of__tile =
                    ((x + (y % 2)) % 2)
                    ? Tile_Kind__RED
                    : Tile_Kind__GREEN
                    ;
            }
        }
        (*p_z)++;
        return; // yield the process 64 ops per process loop.
    }

    set_chunk_as__active(p_chunk);
    set_chunk_as__visually_updated(p_chunk);
    complete_process(p_this_process);
}

void register_chunk_generators(
        Chunk_Generator_Table *p_chunk_generator_table) {
    // 2) Register our chunk generator
    register_chunk_generator_into__chunk_generator_table(
            p_chunk_generator_table, 
            Chunk_Generator_Kind__None, 
            m_process__generate_chunk);
}
