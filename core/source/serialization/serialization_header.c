#include "defines.h"
#include "defines_weak.h"
#include "serialization/identifiers.h"
#include "serialization/serialization_header.h"

void initialize_serialization_header(
        Serialization_Header *p_serialization_header,
        Identifier__u32 identifier_for__serialized_struct,
        Quantity__u32 size_of__struct) {
    p_serialization_header
        ->size_of__struct = 
        size_of__struct;

    p_serialization_header
        ->uuid =
        identifier_for__serialized_struct;
}

void initialize_serialization_header__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_header,
        Identifier__u64 identifier_for__serialized_struct,
        Quantity__u32 size_of__struct) {
    p_serialization_header
        ->size_of__struct = 
        size_of__struct;

    p_serialization_header
        ->uuid =
        identifier_for__serialized_struct;
}

void initialize_serialization_header__contiguous_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Quantity__u32 size_of__struct) {
    u8 *p_bytes = (u8*)p_serialization_headers;
    for (Index__u32 index_of__serialized_header = 0;
            index_of__serialized_header
            < length_of__p_serialization_headers;
            index_of__serialized_header++) {
        Serialization_Header *p_serialized_header =
            (Serialization_Header*)p_bytes;
        memset(
                p_bytes,
                0,
                size_of__struct);
        initialize_serialization_header(
                p_serialized_header,
                IDENTIFIER__UNKNOWN__u32,
                size_of__struct);
        p_bytes += size_of__struct;
    }
}

void initialize_serialization_header__contiguous_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Quantity__u32 size_of__struct) {
    u8 *p_bytes = (u8*)p_serialization_headers;
    for (Index__u32 index_of__serialized_header = 0;
            index_of__serialized_header
            < length_of__p_serialization_headers;
            index_of__serialized_header++) {
        Serialization_Header__UUID_64 *p_serialized_header =
            (Serialization_Header__UUID_64*)p_bytes;
        memset(
                p_bytes,
                0,
                size_of__struct);
        initialize_serialization_header__uuid_64(
                p_serialized_header,
                IDENTIFIER__UNKNOWN__u64,
                size_of__struct);
        p_bytes += size_of__struct;
    }
}

Serialization_Header *get_p_serialization_header_from__contigious_array(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Index__u32 index_of__serialized_header) {
#ifndef NDEBUG
    if (index_of__serialized_header >= length_of__p_serialization_headers) {
        debug_abort("get_p_serialization_header_from__contigious_array, index out of bounds: %d, out of %d",
                index_of__serialized_header,
                length_of__p_serialization_headers);
        return 0;
    }
#endif
    u8 *p_bytes = (u8*)p_serialization_headers;
    p_bytes += 
        p_serialization_headers->size_of__struct
        * index_of__serialized_header
        ;
    return (Serialization_Header*)p_bytes;
}

Serialization_Header *get_next_available_p_serialization_header(
        Serialization_Header *p_serialization_headers,
        Quantity__u32 quantity_of__serialization_headers) {
    u8 *p_bytes = (u8*)p_serialization_headers;
    for (Index__u32 step = 0;
            step < quantity_of__serialization_headers;
            step++) {
        Serialization_Header *p_serialization_header =
            (Serialization_Header*)p_bytes;
        if (is_serialized_struct__deallocated(
                    p_serialization_header))
            return p_serialization_header;
        p_bytes += p_serialization_header
            ->size_of__struct;
    }

    return 0;
}

Serialization_Header__UUID_64 
*get_next_available_p_serialization_header__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 quantity_of__serialization_headers) {
    u8 *p_bytes = (u8*)p_serialization_headers;
    for (Index__u32 step = 0;
            step < quantity_of__serialization_headers;
            step++) {
        Serialization_Header__UUID_64 *p_serialization_header =
            (Serialization_Header__UUID_64*)p_bytes;
        if (is_serialized_struct__deallocated__uuid_64(
                    p_serialization_header))
            return p_serialization_header;
        p_bytes += p_serialization_header
            ->size_of__struct;
    }

    return 0;
}

Serialization_Header__UUID_64 *get_p_serialization_header_from__contigious_array__uuid_64(
        Serialization_Header__UUID_64 *p_serialization_headers,
        Quantity__u32 length_of__p_serialization_headers,
        Index__u32 index_of__serialized_header) {
#ifndef NDEBUG
    if (index_of__serialized_header >= length_of__p_serialization_headers) {
        debug_abort("get_p_serialization_header_from__contigious_array, index out of bounds: %d, out of %d",
                index_of__serialized_header,
                length_of__p_serialization_headers);
        return 0;
    }
#endif
    u8 *p_bytes = (u8*)p_serialization_headers;
    p_bytes += 
        p_serialization_headers->size_of__struct
        * index_of__serialized_header
        ;
    return (Serialization_Header__UUID_64*)p_bytes;
}
