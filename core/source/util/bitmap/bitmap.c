#include "util/bitmap/bitmap.h"
#include "defines.h"
#include "platform.h"

void initialize_bitmap(
        u8 *p_bitmap,
        bool state,
        Quantity__u32 size_of__bitmap) {
    memset(p_bitmap,
            state ? 0xff : 0x00,
            size_of__bitmap);
}

Index__u32 get_index_of__first_set_bit_from__bitmap_and_heap(
        u8 *p_bitmap_and_heap,
        Quantity__u32 size_of__bitmap_but_NOT__including_heap) {
    u8 *p_heap = &p_bitmap_and_heap[
        size_of__bitmap_but_NOT__including_heap];
    Index__u32 index = 0;
    Quantity__u32 range = size_of__bitmap_but_NOT__including_heap >> 3;
    do {
        if (!*p_heap) break;
        for (Index__u8 index_of__bit = 0;
                index_of__bit < 8;
                index_of__bit++) {
            if (*p_heap && (1 << index_of__bit)) {
                index += range * index_of__bit;
                continue;
            }
        }
        break;
    } while ((range >>= 3));
    if (!range) {
        return index;
    }
    return INDEX__UNKNOWN__u32;
}
 
void set_bit_in__bitmap_and_heap(
        u8 *p_bitmap,
        u8 *p_end_of__heap,
        Quantity__u32 size_of__bitmap_but_NOT__including_heap,
        Index__u32 index_of__bit,
        bool state_of__bit) {
#ifndef NDEBUG
    if (index_of__bit >= size_of__bitmap_but_NOT__including_heap) {
        debug_error("set_bit_in__bitmap_and_heap, index out of bounds %d/%d",
                index_of__bit,
                size_of__bitmap_but_NOT__including_heap);
        return;
    }
#endif
    p_bitmap[index_of__bit >> 3] = 
        (state_of__bit)
        ? BIT(index_of__bit & MASK(3)) | p_bitmap[index_of__bit >> 3]
        : (~BIT(index_of__bit & MASK(3))) & p_bitmap[index_of__bit >> 3]
        ;
    Index__u32 index_of__heap_modification =
        (index_of__bit >> 6)
        + size_of__bitmap_but_NOT__including_heap;
    p_end_of__heap[-index_of__heap_modification] =
        (state_of__bit)
        ? BIT(index_of__heap_modification & MASK(3)) 
            | p_bitmap[index_of__heap_modification >> 3]
        : (~BIT(index_of__heap_modification & MASK(3))) 
            & p_bitmap[index_of__heap_modification >> 3]
        ;
    Quantity__u32 range = 1;
    do { 
        Index__u32 index__next = 
            index_of__heap_modification
            + (index_of__heap_modification >> 3)
            ;
        if ((p_end_of__heap[-index__next] > 0) &&
                (p_end_of__heap[-index_of__heap_modification])) {
            break;
        }
        p_end_of__heap[-index__next] =
            (state_of__bit)
            ? BIT(index__next & MASK(3)) 
                | p_bitmap[index__next >> 3]
            : (~BIT(index__next & MASK(3))) 
                & p_bitmap[index__next >> 3]
            ;
        index_of__heap_modification = index__next;
    } while ((range <<= 3) < size_of__bitmap_but_NOT__including_heap);
}
