#ifndef GA_TYPE__BAD_REQUEST_H
#define GA_TYPE__BAD_REQUEST_H

#include <util/custom_type_macro.h>

#include <defines_weak.h>

LAV_TYPE__BEGIN(GA_Bad_Request){
    uint32_t error_code__u32;
} GA_Bad_Request;

#endif
