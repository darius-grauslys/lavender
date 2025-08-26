#include "lav_string.h"
#include "defines_weak.h"

bool cstr_to_i32__limit_n(
        const char *p_cstr,
        i32 limit_n,
        i32 *p_OUT_i32) {
    bool is_negative = false;

    i32 index_towards__limit_n = 0;
    for (;index_towards__limit_n < limit_n
            && p_cstr[index_towards__limit_n];
            index_towards__limit_n++) {
        switch (p_cstr[index_towards__limit_n]) {
            default:
                goto get_numeric;
            case '-':
                is_negative = !is_negative;
                break;
            case '+':
                is_negative = false;
                break;
        }
    }
get_numeric:
    ;
    i32 value = 0;
    for (;index_towards__limit_n < limit_n;
            index_towards__limit_n++) {
        i32 char_value = p_cstr[index_towards__limit_n]
            - '0'
            ;
        if (char_value < 0 || char_value > 9) {
            return false;
        }

        value *= 10;
        value += char_value;
    }

    if (is_negative)
        value *= -1;

    *p_OUT_i32 = value;
    return true;
}

bool cstr_to_u32__limit_n(
        const char *p_cstr,
        i32 limit_n,
        u32 *p_OUT_u32) {
    i32 value = 0;
    for (Index__u32 index_towards__limit_n = 0;
            index_towards__limit_n < limit_n
            && p_cstr[index_towards__limit_n];
            index_towards__limit_n++) {
        i32 char_value = p_cstr[index_towards__limit_n]
            - '0'
            ;
        if (char_value < 0 || char_value > 9) {
            return false;
        }

        value *= 10;
        value += char_value;
    }

    *p_OUT_u32 = value;
    return true;
}
