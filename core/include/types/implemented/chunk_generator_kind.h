#ifndef IMPL_CHUNK_GENERATOR_KIND_H
#define IMPL_CHUNK_GENERATOR_KIND_H

#define DEFINE_CHUNK_GENERATOR_KIND

typedef enum Chunk_Generator_Kind {
/// Assign enum to same value as None to specify default generator.
    Chunk_Generator_Kind__None,
    Chunk_Generator_Kind__Overworld = Chunk_Generator_Kind__None,
    Chunk_Generator_Kind__Overworld__Plains,
    Chunk_Generator_Kind__Overworld__Forest,
    Chunk_Generator_Kind__Overworld__Mountain,
    Chunk_Generator_Kind__Overworld__Desert,
    Chunk_Generator_Kind__Overworld__Beach,
    Chunk_Generator_Kind__Overworld__Ocean,
    Chunk_Generator_Kind__Overworld__River,
    Chunk_Generator_Kind__Unknown
} Chunk_Generator_Kind;

#endif
