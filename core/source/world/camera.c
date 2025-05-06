#include "defines.h"
#include "defines_weak.h"
#include "game.h"
#include "numerics.h"
#include "vectors.h"
#include <world/camera.h>
#include "collisions/hitbox_aabb_manager.h"
#include "collisions/hitbox_aabb.h"
#include "world/world.h"

void m_camera_handler__default(
        Camera *p_this_camera,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
}

void m_camera_handler__follow__default(
        Camera *p_this_camera,
        Game *p_game,
        Graphics_Window *p_graphics_window) {
    Hitbox_AABB *p_hitbox_aabb =
        get_p_hitbox_aabb_by__uuid_u32_from__hitbox_aabb_manager(
                get_p_hitbox_aabb_manager_from__game(p_game), 
                p_this_camera->uuid_of__target__u32);

    if (!p_hitbox_aabb) {
        debug_warning("Camera m_camera_handler set to default.");
        debug_error("m_camera_handler__follow__default, p_hitbox_aabb == 0.");
        p_this_camera
            ->m_camera_handler = m_camera_handler__default;
        return;
    }

    p_this_camera->position =
        get_position_3i32F4_of__hitbox_aabb(
                p_hitbox_aabb);
}

void initialize_camera(
        Camera *p_camera,
        Vector__3i32F4 position,
        m_Camera_Handler m_camera_handler,
        Quantity__u32 width_of__fulcrum,
        Quantity__u32 height_of__fulcrum,
        i32F20 z_near,
        i32F20 z_far) {
    p_camera->position = 
        position;
    p_camera->m_camera_handler =
        (m_camera_handler)
        ? m_camera_handler
        : m_camera_handler__default
        ;
    p_camera->height_of__fulcrum =
        height_of__fulcrum;
    p_camera->width_of__fulcrum =
        width_of__fulcrum;
    p_camera->z_near = z_near;
    p_camera->z_far = z_far;
}

bool is_camera__active(
        Camera *p_camera) {
    return 
        p_camera->m_camera_handler
        && !is_quantity_u32__out_of_bounds(
                p_camera->height_of__fulcrum)
        && !is_quantity_u32__out_of_bounds(
                p_camera->width_of__fulcrum)
        && !is_vectors_3i32F4__out_of_bounds(
                p_camera->position)
        && (p_camera->z_near < p_camera->z_far);
}

void set_camera_to__follow(
        Camera *p_camera,
        Identifier__u32 uuid_of__target__u32) {
    p_camera->m_camera_handler =
        m_camera_handler__follow__default;
    p_camera->uuid_of__target__u32 = uuid_of__target__u32;
}
