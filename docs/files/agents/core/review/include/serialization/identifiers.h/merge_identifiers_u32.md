merge_identifiers_u32 — core/include/serialization/identifiers.h

Merges two 32-bit identifiers by taking the top `bits__left` bits from `identifier__left_half` and the bottom `(32 - bits__left)` bits from `identifier__right_half`.

Pre-conditions:
1. `identifier__left_half` is any `Identifier__u32` (uint32_t); no null or range constraint.
2. `bits__left` is a `Quantity__u8` (uint8_t) representing the number of high-order bits to preserve from the left half. Must be in the range [1, 32] to avoid undefined behavior. A value of 0 causes `MASK(32)` which is UB (shifting a 32-bit value by 32).
3. `identifier__right_half` is any `Identifier__u32` (uint32_t); no null or range constraint.

Post-conditions:
1. Returns an `Identifier__u32` whose high-order bits come from `identifier__left_half` and whose low-order bits come from `identifier__right_half`.
2. The returned value is a pure computation; no input parameters are mutated.

Correctness Verdict: Incorrect

Semantic Alignment:
The function's intent is to take the top `bits__left` bits from the left half and the bottom `(32 - bits__left)` bits from the right half. However, the implementation uses `33 - bits__left` instead of `32 - bits__left`, introducing an off-by-one error. This causes:
- The left half to retain `(bits__left - 1)` bits instead of `bits__left` bits.
- The right half to contribute `(33 - bits__left)` bits instead of `(32 - bits__left)` bits.

For example, when `bits__left = 26` (corresponding to the UUID type branding bit shift at bit 26):
- Buggy: `MASK(33 - 26)` = `MASK(7)` = bits 0–6 (7 bits); left keeps bits 7–31 (25 bits); right contributes bits 0–6 (7 bits).
- Correct: `MASK(32 - 26)` = `MASK(6)` = bits 0–5 (6 bits); left keeps bits 6–31 (26 bits); right contributes bits 0–5 (6 bits).

The buggy version incorrectly shifts the boundary by one bit, causing bit 6 to be sourced from the right half instead of the left half. This is a semantic drift from the intended behavior.

Implementation Correctness:
Type compatibility — `bits__left` is `Quantity__u8` (uint8_t); in the expression `33 - bits__left`, it undergoes integer promotion to `int`, which is then used as the shift amount in `MASK(n)` = `((u32)BIT(n) - 1)` = `((u32)(1U << n) - 1)`. The types are compatible with no truncation. However, there is a potential undefined behavior issue: when `bits__left` is 0 or 1, the shift amount becomes 33 or 32 respectively, both of which exceed the 32-bit width of `u32`/`unsigned int`, resulting in undefined behavior. Even with the correct constant `32`, `bits__left = 0` would produce `MASK(32)` = `(1U << 32) - 1`, which is also UB.
No pointer arithmetic, no null dereference, no type punning, no out-of-bounds array access.
No input validation is performed. For a low-level bit manipulation utility, this is acceptable as the caller is responsible for providing a valid `bits__left` value. However, the off-by-one constant is a logic bug, not a validation issue.

Side Effects:
No side effects. This is a pure function — it computes and returns a new `Identifier__u32` value from its inputs without modifying any state or memory.
