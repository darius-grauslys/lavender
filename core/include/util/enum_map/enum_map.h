#ifndef ENUM_MAP_H
#define ENUM_MAP_H

#define ENUM_MAP(name, type_enum, type_value) \
    typedef struct name ## _t {\
        type_value _values[type_enum ## __Unknown];\
    } name ;

#define DECLARE_API__ENUM_MAP(name, type_enum, type_value)\
    void initialize_enum_map__ ## name (name *p_ ## name);\
    void register_ ## type_value ## _into__ ## name(\
            name *p_ ## name,\
            type_enum enum_key,\
            type_value value);\
    type_value get_ ## type_value ## _from__ ## name(\
            name *p_ ## name,\
            type_enum enum_key);

#define _ENUM_MAP__GET_P_HELPER(name, type_value)\
    get_p_ ## type_value ## _by__enum_key_from__ ## name
#ifndef NDEBUG
#define _DEFINE_API__ENUM_MAP__HELPERS(name, type_enum, type_value)\
    static inline\
    type_value *_ENUM_MAP__GET_P_HELPER(name, type_value)(\
            name *p_name,\
            type_enum enum_key) {\
        if (enum_key < 0 || enum_key >= type_enum ## __Unknown) {\
            debug_error("get_" #type_value "_by__enum_key_from__" #name ", invalid enum_key.");\
            return 0;\
        }\
        return &p_ ## name ->_values[ enum_key ];\
    }
#else
#define _DEFINE_API__ENUM_MAP__HELPERS(name, type_enum, type_value)\
    static inline\
    type_value *_ENUM_MAP__GET_P_HELPER(name, type_value)(\
            name *p_name,\
            type_enum enum_key) {\
        return &p_ ## name ->_values[ enum_key ];\
    }
#endif

#ifndef NDEBUG
#define DEFINE_API__ENUM_MAP(name, type_enum, type_value)\
    _DEFINE_API__ENUM_MAP__HELPERS(name, type_enum, type_value)\
    void initialize_enum_map__ ## name (name *p_ ## name) {\
        memset(p_ ## name, 0, sizeof( name ));\
    }\
    void register_ ## type_value ## _into__ ## name(\
            name *p_ ## name,\
            type_enum enum_key,\
            type_value value) {\
        type_value *p_ ## type_value = _ENUM_MAP__GET_P_HELPER(name, type_value)(\
                p_ ##name,\
                enum_key);\
        if (!p_ ## type_value) {\
            debug_error("register_" #type_value "_into__" #name ", p_" #type_value " == 0.");\
            return;\
        }\
        *p_ ##type_value = value;\
    }\
    type_value get_ ## type_value ## _from__ ## name(\
            name *p_ ## name,\
            type_enum enum_key) {\
        type_value *p_ ## type_value = _ENUM_MAP__GET_P_HELPER(name, type_value)(\
                p_ ##name,\
                enum_key);\
        if (!p_ ## type_value) {\
            debug_error("get_" #type_value "_from__" #name ", p_" #type_value " == 0.");\
            return p_ ##name ->_values[ type_enum ## __None ];\
        }\
        return *p_ ##type_value;\
    }
#else
#define DEFINE_API__ENUM_MAP(name, type_enum, type_value)\
    _DEFINE_API__ENUM_MAP__HELPERS(name, type_enum, type_value)\
    void initialize_enum_map__ ## name (name *p_ ## name) {\
        memset(p_ ## name, 0, sizeof( name ));\
    }\
    void register_ ## type_value ## _into__ ## name(\
            name *p_ ## name,\
            type_enum enum_key,\
            type_value value) {\
        type_value *p_ ## type_value = _ENUM_MAP__GET_P_HELPER(name, type_value)(\
                p_ ##name,\
                enum_key);\
        *p_ ##type_value = value;\
    }\
    type_value get_ ## type_value ## _from__ ## name(\
            name *p_ ## name,\
            type_enum enum_key) {\
        type_value *p_ ## type_value = _ENUM_MAP__GET_P_HELPER(name, type_value)(\
                p_ ##name,\
                enum_key);\
        return *p_ ##type_value;\
    }
#endif

#endif
