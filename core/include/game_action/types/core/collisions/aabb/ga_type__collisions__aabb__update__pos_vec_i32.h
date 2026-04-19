#ifndef GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_H
#define GA_TYPE__COLLISIONS__AABB__UPDATE__POS_VEC_I32_H
#define GA_TYPE_CONTEXT

#include <defines.h>
#include <util/custom_type_macro.h>

LAV_TYPE__BEGIN(GA_AABB__Update__PosVec_I32){
    Vector__3i32 position__3i32;
    Vector__3i32 velocity__3i32;
} GA_AABB__Update__PosVec_I32;

#undef GA_TYPE_CONTEXT
#endif
