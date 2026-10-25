get_ray__out_of_bounds — core/include/raycast/ray.h

Returns a Ray__3i32F20 struct initialized with sentinel "out-of-bounds" values for its vector and angle fields, so that is_ray__out_of_bouds() will return true for the result.

Pre-conditions:
1. None. The function takes no parameters and performs no validation.

Post-conditions:
1. ray_starting_vector__3i32F20 is set to VECTOR__3i32F20__OUT_OF_BOUNDS (all components set to BIT(31), i.e., INT32_MIN when stored in i32F20 fields).
2. ray_current_vector__3i32F20 is set to VECTOR__3i32F20__OUT_OF_BOUNDS.
3. angle_of__ray (10-bit bit-field of type Degree__u9) is set to ANGLE__OUT_OF_BOUNDS (MASK(10) = 1023, the maximum value representable in 10 bits).
4. ray_plane_mode (2-bit bit-field of type Ray_Plane_Mode) is zero-initialized to Ray_Plane_Mode__XY (0). In C, struct members not explicitly named in a compound literal initializer are implicitly zero-initialized.
5. The returned ray satisfies is_ray__out_of_bouds(): is_vectors_3i32F20__out_of_bounds(ray_current_vector__3i32F20) returns true (all components match the sentinel), and is_degree_u9__out_of_bounds(angle_of__ray) returns true (1023 >= 1023).

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the semantic intent of producing an out-of-bounds ray. The Ray__3i32F20 struct has 4 fields (ray_starting_vector__3i32F20, ray_current_vector__3i32F20, angle_of__ray, ray_plane_mode), and the compound literal explicitly assigns 3 of them. The 4th field (ray_plane_mode) is implicitly zero-initialized to Ray_Plane_Mode__XY (0), which is valid C behavior. Since is_ray__out_of_bouds() only checks ray_current_vector__3i32F20 and angle_of__ray for out-of-bounds status, the zero-initialized ray_plane_mode does not affect detection. There is no out-of-bounds sentinel value defined for Ray_Plane_Mode (the enum only defines XY=0, XZ=1, YZ=2), so zero-initialization to XY is the most reasonable default.

Implementation Correctness:
- Type compatibility: VECTOR__3i32F20__OUT_OF_BOUNDS is (const Vector__3i32F20) VECTOR__OUT_OF_BOUNDS, which matches the Vector__3i32F20 field type exactly. The const qualifier is harmless in a compound literal initializer. ANGLE__OUT_OF_BOUNDS is MASK(10) = 1023 (u32), assigned to angle_of__ray (Degree__u9 = uint16_t, 10-bit width). The value 1023 fits exactly in 10 bits, so no truncation occurs. There is an implicit narrowing conversion from u32 to uint16_t, but since the value fits, this is safe and not undefined behavior.
- Undefined behavior: None. No pointer arithmetic, no null dereference, no type punning, no out-of-bounds access. The function operates entirely on stack-allocated struct values.
- Validation: Not needed — this is a zero-argument factory function with no parameters to validate.

Side Effects:
No side effects. The function constructs and returns a Ray__3i32F20 struct by value. No memory is allocated, no global state is modified, and no I/O occurs.