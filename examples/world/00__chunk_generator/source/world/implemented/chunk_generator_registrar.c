#include "world/implemented/chunk_generator_registrar.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "process/process.h"
#include "world/chunk.h"
#include "world/chunk_generator_table.h"
#include "world/global_space.h"

// 1) Define our chunk generator.
//
// A chunk generator is a PROCESS, not a plain function: the engine
// runs one instance of it per chunk that needs generating (via the
// process manager), and hands it the chunk's global space as process
// data. That is what makes chunk generation cooperative: each chunk
// is a process that yields, so a load of 12+ chunks never blocks the
// frame.
void m_process__generate_chunk(
        Process *p_this_process,
        Game *p_game) {
    // The process data is a pointer to the global space being
    // generated.
    Global_Space *p_global_space =
        (Global_Space*)p_this_process->p_process_data;

    // The global space should have acquired its chunk from memory;
    // if not, there is nothing to fill.
    Chunk *p_chunk =
        get_p_chunk_from__global_space(p_global_space);
    if (!p_chunk) {
        debug_error("m_process__generate_chunk, p_chunk == 0.");
        fail_process(p_this_process);
        return;
    }

    // ***) A chunk is CHUNK__WIDTH x CHUNK__HEIGHT x CHUNK__DEPTH
    // tiles (8x8x8). The tile array is row-major:
    //   index = x + y * WIDTH + z * WIDTH * HEIGHT
    // Tile_Kind values map 1:1 onto the tilesheet (top-left tile =
    // index 0, left-to-right, top-to-bottom); index 0 (None) is
    // transparent, so we only ever write RED/GREEN.
    //
    // ***) The pattern: a frame. The outer ring of the chunk is
    // RED, the interior is GREEN. Every chunk in the world gets
    // the same frame, which makes it obvious at a glance that each
    // chunk was generated independently by this generator.
    //
    // ***) Yielding: Lavender is a non-preemptive task scheduler —
    // a process that monopolizes the frame stalls the game. The
    // stock contract is to fill ONE z-slice (64 tiles) per
    // invocation, persist the z cursor in the process's value
    // bytes (which persist between invocations), and return.
    // After the last slice, mark the chunk active + visually
    // updated and complete the process.
    for (Index__u8 *p_z=&p_this_process->process_value_bytes__u8[1];
            *p_z < CHUNK__DEPTH;) {
        for (Index__u8 y=0;
                y < CHUNK__HEIGHT;
                y++) {
            for (Index__u8 x=0;
                    x < CHUNK__WIDTH;
                    x++) {
                bool is_on__frame =
                    (x == 0)
                    || (x == CHUNK__WIDTH - 1)
                    || (y == 0)
                    || (y == CHUNK__HEIGHT - 1);
                p_chunk->tiles[x + y * CHUNK__WIDTH + (
                        *p_z * CHUNK__WIDTH * CHUNK__HEIGHT)]
                    .the_kind_of__tile =
                    is_on__frame
                    ? Tile_Kind__RED
                    : Tile_Kind__GREEN
                    ;
            }
        }
        (*p_z)++;
        return; // yield: 64 tile writes per process loop.
    }

    set_chunk_as__active(p_chunk);
    set_chunk_as__visually_updated(p_chunk);
    complete_process(p_this_process);
}

void register_chunk_generators(
        Chunk_Generator_Table *p_chunk_generator_table) {
    // 2) Register the chunk generator. Chunk_Generator_Kind__None
    // is the DEFAULT kind: any chunk generation request that does
    // not name a specific kind uses this generator. (A game with
    // multiple biomes would register one generator per kind and
    // request the kind per global space.)
    register_chunk_generator_into__chunk_generator_table(
            p_chunk_generator_table,
            Chunk_Generator_Kind__None,
            m_process__generate_chunk);
}
