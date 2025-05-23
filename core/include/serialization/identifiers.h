#ifndef IDENTIFIERS_H
#define IDENTIFIERS_H

#include "defines_weak.h"
#include "random.h"
#include <defines.h>

static inline
Identifier__u32 get_random__uuid_u32(
        Repeatable_Psuedo_Random *p_randomizer) {
    // Would be pretty problematic if we didn't
    // XOR this wouldn't it? LOL
    //
    // Pretty unlikely to collide, but...
    return get_pseudo_random_i32__intrusively(
            p_randomizer) 
        ^ IDENTIFIER__UNKNOWN__u32;
}

static inline
Identifier__u64 get_random__uuid_u64(
        Repeatable_Psuedo_Random *p_randomizer) {
    // Would be pretty problematic if we didn't
    // XOR this wouldn't it? LOL
    //
    // Pretty unlikely to collide, but...
    return (get_pseudo_random_i32__non_intrusively(
                p_randomizer) 
            | ((uint64_t)get_pseudo_random_i32__non_intrusively(
                p_randomizer) << 32))
        ^ IDENTIFIER__UNKNOWN__u64;
}

static inline
Identifier__u32 merge_identifiers_u32(
        Identifier__u32 identifier__left_half,
        Quantity__u8 bits__left,
        Identifier__u32 identifier__right_half) {
    return
        (identifier__left_half & ~MASK(33 - bits__left))
        | (identifier__right_half & MASK(33 - bits__left))
        ;
}

static inline
bool is_identifier_u32__invalid(
        Identifier__u32 identifier__u32) {
    return IDENTIFIER__UNKNOWN__u32 == identifier__u32;
}

static inline
bool is_identifier_u64__invalid(
        Identifier__u64 identifier__u64) {
    return IDENTIFIER__UNKNOWN__u64 == identifier__u64;
}

#endif
