#ifndef LAV_STRING_H
#define LAV_STRING_H

#include "defines_weak.h"

bool cstr_to_i32__limit_n(
        const char *p_cstr,
        i32 limit_n,
        i32 *p_OUT_i32);

bool cstr_to_u32__limit_n(
        const char *p_cstr,
        i32 limit_n,
        u32 *p_OUT_u32);

static inline
bool cstr_to_i16__limit_n(
        const char *p_cstr,
        i32 limit_n,
        i16 *p_OUT_i16) {
    i32 value = 0;
    bool result = (i16)cstr_to_i32__limit_n(
            p_cstr, 
            limit_n,
            &value);
    if (result)
        *p_OUT_i16 = (i16)value;
    return result;
}

static inline
bool cstr_to_i8__limit_n(
        const char *p_cstr,
        i32 limit_n,
        i8 *p_OUT_i8) {
    i32 value = 0;
    bool result = (i8)cstr_to_i32__limit_n(
            p_cstr, 
            limit_n,
            &value);
    if (result)
        *p_OUT_i8 = (i8)value;
    return result;
}

static inline
bool cstr_to_u16__limit_n(
        const char *p_cstr,
        i32 limit_n,
        u16 *p_OUT_u16) {
    u32 value = 0;
    bool result = (u16)cstr_to_u32__limit_n(
            p_cstr, 
            limit_n,
            &value);
    if (result)
        *p_OUT_u16 = (u16)value;
    return result;
}

static inline
bool cstr_to_u8__limit_n(
        const char *p_cstr,
        i32 limit_n,
        u8 *p_OUT_u8) {
    u32 value = 0;
    bool result = (u8)cstr_to_u32__limit_n(
            p_cstr, 
            limit_n,
            &value);
    if (result)
        *p_OUT_u8 = (u8)value;
    return result;
}

#endif
