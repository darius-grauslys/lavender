#ifndef HASHING_H
#define HASHING_H

#include "defines_weak.h"
#include "numerics.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization_header.h"
#include <defines.h>

///
/// Returns an index to a contiguous array
/// that points to a matching uuid.
/// In particular, this handles uuid collisions.
///
/// A collision is when the UUID mod (%) length_of__p_serialization_headers
/// happens to be congruent (same number after mod) with
/// another UUID also mod'd by length_of__p_serialization_headers.
///
/// Returns a valid index within the array regardless if the struct
/// is considered allocated or not. Returns IDENTIFIER__UNKNOWN__u32 only
/// if the array is completely full.
///
Index__u32 poll_for__uuid_collision(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32,
        Index__u32 index__initial__u32);

Index__u32 poll_for__uuid_collision__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64,
        Index__u32 index__initial__u32);

Identifier__u32 get_next_available__uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 uuid);

Identifier__u64 get_next_available__uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 uuid__u64);

Serialization_Header *dehash_identitier_u32_in__contigious_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32);

Serialization_Header__UUID_64 *dehash_identitier_u64_in__contigious_array(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64);

Serialization_Header *get_next_available__allocation_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32);

Serialization_Header__UUID_64 *get_next_available__allocation_in__contiguous_array__u64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64);

static inline
Identifier__u32 get_next_available__random_uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer) {
    Identifier__u32 uuid=
        get_random__uuid_u32(p_randomizer);
    return get_next_available__uuid_in__contiguous_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            uuid);
}

static inline
Identifier__u32 get_next_available__random_branded_uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u32 uuid__branding__u32) {
    Identifier__u32 uuid=
        BRAND_UUID(get_random__uuid_u32(p_randomizer), uuid__branding__u32);
    return get_next_available__uuid_in__contiguous_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            uuid);
}

///
/// NOTE: if p_OUT_uuid__u32 is NOT IDENTIFIER__UNKNOWN__u32, then it is
/// treated as a branding UUID mask. Be sure to initialize the p_OUT
/// parameter before passing it in!
///
/// p_OUT_uuid__u32: This will return the resolved uuid. Be sure to
/// allocate the type!
///
Serialization_Header *get_next_available__random_allocation_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u32 *p_OUT_uuid__u32);

static inline
Serialization_Header *allocate_serialization_header_with__this_uuid(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 uuid__u32) {
    Serialization_Header *p_serialization_header =
        get_next_available__allocation_in__contiguous_array(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                uuid__u32);
    ALLOCATE_P(p_serialization_header, uuid__u32);
    return p_serialization_header;
}

static inline
Serialization_Header *allocate_serialization_header(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer) {
    Identifier__u32 uuid__u32 = IDENTIFIER__UNKNOWN__u32;
    Serialization_Header *p_serialization_header =
        get_next_available__random_allocation_in__contiguous_array(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                p_randomizer, 
                &uuid__u32);
    ALLOCATE_P(p_serialization_header, uuid__u32);
    return p_serialization_header;
}

static inline
Serialization_Header *allocate_serialization_header_with__uuid_branding(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u32 uuid__branding__u32) {
    Serialization_Header *p_serialization_header =
        get_next_available__random_allocation_in__contiguous_array(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                p_randomizer, 
                &uuid__branding__u32);
    ALLOCATE_P(p_serialization_header,
            uuid__branding__u32);
    return p_serialization_header;
}

static inline
Identifier__u64 get_next_available__random_uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer) {
    Identifier__u64 uuid=
        get_random__uuid_u64(p_randomizer);
    return get_next_available__uuid_in__contiguous_array__uuid_64(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            uuid);
}

static inline
Identifier__u64 
get_next_available__random_branded_uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u64 uuid__branding__u64) {
    Identifier__u64 uuid=
        BRAND_UUID__64(
                get_random__uuid_u64(p_randomizer),
                uuid__branding__u64);
    return get_next_available__uuid_in__contiguous_array__uuid_64(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            uuid);
}

///
/// NOTE: if p_OUT_uuid__u64 is NOT IDENTIFIER__UNKNOWN__u64, then it is
/// treated as a branding UUID mask. Be sure to initialize the p_OUT
/// parameter before passing it in!
///
/// p_OUT_uuid__u64: This will return the resolved uuid. Be sure to
/// allocate the type!
///
Serialization_Header__UUID_64
*get_next_available__random_allocation_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u64 *p_OUT_uuid__u64);

static inline
Serialization_Header__UUID_64 
*allocate_serialization_header_with__this_uuid__u64(
        Serialization_Header__UUID_64 *p_serialization_headers__u64,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 uuid__u64) {
    Serialization_Header__UUID_64 *p_serialization_header__u64 =
        get_next_available__allocation_in__contiguous_array__u64(
                p_serialization_headers__u64, 
                length_of__p_serialization_headers, 
                uuid__u64);
    ALLOCATE_P(p_serialization_header__u64, uuid__u64);
    return p_serialization_header__u64;
}

static inline
Serialization_Header__UUID_64 *allocate_serialization_header__u64(
        Serialization_Header__UUID_64 *p_serialization_headers__u64,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer) {
    Identifier__u64 uuid__u64 = IDENTIFIER__UNKNOWN__u64;
    Serialization_Header__UUID_64 *p_serialization_header__u64 =
        get_next_available__random_allocation_in__contiguous_array__uuid_64(
                p_serialization_headers__u64, 
                length_of__p_serialization_headers, 
                p_randomizer, 
                &uuid__u64);
    ALLOCATE_P__u64(p_serialization_header__u64, uuid__u64);
    return p_serialization_header__u64;
}

static inline
Serialization_Header__UUID_64 
*allocate_serialization_header_with__uuid_branding__u64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u64 uuid__branding__u64) {
    Serialization_Header__UUID_64 *p_serialization_header__u64 =
        get_next_available__random_allocation_in__contiguous_array__uuid_64(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                p_randomizer, 
                &uuid__branding__u64);
    ALLOCATE_P__u64(p_serialization_header__u64,
            uuid__branding__u64);
    return p_serialization_header__u64;
}

static inline
bool has_uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32) {
    return dehash_identitier_u32_in__contigious_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            identifier__u32);
}

static inline
bool has_uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64) {
    return dehash_identitier_u64_in__contigious_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            identifier__u64);
}

static inline
Identifier__u32 bound_uuid_to__contiguous_array(
        Identifier__u32 identifier,
        Quantity__u32 quantity_of__elements) {
    return identifier % quantity_of__elements;
}

static inline
Identifier__u32 bound_uuid_to__contiguous_array__uuid_64(
        Identifier__u64 identifier,
        Quantity__u32 quantity_of__elements) {
    return identifier % quantity_of__elements;
}

#endif
