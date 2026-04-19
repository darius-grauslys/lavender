#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32F4_H

#ifndef DEFINES_H
#include <defines.h>
#endif

#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__PosVec_I32F4){
    Vector__3i32F4 position__3i32F4;
    Vector__3i32F4 velocity__3i32F4;
} GA_AABB__Update__PosVec_I32F4;

#endif
