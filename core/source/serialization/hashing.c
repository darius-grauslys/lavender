#include "defines.h"
#include "defines_weak.h"
#include "numerics.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"
#include "serialization/serialized_field.h"
#include "serialization/hashing.h"

Index__u32 poll_for__uuid_collision(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32,
        Index__u32 index__initial__u32) {

    Identifier__u32 identifier__mod_size = 
        ((index__initial__u32 != INDEX__UNKNOWN__u32)
        ? index__initial__u32+1
        : identifier__u32 )
        % length_of__p_serialization_headers;
    Quantity__u32 size_of__struct =
        p_serialization_headers->size_of__struct;

    u8 *p_bytes = (u8*)p_serialization_headers;

    Identifier__u32 current_identifier = 
        identifier__mod_size;
    do {
        Serialization_Header *p_serialization_header =
            (Serialization_Header*)(
                    p_bytes
                    + current_identifier
                    * size_of__struct
                    );
        if (is_serialized_struct__deallocated(
                    p_serialization_header)
                || is_identifier_u32_matching__serialization_header(
                    identifier__u32,
                    p_serialization_header)) {
            return current_identifier;
        }
    } while ((current_identifier = (current_identifier + 1) 
                % length_of__p_serialization_headers)
            != identifier__mod_size);
    return INDEX__UNKNOWN__u32;
}

Index__u32 poll_for__uuid_collision__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64,
        Index__u32 index__initial__u32) {

    Identifier__u64 identifier__mod_size = 
        ((index__initial__u32 != INDEX__UNKNOWN__u32)
        ? index__initial__u32+1
        : identifier__u64 )
        % length_of__p_serialization_headers;
    Quantity__u32 size_of__struct =
        p_serialization_headers->size_of__struct;

    u8 *p_bytes = (u8*)p_serialization_headers;

    Identifier__u64 current_identifier = 
        identifier__mod_size;
    do {
        Serialization_Header__UUID_64 *p_serialization_header =
            (Serialization_Header__UUID_64*)(
                    p_bytes
                    + current_identifier
                    * size_of__struct
                    );
        if (is_serialized_struct__deallocated__uuid_64(
                    p_serialization_header)
                || is_identifier_u64_matching__serialization_header(
                    identifier__u64,
                    p_serialization_header)) {
            return current_identifier;
        }
    } while ((current_identifier = (current_identifier + 1) 
                % length_of__p_serialization_headers)
            != identifier__mod_size);
    return INDEX__UNKNOWN__u32;
}

Identifier__u32 get_next_available__uuid_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 uuid) {
    uuid -= (uuid % length_of__p_serialization_headers);
    Index__u32 index__u32 =
        poll_for__uuid_collision(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                uuid,
                INDEX__UNKNOWN__u32);
    uuid += index__u32;
    return uuid;
}

Identifier__u64 get_next_available__uuid_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 uuid__u64) {
    uuid__u64 -= (uuid__u64 % length_of__p_serialization_headers);
    Index__u32 index__u32 =
        poll_for__uuid_collision__uuid_64(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                uuid__u64,
                INDEX__UNKNOWN__u32);
    uuid__u64 += index__u32;
    return uuid__u64;
}

Serialization_Header *dehash_identitier_u32_in__contigious_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32) {
    Index__u32 index__initial__u32 = 
        poll_for__uuid_collision(
                p_serialization_headers, 
                length_of__p_serialization_headers,
                identifier__u32,
                INDEX__UNKNOWN__u32);
    Index__u32 index__u32 = index__initial__u32;
    do {
        if (is_identifier_u32_matching__serialization_header(
                    identifier__u32, 
                    get_p_serialization_header_from__contigious_array(
                        p_serialization_headers, 
                        length_of__p_serialization_headers, 
                        index__u32))) {
            break;
        }
        index__u32 = poll_for__uuid_collision(
                p_serialization_headers, 
                length_of__p_serialization_headers,
                identifier__u32,
                index__u32);
        if (index__initial__u32 == index__u32)
            return 0;
    } while (true);
    return get_p_serialization_header_from__contigious_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            index__u32);
}

Serialization_Header__UUID_64 *dehash_identitier_u64_in__contigious_array(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64) {
    Index__u32 index__initial__u32 = 
        poll_for__uuid_collision__uuid_64(
                p_serialization_headers, 
                length_of__p_serialization_headers,
                identifier__u64,
                INDEX__UNKNOWN__u32);
    Index__u32 index__u32 = index__initial__u32;
    do {
        if (is_identifier_u64_matching__serialization_header(
                    identifier__u64, 
                    get_p_serialization_header_from__contigious_array__uuid_64(
                        p_serialization_headers, 
                        length_of__p_serialization_headers, 
                        index__u32))) {
            break;
        }
        index__u32 = poll_for__uuid_collision__uuid_64(
                p_serialization_headers, 
                length_of__p_serialization_headers,
                identifier__u64,
                index__u32);
        if (index__initial__u32 == index__u32)
            return 0;
    } while (true);
    return get_p_serialization_header_from__contigious_array__uuid_64(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            index__u32);
}

Serialization_Header *get_next_available__allocation_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u32 identifier__u32) {
    Index__u32 index_of__allocation = 
        poll_for__uuid_collision(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                identifier__u32, 
                INDEX__UNKNOWN__u32);
    if (index_of__allocation == INDEX__UNKNOWN__u32)
        return 0;
    return (Serialization_Header*)
        get_p_serialization_header_from__contigious_array(
                p_serialization_headers,
                length_of__p_serialization_headers,
                index_of__allocation);
}

Serialization_Header__UUID_64 
*get_next_available__allocation_in__contiguous_array__u64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Identifier__u64 identifier__u64) {
    Index__u32 index_of__allocation = 
        poll_for__uuid_collision__uuid_64(
                p_serialization_headers, 
                length_of__p_serialization_headers, 
                identifier__u64, 
                INDEX__UNKNOWN__u32);
    if (index_of__allocation == INDEX__UNKNOWN__u32)
        return 0;
    return (Serialization_Header__UUID_64*)
        get_p_serialization_header_from__contigious_array__uuid_64(
                p_serialization_headers,
                length_of__p_serialization_headers,
                index_of__allocation);
}

Serialization_Header *get_next_available__random_allocation_in__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u32 uuid__branding__u32) {
    Identifier__u32 uuid__u32 =
        (uuid__branding__u32)
        ? get_next_available__random_branded_uuid_in__contiguous_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            p_randomizer,
            uuid__branding__u32)
        : get_next_available__random_uuid_in__contiguous_array(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            p_randomizer);
    Serialization_Header *p_allocation = 
        get_next_available__allocation_in__contiguous_array(
            p_serialization_headers, 
            ENTITY_MAXIMUM_QUANTITY_OF,
            uuid__u32);

    initialize_serialization_header(
            p_allocation, 
            uuid__u32, 
            p_allocation->size_of__struct);

    return p_allocation;
}

Serialization_Header__UUID_64
*get_next_available__random_allocation_in__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Repeatable_Psuedo_Random *p_randomizer,
        Identifier__u64 uuid__branding__u64) {
    Identifier__u64 uuid__u64 =
        (uuid__branding__u64)
        ? get_next_available__random_branded_uuid_in__contiguous_array__uuid_64(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            p_randomizer,
            uuid__branding__u64)
        : get_next_available__random_uuid_in__contiguous_array__uuid_64(
            p_serialization_headers, 
            length_of__p_serialization_headers, 
            p_randomizer);
    Serialization_Header__UUID_64 *p_allocation = 
        get_next_available__allocation_in__contiguous_array__u64(
            p_serialization_headers, 
            ENTITY_MAXIMUM_QUANTITY_OF,
            uuid__u64);

    initialize_serialization_header__uuid_64(
            p_allocation, 
            uuid__u64, 
            p_allocation->size_of__struct);

    return p_allocation;
}
