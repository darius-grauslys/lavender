#include <world/test_suite_world_camera.h>

#include <world/camera.c>

///
/// Spec:    docs/specs/core/world/camera.h.spec.md
/// Section: 1.4.1 Initialization — initialize_camera_as__inactive
///          1.4.3 State Queries — is_camera__active
///
TEST_FUNCTION(camera__initialize_camera_as__inactive__position_out_of_bounds) {
    Camera camera;
    initialize_camera_as__inactive(&camera);
    munit_assert_false(is_camera__active(&camera));
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/camera.h.spec.md
/// Section: 1.4.1 Initialization — initialize_camera
///          1.3.1 Camera (struct) — width_of__fulcrum, height_of__fulcrum
///
TEST_FUNCTION(camera__initialize_camera__sets_fulcrum) {
    Camera camera;
    Vector__3i32F4 pos;
    pos.x__i32F4 = 0;
    pos.y__i32F4 = 0;
    pos.z__i32F4 = 0;
    initialize_camera(
        &camera,
        pos,
        0,
        256,
        196,
        0,
        0);
    munit_assert_uint32(camera.width_of__fulcrum, ==, 256);
    munit_assert_uint32(camera.height_of__fulcrum, ==, 196);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/camera.h.spec.md
/// Section: 1.4.1 Initialization — initialize_camera
///          1.4.3 State Queries — is_camera__active
///
TEST_FUNCTION(camera__initialize_camera__is_active) {
    Camera camera;
    Vector__3i32F4 pos;
    pos.x__i32F4 = 0;
    pos.y__i32F4 = 0;
    pos.z__i32F4 = 0;
    initialize_camera(
        &camera,
        pos,
        0,
        256,
        196,
        0,
        0);
    munit_assert_true(is_camera__active(&camera));
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/camera.h.spec.md
/// Section: 1.4.4 Follow Target — set_camera_to__follow
///
TEST_FUNCTION(camera__set_camera_to__follow__sets_uuid) {
    Camera camera;
    initialize_camera_as__inactive(&camera);
    set_camera_to__follow(&camera, 42);
    munit_assert_uint32(camera.uuid_of__target__u32, ==, 42);
    return MUNIT_OK;
}

///
/// Spec:    docs/specs/core/world/camera.h.spec.md
/// Section: 1.4.5 Position Accessors — get_position_3i32F4_of__camera
///
TEST_FUNCTION(camera__get_position_3i32F4_of__camera__returns_position) {
    Camera camera;
    Vector__3i32F4 pos;
    pos.x__i32F4 = 100;
    pos.y__i32F4 = 200;
    pos.z__i32F4 = 0;
    initialize_camera(
        &camera,
        pos,
        0,
        256,
        196,
        0,
        0);
    Vector__3i32F4 result = get_position_3i32F4_of__camera(&camera);
    munit_assert_int32(result.x__i32F4, ==, 100);
    munit_assert_int32(result.y__i32F4, ==, 200);
    return MUNIT_OK;
}

DEFINE_SUITE(camera,
    INCLUDE_TEST__STATELESS(camera__initialize_camera_as__inactive__position_out_of_bounds),
    INCLUDE_TEST__STATELESS(camera__initialize_camera__sets_fulcrum),
    INCLUDE_TEST__STATELESS(camera__initialize_camera__is_active),
    INCLUDE_TEST__STATELESS(camera__set_camera_to__follow__sets_uuid),
    INCLUDE_TEST__STATELESS(camera__get_position_3i32F4_of__camera__returns_position),
    END_TESTS)
