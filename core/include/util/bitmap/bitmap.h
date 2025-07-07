#ifndef BITMAP_H
#define BITMAP_H

#include "debug/debug.h"
#include "defines_weak.h"

#define BITMAP(name, N)\
    u8 name[ N >> 3]

#define BITMAP_AND_HEAP(name, N)\
    u8 name[ (N >> 3)\
    + (N >> 6)\
    + (N >> 9)\
    + (N >> 12)\
    + (N >> 15)\
    + (N >> 18)\
    + (N >> 21)\
    + (N >> 24)\
    + (N >> 27)\
    + (N >> 30)]

void initialize_bitmap(
        u8 *p_bitmap,
        bool state,
        Quantity__u32 size_of__bitmap);

Index__u32 get_index_of__first_set_bit_from__bitmap_and_heap(
        u8 *p_bitmap_and_heap,
        Quantity__u32 size_of__bitmap_but_NOT__including_heap);

static inline
bool is_bit_set_in__bitmap(
        u8 *p_bitmap,
        Quantity__u32 size_of__bitmap,
        Index__u32 index_of__bit) {
#ifndef NDEBUG
    if (index_of__bit >= size_of__bitmap) {
        debug_error("is_bit_set_in__bitmap, index out of bounds %d/%d",
                index_of__bit,
                size_of__bitmap);
        return false;
    }
#endif
    return BIT(index_of__bit & MASK(3))
        & p_bitmap[index_of__bit >> 3];
}

static inline
void set_bit_in__bitmap(
        u8 *p_bitmap,
        Quantity__u32 size_of__bitmap,
        Index__u32 index_of__bit,
        bool state_of__bit) {
#ifndef NDEBUG
    if (index_of__bit >= size_of__bitmap) {
        debug_error("set_bit_in__bitmap, index out of bounds %d/%d",
                index_of__bit,
                size_of__bitmap);
        return;
    }
#endif
    p_bitmap[index_of__bit >> 3] 
        = 
        (state_of__bit)
        ? BIT(index_of__bit & MASK(3)) | p_bitmap[index_of__bit >> 3]
        : (~BIT(index_of__bit & MASK(3))) & p_bitmap[index_of__bit >> 3]
        ;
}

void set_bit_in__bitmap_and_heap(
        u8 *p_bitmap,
        u8 *p_end_of__heap,
        Quantity__u32 size_of__bitmap_but_NOT__including_heap,
        Index__u32 index_of__bit,
        bool state_of__bit);

#define SET_BIT_IN__BITMAP_AND_HEAP(\
        bitmap,\
        size_of__bitmap_but_NOT__including_heap,\
        index,\
        state)\
        set_bit_in__bitmap_and_heap(\
                bitmap,\
                &bitmap[sizeof(bitmap)-1],\
                size_of__bitmap_but_NOT__including_heap,\
                index,\
                state)

#endif
