#include <raycast/test_suite_raycast_ray.h>

#include <raycast/ray.c>

TEST_FUNCTION(get_ray__initializes_current_to_starting) {
    Vector__3i32F4 start;
    start.x__i32F4 = 16;
    start.y__i32F4 = 32;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    munit_assert_int32(
            ray.ray_current_vector__3i32F20.x__i32F20,
            ==,
            ray.ray_starting_vector__3i32F20.x__i32F20);
    munit_assert_int32(
            ray.ray_current_vector__3i32F20.y__i32F20,
            ==,
            ray.ray_starting_vector__3i32F20.y__i32F20);
    munit_assert_int32(
            ray.ray_current_vector__3i32F20.z__i32F20,
            ==,
            ray.ray_starting_vector__3i32F20.z__i32F20);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__stores_angle) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__90, Ray_Plane_Mode__XY);

    munit_assert_uint16(ray.angle_of__ray, ==, ANGLE__90);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__stores_plane_mode_xy) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    munit_assert_int(ray.ray_plane_mode, ==, Ray_Plane_Mode__XY);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__stores_plane_mode_xz) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XZ);

    munit_assert_int(ray.ray_plane_mode, ==, Ray_Plane_Mode__XZ);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__stores_plane_mode_yz) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__YZ);

    munit_assert_int(ray.ray_plane_mode, ==, Ray_Plane_Mode__YZ);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__out_of_bounds__is_detected_as_out_of_bounds) {
    Ray__3i32F20 ray = get_ray__out_of_bounds();

    munit_assert_true(is_ray__out_of_bouds(ray));

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__valid_ray_is_not_out_of_bounds) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    munit_assert_false(is_ray__out_of_bouds(ray));

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_as__extension__starts_at_source_endpoint) {
    Vector__3i32F4 start;
    start.x__i32F4 = 16;
    start.y__i32F4 = 16;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    step_p_ray(&ray);

    Ray__3i32F20 extension = get_ray_as__extension(&ray, ANGLE__90);

    munit_assert_int32(
            extension.ray_starting_vector__3i32F20.x__i32F20,
            ==,
            ray.ray_current_vector__3i32F20.x__i32F20);
    munit_assert_int32(
            extension.ray_starting_vector__3i32F20.y__i32F20,
            ==,
            ray.ray_current_vector__3i32F20.y__i32F20);
    munit_assert_int32(
            extension.ray_starting_vector__3i32F20.z__i32F20,
            ==,
            ray.ray_current_vector__3i32F20.z__i32F20);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_as__extension__inherits_plane_mode) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XZ);
    Ray__3i32F20 extension = get_ray_as__extension(&ray, ANGLE__45);

    munit_assert_int(extension.ray_plane_mode, ==, Ray_Plane_Mode__XZ);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_as__extension__stores_new_angle) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    Ray__3i32F20 extension = get_ray_as__extension(&ray, ANGLE__180);

    munit_assert_uint16(extension.angle_of__ray, ==, ANGLE__180);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_as__extension__current_equals_starting) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    step_p_ray(&ray);

    Ray__3i32F20 extension = get_ray_as__extension(&ray, ANGLE__90);

    munit_assert_int32(
            extension.ray_current_vector__3i32F20.x__i32F20,
            ==,
            extension.ray_starting_vector__3i32F20.x__i32F20);
    munit_assert_int32(
            extension.ray_current_vector__3i32F20.y__i32F20,
            ==,
            extension.ray_starting_vector__3i32F20.y__i32F20);
    munit_assert_int32(
            extension.ray_current_vector__3i32F20.z__i32F20,
            ==,
            extension.ray_starting_vector__3i32F20.z__i32F20);

    return MUNIT_OK;
}

TEST_FUNCTION(step_p_ray__advances_current_vector) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    i32F20 old_x = ray.ray_current_vector__3i32F20.x__i32F20;
    i32F20 old_y = ray.ray_current_vector__3i32F20.y__i32F20;

    step_p_ray(&ray);

    bool has_moved =
        (ray.ray_current_vector__3i32F20.x__i32F20 != old_x)
        || (ray.ray_current_vector__3i32F20.y__i32F20 != old_y);

    munit_assert_true(has_moved);

    return MUNIT_OK;
}

TEST_FUNCTION(step_p_ray__does_not_change_starting_vector) {
    Vector__3i32F4 start;
    start.x__i32F4 = 16;
    start.y__i32F4 = 32;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    i32F20 start_x = ray.ray_starting_vector__3i32F20.x__i32F20;
    i32F20 start_y = ray.ray_starting_vector__3i32F20.y__i32F20;
    i32F20 start_z = ray.ray_starting_vector__3i32F20.z__i32F20;

    step_p_ray(&ray);

    munit_assert_int32(ray.ray_starting_vector__3i32F20.x__i32F20, ==, start_x);
    munit_assert_int32(ray.ray_starting_vector__3i32F20.y__i32F20, ==, start_y);
    munit_assert_int32(ray.ray_starting_vector__3i32F20.z__i32F20, ==, start_z);

    return MUNIT_OK;
}

TEST_FUNCTION(step_p_ray__multiple_steps_increase_displacement) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    step_p_ray(&ray);
    Vector__3i32F20 after_one = ray.ray_current_vector__3i32F20;

    step_p_ray(&ray);
    Vector__3i32F20 after_two = ray.ray_current_vector__3i32F20;

    i32F20 disp_one_x = after_one.x__i32F20
        - ray.ray_starting_vector__3i32F20.x__i32F20;
    i32F20 disp_two_x = after_two.x__i32F20
        - ray.ray_starting_vector__3i32F20.x__i32F20;

    i32F20 disp_one_y = after_one.y__i32F20
        - ray.ray_starting_vector__3i32F20.y__i32F20;
    i32F20 disp_two_y = after_two.y__i32F20
        - ray.ray_starting_vector__3i32F20.y__i32F20;

    i32F20 abs_disp_one = (disp_one_x < 0 ? -disp_one_x : disp_one_x)
        + (disp_one_y < 0 ? -disp_one_y : disp_one_y);
    i32F20 abs_disp_two = (disp_two_x < 0 ? -disp_two_x : disp_two_x)
        + (disp_two_y < 0 ? -disp_two_y : disp_two_y);

    munit_assert_true(abs_disp_two > abs_disp_one);

    return MUNIT_OK;
}

TEST_FUNCTION(step_p_ray_until__next_tile__advances_past_tile_boundary) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    Vector__3i32 start_tile = get_ray_endpoint_as__vector_3i32(&ray);

    step_p_ray_until__next_tile(&ray);

    Vector__3i32 end_tile = get_ray_endpoint_as__vector_3i32(&ray);

    bool tile_changed =
        (end_tile.x__i32 != start_tile.x__i32)
        || (end_tile.y__i32 != start_tile.y__i32);

    munit_assert_true(tile_changed);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_endpoint_as__vector_3i32__returns_integer_coords) {
    Vector__3i32F4 start;
    start.x__i32F4 = 5 << 4;
    start.y__i32F4 = 10 << 4;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    Vector__3i32 endpoint = get_ray_endpoint_as__vector_3i32(&ray);

    munit_assert_int32(endpoint.x__i32, ==, 5);
    munit_assert_int32(endpoint.y__i32, ==, 10);
    munit_assert_int32(endpoint.z__i32, ==, 0);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray_endpoint_as__vector_3i32F4__returns_f4_coords) {
    Vector__3i32F4 start;
    start.x__i32F4 = 5 << 4;
    start.y__i32F4 = 10 << 4;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    Vector__3i32F4 endpoint = get_ray_endpoint_as__vector_3i32F4(&ray);

    munit_assert_int32(endpoint.x__i32F4, ==, start.x__i32F4);
    munit_assert_int32(endpoint.y__i32F4, ==, start.y__i32F4);
    munit_assert_int32(endpoint.z__i32F4, ==, start.z__i32F4);

    return MUNIT_OK;
}

TEST_FUNCTION(get_vector__3i32F20_wrt__p_ray_and_its_origin__zero_at_start) {
    Vector__3i32F4 start;
    start.x__i32F4 = 16;
    start.y__i32F4 = 32;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    Vector__3i32F20 displacement =
        get_vector__3i32F20_wrt__p_ray_and_its_origin(&ray);

    munit_assert_int32(displacement.x__i32F20, ==, 0);
    munit_assert_int32(displacement.y__i32F20, ==, 0);
    munit_assert_int32(displacement.z__i32F20, ==, 0);

    return MUNIT_OK;
}

TEST_FUNCTION(get_vector__3i32F20_wrt__p_ray_and_its_origin__nonzero_after_step) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    step_p_ray(&ray);

    Vector__3i32F20 displacement =
        get_vector__3i32F20_wrt__p_ray_and_its_origin(&ray);

    bool has_displacement =
        (displacement.x__i32F20 != 0)
        || (displacement.y__i32F20 != 0);

    munit_assert_true(has_displacement);

    return MUNIT_OK;
}

TEST_FUNCTION(is_p_ray_within__squared_length_i32__true_at_origin) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);

    munit_assert_true(is_p_ray_within__squared_length_i32(&ray, 100));

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__different_angles_produce_different_directions) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray_0 = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    Ray__3i32F20 ray_90 = get_ray(start, ANGLE__90, Ray_Plane_Mode__XY);

    step_p_ray(&ray_0);
    step_p_ray(&ray_90);

    bool different_direction =
        (ray_0.ray_current_vector__3i32F20.x__i32F20
            != ray_90.ray_current_vector__3i32F20.x__i32F20)
        || (ray_0.ray_current_vector__3i32F20.y__i32F20
            != ray_90.ray_current_vector__3i32F20.y__i32F20);

    munit_assert_true(different_direction);

    return MUNIT_OK;
}

TEST_FUNCTION(get_ray__opposite_angles_produce_opposite_displacements) {
    Vector__3i32F4 start;
    start.x__i32F4 = 0;
    start.y__i32F4 = 0;
    start.z__i32F4 = 0;

    Ray__3i32F20 ray_0 = get_ray(start, ANGLE__0, Ray_Plane_Mode__XY);
    Ray__3i32F20 ray_180 = get_ray(start, ANGLE__180, Ray_Plane_Mode__XY);

    step_p_ray(&ray_0);
    step_p_ray(&ray_180);

    Vector__3i32F20 disp_0 =
        get_vector__3i32F20_wrt__p_ray_and_its_origin(&ray_0);
    Vector__3i32F20 disp_180 =
        get_vector__3i32F20_wrt__p_ray_and_its_origin(&ray_180);

    bool x_opposite = (disp_0.x__i32F20 > 0 && disp_180.x__i32F20 < 0)
        || (disp_0.x__i32F20 < 0 && disp_180.x__i32F20 > 0)
        || (disp_0.x__i32F20 == 0 && disp_180.x__i32F20 == 0);
    bool y_opposite = (disp_0.y__i32F20 > 0 && disp_180.y__i32F20 < 0)
        || (disp_0.y__i32F20 < 0 && disp_180.y__i32F20 > 0)
        || (disp_0.y__i32F20 == 0 && disp_180.y__i32F20 == 0);

    munit_assert_true(x_opposite || y_opposite);

    return MUNIT_OK;
}

DEFINE_SUITE(ray,
    INCLUDE_TEST__STATELESS(get_ray__initializes_current_to_starting),
    INCLUDE_TEST__STATELESS(get_ray__stores_angle),
    INCLUDE_TEST__STATELESS(get_ray__stores_plane_mode_xy),
    INCLUDE_TEST__STATELESS(get_ray__stores_plane_mode_xz),
    INCLUDE_TEST__STATELESS(get_ray__stores_plane_mode_yz),
    INCLUDE_TEST__STATELESS(get_ray__out_of_bounds__is_detected_as_out_of_bounds),
    INCLUDE_TEST__STATELESS(get_ray__valid_ray_is_not_out_of_bounds),
    INCLUDE_TEST__STATELESS(get_ray_as__extension__starts_at_source_endpoint),
    INCLUDE_TEST__STATELESS(get_ray_as__extension__inherits_plane_mode),
    INCLUDE_TEST__STATELESS(get_ray_as__extension__stores_new_angle),
    INCLUDE_TEST__STATELESS(get_ray_as__extension__current_equals_starting),
    INCLUDE_TEST__STATELESS(step_p_ray__advances_current_vector),
    INCLUDE_TEST__STATELESS(step_p_ray__does_not_change_starting_vector),
    INCLUDE_TEST__STATELESS(step_p_ray__multiple_steps_increase_displacement),
    INCLUDE_TEST__STATELESS(step_p_ray_until__next_tile__advances_past_tile_boundary),
    INCLUDE_TEST__STATELESS(get_ray_endpoint_as__vector_3i32__returns_integer_coords),
    INCLUDE_TEST__STATELESS(get_ray_endpoint_as__vector_3i32F4__returns_f4_coords),
    INCLUDE_TEST__STATELESS(get_vector__3i32F20_wrt__p_ray_and_its_origin__zero_at_start),
    INCLUDE_TEST__STATELESS(get_vector__3i32F20_wrt__p_ray_and_its_origin__nonzero_after_step),
    INCLUDE_TEST__STATELESS(is_p_ray_within__squared_length_i32__true_at_origin),
    INCLUDE_TEST__STATELESS(get_ray__different_angles_produce_different_directions),
    INCLUDE_TEST__STATELESS(get_ray__opposite_angles_produce_opposite_displacements),
    END_TESTS)
