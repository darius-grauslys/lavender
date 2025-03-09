#ifndef TEST_UTIL__VECTORS_H
#define TEST_UTIL__VECTORS_H

#include "defines_weak.h"
#include "vectors.h"

///
/// Sets all vectors to OUT_OF_BOUNDS, which is
/// needed for other test_util__vectors.h functions
/// to work properly.
///
void test_util__initialize_buffer_of__vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors);

///
/// Gives back a vector that will NOT be OUT_OF_BOUNDS.
///
Vector__3i32 test_util__get_random_vector__3i32(i32 min, i32 max);

void test_util__vector_random_walk__3i32(
        Vector__3i32 *p_vector__3i32);

///
/// Ensures that the returned vector is unqiue
/// within the given array (does not insert it
/// into the array.)
///
/// min * max
///
Vector__3i32 test_util__get_unique_vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors,
        i32 min, i32 max);

///
/// Same as above, but will insert vector into
/// the vector buffer.
///
Vector__3i32 test_util__insert_unique_vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors,
        i32 min, i32 max);

static inline
Vector__3i32 test_util__get_vector__3i32_from__vector_buffer(
        Vector__3i32 *p_vector_buffer,
        Index__u32 index_of__buffer,
        Quantity__u32 max_quantity_of__vectors) {
#ifndef NDEBUG
    if (index_of__buffer >= max_quantity_of__vectors) {
        debug_error("test_util__get_vector__3i32_from__vector_buffer, index out of bounds.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
#endif
    return p_vector_buffer[index_of__buffer];
}

#endif
