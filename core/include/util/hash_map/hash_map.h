#ifndef HASH_MAP_H
#define HASH_MAP_H
#include "defines.h"
#include "serialization/hashing.h"

#define UUID_MAPPED__POOL(\
        name,\
        type_value,\
        length_of__pool)\
    typedef struct name ## _t {\
        Serialization_Pool _serialization_pool;\
        type_value _values[length_of__pool];\
    } name ;

#define DECLARE_API__UUID_MAPPED__POOL(\
        name,\
        type_value,\
        length_of__pool)\
    static inline\
    void initialize_ ## name (name *p_ ##name) {\
        initialize_serialization_pool(\
                &name->_serialization_pool,\
                (sizeof(name) - sizeof(Serialization_Pool))\
                / sizeof(type_value),\
                sizeof(type_value));\
    }\
    static inline\
    type_value *allocate_ ## type_value ##_from__ ## name(\
            name *p_ ## name ) {\
        return (type_value*)allocate_from__serialization_pool(\
                &name->_serialization_pool);\
    }\
    static inline\
    void release_ ## type_value ##_from__ ## name(\
            name *p_ ## name ,\
            type_value *p_ ## type_value) {\
        release_from__serialization_pool(\
                &name->_serialization_pool,\
                (Serialization_Header*)p_ ## type_value );\
    }\
    static inline\
    type_value *dehash_p_ ## type_value ## _from__ ## name (\
            name *p_ ## name,\
            Identifier__u32 uuid) {\
        (void)p_ ## name ->_values[0]._serialization_header.uuid;\
        return DEHASH(p_ ##name ->_serialization_pool,\
                uuid,\
                type_value *);\
    }

#endif
