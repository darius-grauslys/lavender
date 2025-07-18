#ifndef NUMERICS_H
#define NUMERICS_H

#include "defines.h"
#include <defines_weak.h>
#include <stdint.h>

///
/// R shift on negative numbers is compiler specific
/// on implementation, this is to keep things consistent.
///
#define ARITHMETRIC_R_SHIFT(x, n)\
    (((x)>=0) ? (x) >> (n) : -((-(x)) >> (n)))

///
/// L shift on negative numbers is undefined behavior.
/// This is an explicit arithmetric definition for
/// L shift on negatives.
///
#define ARITHMETRIC_L_SHIFT(x, n)\
    ((i32)((u32)(x) << (n)))

static const u8 MAX__U8     = ((u8)-1);
static const u16 MAX__U16   = ((u16)-1);
static const u32 MAX__U32   = ((u32)-1);

static inline
bool is_index_u8__out_of_bounds(
        Index__u8 index__u8) {
    return index__u8 == INDEX__UNKNOWN__u8;
}

static inline
bool is_index_u16__out_of_bounds(
        Index__u16 index__u16) {
    return index__u16 == INDEX__UNKNOWN__u16;
}

static inline
bool is_index_u32__out_of_bounds(
        Index__u32 index__u32) {
    return index__u32 == INDEX__UNKNOWN__u32;
}

static inline
bool is_quantity_u8__out_of_bounds(
        Index__u8 quantity__u8) {
    return quantity__u8 == QUANTITY__UNKNOWN__u8;
}

static inline
bool is_quantity_u16__out_of_bounds(
        Index__u16 quantity__u16) {
    return quantity__u16 == QUANTITY__UNKNOWN__u16;
}

static inline
bool is_quantity_u32__out_of_bounds(
        Index__u32 quantity__u32) {
    return quantity__u32 == QUANTITY__UNKNOWN__u32;
}

static inline 
i32F4 i32_to__i32F4(Signed_Index__i32 x) {
    return ARITHMETRIC_L_SHIFT(
            x, 
            FRACTIONAL_PERCISION_4__BIT_SIZE);
}

static inline 
Signed_Index__i32 i32F4_to__i32(i32F4 x) {
    return ARITHMETRIC_R_SHIFT(
            x, 
            FRACTIONAL_PERCISION_4__BIT_SIZE);
}

static inline 
i32F20 i32_to__i32F20(Signed_Index__i32 x) {
    return ARITHMETRIC_L_SHIFT(
            x, 
            FRACTIONAL_PERCISION_20__BIT_SIZE);
}

static inline 
Signed_Index__i32 i32F20_to__i32(i32F20 x) {
    return ARITHMETRIC_R_SHIFT(
            x,
            FRACTIONAL_PERCISION_20__BIT_SIZE);
}

static inline 
Signed_Index__i32 i32F20_to__i32F4(i32F20 x) {
    return ARITHMETRIC_R_SHIFT(
            x,
            FRACTIONAL_PERCISION_16__BIT_SIZE);
}

static inline 
Signed_Index__i32 i32F4_to__i32F20(i32F4 x) {
    return ARITHMETRIC_L_SHIFT(
            x, 
            FRACTIONAL_PERCISION_16__BIT_SIZE);
}

static inline
u8 min__u8(
        u8 first__u8,
        u8 second__u8) {
    return (second__u8 > first__u8)
        ? first__u8 
        : second__u8
        ;
}

static inline
u32 min__u32(
        u32 first__u32,
        u32 second__u32) {
    return (second__u32 > first__u32)
        ? first__u32 
        : second__u32
        ;
}

static inline
u8 max__u8(
        u8 first__u8,
        u8 second__u8) {
    return (first__u8 < second__u8)
        ? second__u8
        : first__u8
        ;
}

static inline
u32 max__u32(
        u32 first__u32,
        u32 second__u32) {
    return (first__u32 < second__u32)
        ? second__u32
        : first__u32
        ;
}

static inline
i32 max__i32(
        i32 first__i32,
        i32 second__i32) {
    return (first__i32 < second__i32)
        ? second__i32
        : first__i32
        ;
}

static inline
u8 add_u8__clamped(
        u8 first__u8,
        u8 second__u8,
        u8 clamp__u8) {
    if (MAX__U8 - first__u8 < second__u8) {
        return clamp__u8;
    }
    if (first__u8 + second__u8 > clamp__u8) {
        return clamp__u8;
    }
    return first__u8 + second__u8;
}

static inline
u16 add_u16__clamped(
        u16 first__u16,
        u16 second__u16,
        u16 clamp__u16) {
    if (MAX__U8 - first__u16 < second__u16) {
        return MAX__U8;
    }
    if (first__u16 + second__u16 > clamp__u16) {
        return clamp__u16;
    }
    return first__u16 + second__u16;
}

static inline
u32 add_u32__clamped(
        u32 first__u32,
        u32 second__u32,
        u32 clamp__u32) {
    if (MAX__U8 - first__u32 < second__u32) {
        return MAX__U8;
    }
    if (first__u32 + second__u32 > clamp__u32) {
        return clamp__u32;
    }
    return first__u32 + second__u32;
}

static inline
u8 subtract_u8__clamped(
        u8 first__u8,
        u8 second__u8,
        u8 min__u8) {
    if (first__u8 < second__u8) {
        return min__u8;
    }
    u8 subtraction = first__u8 - second__u8;
    if (subtraction > min__u8) {
        return min__u8;
    }
    return subtraction;
}

static inline
u16 subtract_u16__clamped(
        u16 first__u16,
        u16 second__u16,
        u16 min__u16) {
    if (first__u16 < second__u16) {
        return min__u16;
    }
    u16 subtraction = first__u16 - second__u16;
    if (subtraction > min__u16) {
        return min__u16;
    }
    return subtraction;
}

static inline
u32 subtract_u32__clamped(
        u32 first__u32,
        u32 second__u32,
        u32 min__u32) {
    if (first__u32 < second__u32) {
        return min__u32;
    }
    u32 subtraction = first__u32 - second__u32;
    if (subtraction > min__u32) {
        return min__u32;
    }
    return subtraction;
}

static inline
u8 subtract_u8__no_overflow(
        u8 first__u8,
        u8 second__u8) {
    if (first__u8 < second__u8)
        return 0;
    return first__u8 - second__u8;
}

static inline
u16 subtract_u16__no_overflow(
        u16 first__u16,
        u16 second__u16) {
    if (first__u16 < second__u16)
        return 0;
    return first__u16 - second__u16;
}

static inline
u32 subtract_u32__no_overflow(
        u32 first__u32,
        u32 second__u32) {
    if (first__u32 < second__u32)
        return 0;
    return first__u32 - second__u32;
}

static inline
u8 delta_u8__no_overflow(
        u8 first__u8,
        u8 second__u8) {
    if (first__u8 < second__u8)
        return second__u8 - first__u8;
    return first__u8 - second__u8;
}

static inline
u16 delta_u16__no_overflow(
        u16 first__u16,
        u16 second__u16) {
    if (first__u16 < second__u16)
        return second__u16 - first__u16;
    return first__u16 - second__u16;
}

static inline
u32 delta_u32__no_overflow(
        u32 first__u32,
        u32 second__u32) {
    if (first__u32 < second__u32)
        return second__u32 - first__u32;
    return first__u32 - second__u32;
}

static inline
bool add_u8__no_overflow(
        u8 first__u8,
        u8 second__u8,
        u8 *p_out__u8) {
    if (UINT8_MAX - first__u8 < second__u8)
        return true;
    *p_out__u8 = first__u8 + second__u8;
    return false;
}

static inline
bool add_u16__no_overflow(
        u16 first__u16,
        u16 second__u16,
        u16 *p_out__u16) {
    if (UINT16_MAX - first__u16 < second__u16)
        return true;
    *p_out__u16 = first__u16 + second__u16;
    return false;
}

static inline
bool add_u32__no_overflow(
        u32 first__u32,
        u32 second__u32,
        u32 *p_out__u32) {
    if (UINT32_MAX - first__u32 < second__u32)
        return true;
    *p_out__u32 = first__u32 + second__u32;
    return false;
}

static inline
bool add_u64__no_overflow(
        u64 first__u64,
        u64 second__u64,
        u64 *p_out__u64) {
    if (UINT64_MAX - first__u64 < second__u64)
        return true;
    *p_out__u64 = first__u64 + second__u64;
    return false;
}

static inline
u8 multiply_u8__clamped(
        u8 first__u8,
        u8 second__u8,
        u8 clamp__u8) {
    if ((MAX__U8>>1) < first__u8
            || (MAX__U8>>1) < second__u8) {
        return clamp__u8;
    }
    u8 multiple = first__u8 * second__u8;
    if (multiple > clamp__u8) {
        return clamp__u8;
    }
    return multiple;
}

static inline
u16 multiply_u16__clamped(
        u16 first__u16,
        u16 second__u16,
        u16 clamp__u16) {
    if ((MAX__U16>>1) < first__u16
            || (MAX__U16>>1) < second__u16) {
        return clamp__u16;
    }
    u16 multiple = first__u16 * second__u16;
    if (multiple > clamp__u16) {
        return clamp__u16;
    }
    return multiple;
}

static inline
u32 multiply_u32__clamped(
        u32 first__u32,
        u32 second__u32,
        u32 clamp__u32) {
    if ((MAX__U32>>1) < first__u32
            || (MAX__U32>>1) < second__u32) {
        return clamp__u32;
    }
    u32 multiple = first__u32 * second__u32;
    if (multiple > clamp__u32) {
        return clamp__u32;
    }
    return multiple;
}

static inline
u8 r_bitshift_u8__clamped(
        u8 value__u8,
        u8 shift__u8,
        u8 min__u8) {
    if (shift__u8 >= 8)
        return min__u8;
    u8 shifted = value__u8 >> shift__u8;
    if (shift__u8 < min__u8) {
        return min__u8;
    }
    return shifted;
}

static inline
u16 r_bitshift_u16__clamped(
        u16 value__u16,
        u16 shift__u16,
        u16 min__u16) {
    if (shift__u16 >= 8)
        return min__u16;
    u16 shifted = value__u16 >> shift__u16;
    if (shift__u16 < min__u16) {
        return min__u16;
    }
    return shifted;
}

static inline
u32 r_bitshift_u32__clamped(
        u32 value__u32,
        u32 shift__u32,
        u32 min__u32) {
    if (shift__u32 >= 8)
        return min__u32;
    u32 shifted = value__u32 >> shift__u32;
    if (shift__u32 < min__u32) {
        return min__u32;
    }
    return shifted;
}

static inline
u8 clamp__u8(
        u8 value__u8,
        u8 min__u8,
        u8 max__u8) {
    if (value__u8 < min__u8)
        return min__u8;
    if (value__u8 > max__u8)
        return max__u8;
    return value__u8;
}

static inline
void clamp__p_u8(
        u8 *p_value__u8,
        u8 min__u8,
        u8 max__u8) {
    u8 value__u8 = *p_value__u8;
    if (value__u8 < min__u8) {
        *p_value__u8 = min__u8;
        return;
    }
    if (value__u8 > max__u8) {
        *p_value__u8 = max__u8;
        return;
    }
}

static inline
i32 clamp__i32(
        i32 value__i32,
        i32 min__i32,
        i32 max__i32) {
    if (value__i32 < min__i32)
        return min__i32;
    if (value__i32 > max__i32)
        return max__i32;
    return value__i32;
}

static inline
void clamp__p_i32(
        i32 *p_value__i32,
        i32 min__i32,
        i32 max__i32) {
    i32 value__i32 = *p_value__i32;
    if (value__i32 < min__i32) {
        *p_value__i32 = min__i32;
        return;
    }
    if (value__i32 > max__i32) {
        *p_value__i32 = max__i32;
        return;
    }
}

#endif
