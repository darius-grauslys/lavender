#include "debug/debug.h"
#include "defines.h"
#include "defines_weak.h"
#include "numerics.h"
#include "vectors.h"
#include <raycast/ray.h>

extern Vector__3i32F20 __DEGREE_TO_2i32F10__LOOKUP_TABLE[255];

Ray__3i32F20 get_ray(
        Vector__3i32F4 starting_vector__3i32F4,
        Degree__u9 angle,
        Ray_Plane_Mode ray_plane_mode) {
    return (Ray__3i32F20) {
        vector_3i32F4_to__vector_3i32F20(starting_vector__3i32F4),
        vector_3i32F4_to__vector_3i32F20(starting_vector__3i32F4),
        angle,
        ray_plane_mode
    };
}

Ray__3i32F20 get_ray_as__extension(
        Ray__3i32F20 *p_ray,
        Degree__u9 angle) {
    return (Ray__3i32F20) {
        p_ray->ray_current_vector__3i32F20,
        p_ray->ray_current_vector__3i32F20,
        angle,
        p_ray->ray_plane_mode
    };
}

void step_p_ray(Ray__3i32F20 *p_ray) {
    Vector__3i32F20 offset__2i32F20 =
            __DEGREE_TO_2i32F10__LOOKUP_TABLE[p_ray->angle_of__ray];
    switch (p_ray->ray_plane_mode) {
        default:
        case Ray_Plane_Mode__XY:
            break;
        case Ray_Plane_Mode__XZ:
            offset__2i32F20.z__i32F20 =
                offset__2i32F20.y__i32F20;
            offset__2i32F20.y__i32F20 = 0;
            break;
        case Ray_Plane_Mode__YZ:
            offset__2i32F20.z__i32F20 =
                offset__2i32F20.x__i32F20;
            offset__2i32F20.x__i32F20 = 0;
            break;
    }
    add_p_vectors__3i32F20(
            &p_ray->ray_current_vector__3i32F20, 
            &offset__2i32F20);
}

static inline
void __step_p_ray_until(Ray__3i32F20 *p_ray, u32 percision) {
    Signed_Quantity__i32 a, b;
    Signed_Quantity__i32 *p_a, *p_b;
    switch (p_ray->ray_plane_mode) {
        default:
        case Ray_Plane_Mode__XY:
            p_a = &p_ray->ray_current_vector__3i32F20.x__i32F20;
            p_b = &p_ray->ray_current_vector__3i32F20.y__i32F20;
            a = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.x__i32F20, 
                    percision);
            b = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.y__i32F20, 
                    percision);
            break;
        case Ray_Plane_Mode__XZ:
            p_a = &p_ray->ray_current_vector__3i32F20.x__i32F20;
            p_b = &p_ray->ray_current_vector__3i32F20.z__i32F20;
            a = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.x__i32F20, 
                    percision);
            b = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.z__i32F20, 
                    percision);
            break;
        case Ray_Plane_Mode__YZ:
            p_a = &p_ray->ray_current_vector__3i32F20.y__i32F20;
            p_b = &p_ray->ray_current_vector__3i32F20.z__i32F20;
            a = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.y__i32F20, 
                    percision);
            b = ARITHMETRIC_R_SHIFT(
                    p_ray->ray_current_vector__3i32F20.z__i32F20, 
                    percision);
            break;
    }

    do {
        step_p_ray(p_ray);
    } while (
            ARITHMETRIC_R_SHIFT(*p_a, 
                percision)
            == a
            && ARITHMETRIC_R_SHIFT(*p_b, 
                percision)
            == b);
}

void step_p_ray_until__next_whole_integer(Ray__3i32F20 *p_ray) {
    __step_p_ray_until(p_ray, FRACTIONAL_PERCISION_20__BIT_SIZE);
}

void step_p_ray_until__next_tile(Ray__3i32F20 *p_ray) {
    __step_p_ray_until(p_ray, 
            FRACTIONAL_PERCISION_20__BIT_SIZE
            + TILE__WIDTH_AND__HEIGHT__BIT_SHIFT);
}

