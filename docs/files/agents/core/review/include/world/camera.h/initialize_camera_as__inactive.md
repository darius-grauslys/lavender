initialize_camera_as__inactive — core/include/world/camera.h

Resets a Camera struct to an inactive/default state by delegating to initialize_camera with sentinel values (out-of-bounds position, unknown fulcrum dimensions, zero z-near/z-far) so that is_camera__active() returns false.

Pre-conditions:
1. p_camera must be a non-null pointer to a writable Camera struct.

Post-conditions:
1. p_camera->position is set to VECTOR__3i32F4__OUT_OF_BOUNDS.
2. p_camera->m_camera_handler is set to m_camera_handler__default (the 0 passed is a null pointer constant, which initialize_camera replaces with the default no-op handler via its ternary).
3. p_camera->width_of__fulcrum is set to QUANTITY__UNKNOWN__u32.
4. p_camera->height_of__fulcrum is set to QUANTITY__UNKNOWN__u32.
5. p_camera->z_near is set to 0.
6. p_camera->z_far is set to 0.
7. After return, is_camera__active(p_camera) evaluates to false because: position is out-of-bounds, fulcrum dimensions are unknown, and z_near (0) is not less than z_far (0).

Correctness Verdict: Correct

Semantic Alignment:
This is Lavender-style initialization (pool cleanup / struct reset), NOT RAII. No resources are acquired; the struct is cleaned to default/invalid sentinel values so it can be returned to a free pool.

The function correctly achieves its intent: after calling initialize_camera_as__inactive, is_camera__active returns false. The sentinel values chosen for each field cause the corresponding checks in is_camera__active to fail, guaranteeing the camera is considered inactive.

However, one field is not initialized: uuid_of__target__u32. The Camera struct (defined in defines.h) has 7 fields, but initialize_camera (the callee) only assigns 6 — uuid_of__target__u32 is omitted. This field is only read by m_camera_handler__follow__default (which runs only when the camera is in follow mode), and is explicitly set by set_camera_to__follow when transitioning to follow mode. In practice, a stale uuid_of__target__u32 value will not cause incorrect behavior because it is never read while the camera is inactive. Nevertheless, for full pool-safety semantics, this field should be reset.

Implementation Correctness:
Type compatibility — all argument types match the initialize_camera parameter types exactly:
- VECTOR__3i32F4__OUT_OF_BOUNDS is (const Vector__3i32F4) VECTOR__OUT_OF_BOUNDS, matching Vector__3i32F4.
- 0 is a valid null pointer constant for m_Camera_Handler (a function pointer type).
- QUANTITY__UNKNOWN__u32 is (uint32_t)(-1), matching Quantity__u32.
- 0 matches i32F20.
No implicit conversions or truncation.

Undefined behavior — none. No pointer arithmetic, no null dereference (p_camera is dereferenced by initialize_camera, but that is the callee's responsibility), no type punning, no out-of-bounds access.

Validation — no validation is performed in this function, which is appropriate for a low-level struct initializer. The caller must ensure p_camera is non-null.

Side Effects:
Mutates the Camera struct pointed to by p_camera: position, m_camera_handler, width_of__fulcrum, height_of__fulcrum, z_near, and z_far are all overwritten. The uuid_of__target__u32 field is left unchanged (not overwritten by initialize_camera). No other memory or I/O side effects.
