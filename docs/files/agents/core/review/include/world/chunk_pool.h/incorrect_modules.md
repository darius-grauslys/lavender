-e [1;34m./get_chunk_at__index_from__chunk_pool.md[0m
**Incorrect** — The function does not exist in the codebase. It is neither declared in `core/include/world/chunk_pool.h` nor implemented in `core/source/world/chunk_pool.c`. Only a static inline helper (`get_p_chunk_by__index_from__chunk_pool`) exists internally, but the public API function is missing entirely.
