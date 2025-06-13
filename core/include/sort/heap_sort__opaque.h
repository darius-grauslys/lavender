#ifndef HEAP_SORT__OPAQUE_H
#define HEAP_SORT__OPAQUE_H

#include "defines.h"
#include "defines_weak.h"

///
/// Only returns once sort is finished.
///
void heap_sort__opaque(
        void *p_ptr_array,
        Quantity__u32 size_of__type,
        Quantity__u32 size_of__array,
        f_Sort_Heuristic__i32 f_sort_heuristic__void,
        f_Sort_Swap__Void f_sort_swap__void);

#endif
