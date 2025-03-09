#include "test_util__vectors.h"
#include "defines.h"
#include "defines_weak.h"
#include "test_util.h"
#include "test_util__log.h"
#include "vectors.h"
#include "munit.h"

static inline
void test_util__validate_min_max(
        i32 *p_min,
        i32 *p_max) {
    if (*p_min > *p_max) {
        i32 min_tmp = *p_min;
        *p_min = *p_max;
        *p_max = min_tmp;
    }
}

void test_util__initialize_buffer_of__vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors) {
    for (Index__u32 index_of__vector = 0;
            index_of__vector < max_quantity_of__vectors;
            index_of__vector++) {
        p_vector_buffer[index_of__vector] =
            VECTOR__3i32__OUT_OF_BOUNDS;
    }
}

Vector__3i32 test_util__get_random_vector__3i32(i32 min, i32 max) {
    test_util__validate_min_max(&min, &max);
    Vector__3i32 vec__3i32 =
        get_vector__3i32(
                munit_rand_int_range(min, max), 
                munit_rand_int_range(min, max), 
                munit_rand_int_range(min, max));

    if (is_vectors_3i32__out_of_bounds(vec__3i32)) {
        test_util__vector_random_walk__3i32(
                &vec__3i32);
    }
    
    return vec__3i32;
}

void test_util__vector_random_walk__3i32(
        Vector__3i32 *p_vector__3i32) {
    switch (munit_rand_int_range(0, 3)) {
        case 0:
            p_vector__3i32->x__i32++;
            break;
        case 1:
            p_vector__3i32->y__i32++;
            break;
        case 2:
            p_vector__3i32->z__i32++;
            break;
    }
}

Vector__3i32 test_util__get_unique_vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors,
        i32 min, i32 max) {
    test_util__validate_min_max(&min, &max);
    if (((u32)max -(u32)min) * ((u32)max -(u32)min) <= max_quantity_of__vectors) {
        test_util__log("test_util__get_unique_vector__3i32, bad args.");
        return VECTOR__3i32__OUT_OF_BOUNDS;
    }
    Vector__3i32 vector__returning__3i32 = 
        test_util__get_random_vector__3i32(min, max);
    for (Index__u32 index_of__vector = 0;
            index_of__vector < max_quantity_of__vectors;
            index_of__vector++) {
        Vector__3i32 vector__3i32 =
            test_util__get_vector__3i32_from__vector_buffer(
                    p_vector_buffer, 
                    index_of__vector, 
                    max_quantity_of__vectors);
        if (is_vectors_3i32__equal(
                    vector__3i32, 
                    vector__returning__3i32)) {
            test_util__vector_random_walk__3i32(
                    &vector__returning__3i32);
            index_of__vector = 0;
        }
        if (is_vectors_3i32__out_of_bounds(
                    vector__3i32)) {
            break;
        }
    }

    return vector__returning__3i32;
}

Vector__3i32 test_util__insert_unique_vector__3i32(
        Vector__3i32 *p_vector_buffer,
        Quantity__u32 max_quantity_of__vectors,
        i32 min, i32 max) {
    Vector__3i32 *p_vector_insert__3i32 = 0;
    for (Index__u32 index_of__vector = 0;
            index_of__vector < max_quantity_of__vectors;
            index_of__vector++) {
        Vector__3i32 vec__3i32 = 
            test_util__get_vector__3i32_from__vector_buffer(
                    p_vector_buffer, 
                    index_of__vector, 
                    max_quantity_of__vectors);
        if (is_vectors_3i32__out_of_bounds(vec__3i32)) {
            p_vector_insert__3i32 = &p_vector_buffer[index_of__vector];
            break;
        }
    }

    Vector__3i32 vector__returning__3i32 =
        test_util__get_unique_vector__3i32(
                p_vector_buffer, 
                max_quantity_of__vectors, 
                min, 
                max);

    if (p_vector_insert__3i32) {
        *p_vector_insert__3i32 = vector__returning__3i32;
    } else {
        test_util__log("test_util__insert_unique_vector__3i32, p_vector_insert__3i32 == 0.");
    }

    return vector__returning__3i32;
}
