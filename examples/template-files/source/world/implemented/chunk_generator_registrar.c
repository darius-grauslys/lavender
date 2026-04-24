#include "world/implemented/chunk_generator_registrar.h"
#include "types/implemented/chunk_generator_kind.h"
#include "world/chunk_generator_table.h"

// GEN-INCLUDE-BEGIN
#include "world/implemented/chunk_generator__overworld.h"
// GEN-INCLUDE-END

void register_chunk_generators(
        Chunk_Generator_Table *p_chunk_generator_table) {
    // GEN-BEGIN
    register_chunk_generator_into__chunk_generator_table(
            p_chunk_generator_table, 
            Chunk_Generator_Kind__Overworld, 
            m_process__chunk_generator__overworld);
    // GEN-END
}
