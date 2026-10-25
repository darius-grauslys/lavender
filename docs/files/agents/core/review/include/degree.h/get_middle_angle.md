get_middle_angle — core/source/degree.c

Computes the midpoint of two angle values by averaging them, conditionally adding a full rotation (ANGLE__360 = 512) when degree__one >= degree__two.

Pre-conditions:
1. `degree__one` and `degree__two` should be valid angles in the range [0, 511] (the Degree__u9 domain). No validation is performed; this is the caller's responsibility, consistent with the codebase convention (cf. add_angles, subtract_angles).
2. Inputs are typed as `i32F20` (int32_t) but represent plain integer degree values. The function performs integer arithmetic (addition and right-shift), ignoring any fixed-point fractional component.
3. The function currently has no callers in the codebase.

Post-conditions:
1. Returns a `Degree__u9` value intended as the midpoint of the two inputs.
2. The result is NOT masked to [0, 511]. In certain inputs (e.g., degree__one == degree__two == 256) the return value is 512, which equals ANGLE__360 and is outside the valid angle range.
3. No state is mutated; the function does not modify any external objects.

Correctness Verdict: Incorrect

Semantic Alignment:
The function does not reliably compute the standard "middle angle" (midpoint of the shorter arc). The branch condition `degree__one < degree__two` controls whether the wrap-around offset is applied, but the value ordering does not indicate whether the shorter arc between the two angles crosses the 0/360 boundary. The correct condition requires comparing the angular distance to half the circle (256 units). Concrete failures under the shorter-arc interpretation:
- degree__one == degree__two: the else-branch always executes, returning degree__one + 256 instead of degree__one.
- degree__one=200, degree__two=100: angular distance is 100 (< 256, no wrap), but the function returns (200+100+512)>>1 = 406 instead of 150.
- degree__one=10, degree__two=400: angular distance is 390 (> 256, wrap needed), but the function returns (10+400)>>1 = 205 instead of 461.

The branch logic is only correct if the intended semantic is "midpoint of the forward (clockwise) arc from degree__one to degree__two," but no documentation or caller confirms this intent. Given the function name and the absence of any documentation, the standard interpretation (shorter arc) is not fulfilled.

Implementation Correctness:
Type compatibility — parameters are `i32F20` (int32_t) and the return type is `Degree__u9` (uint16_t). The expression `(degree__one + degree__two + ANGLE__360) >> 1` is evaluated in int32_t. The maximum possible result is (511+511+512)>>1 = 767, which fits in uint16_t without truncation. However, using `i32F20` (a fixed-point type) for integer degree values is a semantic mismatch; the function performs integer arithmetic, not fixed-point arithmetic.
Undefined behavior — none under valid inputs. All angle values are in [0, 511], so sums are in [0, 1536], all non-negative, making `>> 1` well-defined (no implementation-defined shift on negative operands). If a caller passes negative values, `>> 1` on a signed int32_t would be implementation-defined, but the function provides no validation.
Validation — no input validation is performed, consistent with the codebase convention where callers ensure valid inputs. However, the output is not masked to the valid angle range, which is an omission. Other modular functions such as add_angles apply a masking operation (using ANGLE__MASK, though that constant itself appears misconfigured as MASK(5)=31 rather than MASK(9)=511).

Side Effects:
No side effects. The function is pure — it reads only its parameters and returns a computed value.
