#include "sort/heap_sort__opaque.h"
#include "defines_weak.h"

void heap_sort__opaque(
        void *p_context, // This is maybe p_game, or a manager.
        void *p_array,
        Quantity__u32 length_of__array,
        Quantity__u32 size_of__type,
        f_Sort_Heuristic__i32 f_sort_heuristic__void,
        f_Sort_Swap__Void f_sort_swap__void) {

    /// Generated with ChatGPT:

    if (length_of__array < 2) return;
    unsigned char *p_byte_array = (unsigned char*)p_array;

    // Heapify phase
    for (Quantity__u32 i = (length_of__array / 2); i-- > 0;) {
        Quantity__u32 root = i;

        while (1) {
            Quantity__u32 child = 2 * root + 1;
            if (child >= length_of__array) break;

            // Select the larger child
            if (child + 1 < length_of__array 
                    && f_sort_heuristic__void(
                        p_context,
                        &p_byte_array[size_of__type * child], 
                        &p_byte_array[size_of__type * (child + 1)]) 
                    < 0) {
                child += 1;
            }

            if (f_sort_heuristic__void(
                        p_context,
                        &p_byte_array[size_of__type * root], 
                        &p_byte_array[size_of__type * child]) 
                    < 0) {
                f_sort_swap__void(
                        p_context,
                        &p_byte_array[size_of__type * root], 
                        &p_byte_array[size_of__type * child]);
                root = child;
            } else {
                break;
            }
        }
    }

    // Sort down phase
    for (Quantity__u32 i = length_of__array - 1; i > 0; --i) {
        // Swap the root(max) with the last element
        f_sort_swap__void(p_context, p_byte_array, &p_byte_array[size_of__type * i]);

        Quantity__u32 root = 0;
        while (1) {
            Quantity__u32 child = 2 * root + 1;
            if (child >= i) break;

            if (child + 1 < i &&
                f_sort_heuristic__void(
                    p_context,
                    &p_byte_array[size_of__type * child], 
                    &p_byte_array[size_of__type * (child + 1)]) < 0) {
                child += 1;
            }

            if (f_sort_heuristic__void(
                        p_context,
                        &p_byte_array[size_of__type * root], 
                        &p_byte_array[size_of__type * child]) < 0) {
                f_sort_swap__void(
                        p_context,
                        &p_byte_array[size_of__type * root], 
                        &p_byte_array[size_of__type * child]);
                root = child;
            } else {
                break;
            }
        }
    }
}
