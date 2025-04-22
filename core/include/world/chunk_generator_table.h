#ifndef CHUNK_GENERATOR_TABLE_H
#define CHUNK_GENERATOR_TABLE_H

#include "defines.h"
#include "types/implemented/chunk_generator_kind.h"

void initialize_chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table);

void register_chunk_generator_into__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator,
        f_Chunk_Generator f_chunk_generator);

f_Chunk_Generator get_chunk_generator_from__chunk_generator_table(
        Chunk_Generator_Table *p_chunk_generator_table,
        Chunk_Generator_Kind the_kind_of__chunk_generator);

static inline
f_Chunk_Generator get_default_chunk_generator(
        Chunk_Generator_Table *p_chunk_generator_table) {
    return get_chunk_generator_from__chunk_generator_table(
            p_chunk_generator_table, 
            Chunk_Generator_Kind__None);
}

#endif
