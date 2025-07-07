#ifndef CHUNK_GENERATOR_TABLE_H
#define CHUNK_GENERATOR_TABLE_H

#include "defines.h"
#include "types/implemented/chunk_generator_kind.h"

void initialize_chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table);

void register_chunk_generator_into__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator,
        m_Process m_process__chunk_generator);

m_Process get_chunk_generator_process_from__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator);

static inline
m_Process get_default_chunk_generator_process(
        Chunk_Generator_Table *p_chunk_generator_table) {
    return get_chunk_generator_process_from__chunk_generator_table(
            p_chunk_generator_table, 
            Chunk_Generator_Kind__None);
}

#endif
