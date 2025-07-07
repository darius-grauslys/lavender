#include "world/chunk_generator_table.h"
#include "defines_weak.h"
#include "platform_defines.h"
#include "types/implemented/chunk_generator_kind.h"
#include "types/implemented/tile_kind.h"
#include "world/chunk.h"
#include "world/global_space.h"
#include "world/implemented/chunk_generator_registrar.h"
#include "defines.h"

static void _m_chunk_generator__default(
        Process *p_this_process,
        Game *p_game) {
    Global_Space *p_global_space = p_this_process->p_process_data;
    Chunk *p_chunk = get_p_chunk_from__global_space(p_global_space);
    if (!p_chunk)
        return;

#if CHUNK__DEPTH > 1
    for (Index__u16 index__z = 0;
            index__z < CHUNK__DEPTH;
            index__z++ ) {
#endif
        for (Index__u16 index__y = 0;
                index__y < CHUNK__HEIGHT;
                index__y++) {
            for (Index__u16 index__x = 0;
                    index__x < CHUNK__WIDTH;
                    index__x++) {
                Tile *p_tile = 
                    get_p_tile_from__chunk_using__u8(
                            p_chunk, 
                            index__x, 
                            index__y, 
                            index__z);

                p_tile->the_kind_of__tile =
                    Tile_Kind__None;
            }
        }
#if CHUNK__DEPTH > 1
    }
#endif
}

void initialize_chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table) {
#ifndef NDEBUG
    if (!p_chunk_generator_table) {
        debug_error("initialize_chunk_generator_table, p_chunk_generator_table == 0.");
        return;
    }
#endif
    memset(p_chunk_generator_table,
            0,
            sizeof(Chunk_Generator_Table));
    register_chunk_generator_into__chunk_generator_table(
            p_chunk_generator_table, 
            Chunk_Generator_Kind__None, 
            _m_chunk_generator__default);
    register_chunk_generators(
            p_chunk_generator_table);
}

void register_chunk_generator_into__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator,
        m_Process m_process__chunk_generator) {
#ifndef NDEBUG
    if (!p_chunk_generator_table) {
        debug_error("register_chunk_generators, p_chunk_generator_table == 0.");
        return;
    }
    if (the_kind_of__chunk_generator >= Chunk_Generator_Kind__Unknown) {
        debug_error("register_chunk_generators, the_kind_of__chunk_generator >= Unknown.");
        return;
    }
    if (!m_process__chunk_generator) {
        debug_error("register_chunk_generators, m_chunk_generator == 0.");
        return;
    }
#endif
    p_chunk_generator_table->M_process__chunk_generators[
        the_kind_of__chunk_generator] = m_process__chunk_generator;
}

m_Process get_chunk_generator_process_from__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator) {
#ifndef NDEBUG
    if (!p_chunk_generator_table) {
        debug_error("register_chunk_generators, p_chunk_generator_table == 0.");
        return 0;
    }
    if (the_kind_of__chunk_generator >= Chunk_Generator_Kind__Unknown) {
        debug_error("register_chunk_generators, the_kind_of__chunk_generator >= Unknown.");
        return 0;
    }
#endif

    return p_chunk_generator_table->M_process__chunk_generators[
        the_kind_of__chunk_generator];
}
