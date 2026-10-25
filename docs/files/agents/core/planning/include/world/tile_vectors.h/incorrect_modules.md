# Planning: tile_vectors.h — Incorrect Modules

**Review source:** `agents/core/review/include/world/tile_vectors.h/incorrect_modules.md`

**Source files reviewed (read-only):**
- `core/include/world/tile_vectors.h`
- `core/include/world/chunk_vectors.h` (reference pattern)
- `core/include/numerics.h` (`ARITHMETIC_R_SHIFT`, `ARITHMETIC_MASK`, `i32F4_to__i32`, `i32F20_to__i32`)
- `core/include/platform_defaults.h` (`TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`, `CHUNK__WIDTH_AND__HEIGHT__BIT_SHIFT`)
- `tests/core/source/world/test_suite_world_tile.c` (no coverage of these functions)

---

## 1. Problem Identification

All six flagged functions live in `tile_vectors.h` and are `static inline`. The
root cause shared by most of them is a **floor-division** defect: the codebase's
`ARITHMETRIC_R_SHIFT(x, n)` performs *truncation toward zero* (`((x)>=0) ? (x)>>n :
-((-(x))>>n)`), which equals `floor` only for non-negative operands. Where a
function must implement `floor(x / 2^k)`, the truncation is either uncorrected or
over-corrected, breaking the **Postcondition** at the negative **Boundary Condition**.

- **`normalize_xyz_i32_to__tile_xyz_i32`** — uses a plain signed `>>`
  (`xyz__i32 >> TILE__WIDTH_AND__HEIGHT__BIT_SHIFT`). Right-shifting a negative
  signed integer is implementation-defined (pre-C23), so the tile index for
  negative coordinates is **Non-portable / not a faithful floor**. It neither uses
  `ARITHMETRIC_R_SHIFT` nor any floor correction.

- **`normalize_i32__to_tile_u8`** — applies the correction term `- (x < 0)`
  unconditionally. This over-corrects for negative *exact multiples* of the tile
  width (8): `ARITHMETRIC_R_SHIFT(-8,3)` is already `floor(-8/8) = -1`, but the
  extra `-1` yields `-2`, so `ARITHMETIC_MASK(-2,7) = 6` instead of the correct
  `7`. Off-by-one at every negative multiple of 8 (−8, −16, −24, …).

- **`normalize_i32F4__to_tile_u8`** — two interacting defects:
  - *Bug 1 (incomplete floor correction):* the small-negative term
    `(x < 0 && -x < BIT(FRACTIONAL_PERCISION_4__BIT_SIZE))` only fires for
    `x ∈ (-16, 0)`, i.e. fixed-point `(-1.0, 0.0)`. Any negative value with a
    non-zero fractional part and integer part ≤ −1 (e.g. −24 = −1.5) is not
    corrected, so `i32F4_to__i32` truncates upward. The correct **Boundary
    Condition** test is `x < 0 && (x & MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)) != 0`.
  - *Bug 2 (inherited):* delegates to the over-correcting `normalize_i32__to_tile_u8`.
  - *Net effect:* the two bugs cancel for most negative fractional inputs, but for
    exact multiples of `8.0` (e.g. x = −128 = −8.0) Bug 1 does not fire and Bug 2
    over-corrects → result 6 instead of 7.

- **`get_tile_x_u8_from__vector_3i32F4`** — correct delegation chain, but inherits
  the `normalize_i32__to_tile_u8` off-by-one through `normalize_i32F4__to_tile_u8`.
  Produces a tile index one low for X positions that are negative multiples of 8
  (e.g. −8.0 → 6 instead of 7). The Y/Z siblings (`get_tile_y/z_u8_from__vector_3i32F4`)
  share the identical defect and must be corrected together even though only X was
  flagged.

- **`normalize_xyz_i32F20_to__tile_xyz_i32`** — two-step pipeline loses floor
  semantics: `i32F20_to__i32` truncates toward zero (destroying the fractional
  part), then the base uses plain `>>`. For negative fractional inputs the result
  is too high by one (e.g. −524288 → 0 instead of −1; −8388609 → −1 instead of −2).
  The small-negative fractional correction is missing entirely.

- **`vector_3i32_to__tile_vector`** — **Mode Confusion / Translation Gap**: the
  parameter is `Vector__3i32F4` (4 fractional bits) but it calls
  `normalize_xyz_i32_to__tile_xyz_i32`, which shifts the *raw* fixed-point value by 3
  without first stripping the 4 fractional bits. The fractional **Surface-form** is
  leaked into the tile index, producing wrong coordinates. It should call
  `normalize_xyz_i32F4_to__tile_xyz_i32` (as its correct sibling
  `vector_3i32F4_to__tile_vector` does). The name/parameter mismatch is a secondary
  readability defect.

## 2. Impact Assessment

All six functions are `static inline`, so their consumers are exactly the
translation units that include `tile_vectors.h`, plus the internal sibling
functions in the same header. The coupling is concentrated inside the header:

**Internal call graph (who depends on the broken behavior):**
- `normalize_xyz_i32_to__tile_xyz_i32` (base) ← called by
  `normalize_xyz_i32F4_to__tile_xyz_i32`, `normalize_xyz_i32F20_to__tile_xyz_i32`,
  and `vector_3i32_to__tile_vector`. Fixing the base's shift propagates to all three.
- `normalize_i32__to_tile_u8` (base) ← called by `normalize_i32F4__to_tile_u8` ←
  called by `get_tile_x/y/z_u8_from__vector_3i32F4` ← called by
  `vector_3i32F4_to__local_tile_vector_3u8`. Fixing the base correction propagates
  to all local-tile-index getters.

**Assumptions invalidated by the fix:**
- The off-by-one for negative multiples of 8 is currently observable output. If any
  caller (or persisted/serialized tile index) was computed using the buggy path for a
  boundary-aligned negative position, correcting the floor changes that value → a
  **State Desync** between world-space positions and their derived tile indices. This
  is the only behavior that changes; non-negative and non-boundary negative inputs are
  already correct and remain unchanged (behavior-preserving for the common case).

**External callers in `./source`:** A survey of `core/source/world/*.c`
(`world.c`, `chunk.c`, `tile.c`, `local_space.c`, `local_space_manager.c`,
`global_space.c`, `region.c`, `region_manager.c`, `camera.c`), plus
`core/source/raycast/ray.c` and `core/source/entity/entity.c`, found **no direct
references** to these functions. The concrete blast radius is therefore confined to
the internal coupling in `tile_vectors.h`; the public entry points
(`get_tile_vector*`, `vector_3i32*__to__tile_vector`, `get_ray_endpoint_as__tile_vector`,
`get_tile_*_u8_from__vector_3i32F4`) are the surfaces an external includer of
`tile_vectors.h` would use. **At implementation time, re-verify** which TUs include
`tile_vectors.h` to confirm no external consumer depends on the buggy boundary output.

**Coupled out-of-scope defect (flag for follow-up, not in this plan):**
The `F20` review cites `chunk_vectors.h::normalize_xyz_i32F4_to__chunk_xyz_i32` as the
correct reference pattern, but that function uses the *same incomplete* small-negative
test `- (x < 0 && -x < BIT(4))` that Bug 1 above proves insufficient. Do **not** copy
that pattern verbatim; apply the complete `x < 0 && (x & MASK(n))` idiom instead and
file a separate review for `chunk_vectors.h`.

## 3. Resolution Assessment

Define one canonical floor-division idiom and apply it consistently. Two independent,
composable corrections (they operate at different levels, so no double-correction):

1. **Integer → tile floor** (base `normalize_i32__to_tile_u8` and base
   `normalize_xyz_i32_to__tile_xyz_i32`):
   ```c
   ARITHMETIC_R_SHIFT(x, k) - (x < 0 && (x & MASK(k)) != 0)
   ```
   Replace plain `>>` with `ARITHMETIC_R_SHIFT` (portable) and gate the correction on a
   non-zero remainder. For `normalize_xyz_i32_to__tile_xyz_i32`, this also removes the
   implementation-defined signed shift.

2. **Fixed-point → integer floor** (the F4/F20 wrappers): convert with a floor, not a
   truncation, by applying the small-negative correction to the *raw fixed-point* value
   before `i32F*_to__i32`:
   ```c
   i32F4_to__i32(x) - (x < 0 && (x & MASK(FRACTIONAL_PERCISION_4__BIT_SIZE)) != 0)
   ```

**Per function:**
- `normalize_xyz_i32_to__tile_xyz_i32` — adopt idiom (1); callers passing integer
  values need no change. Callers: `normalize_xyz_i32F4_to__tile_xyz_i32`,
  `normalize_xyz_i32F20_to__tile_xyz_i32`, `vector_3i32_to__tile_vector` (see below).
- `normalize_i32__to_tile_u8` — replace `- (x < 0)` with idiom (1) using
  `MASK(TILE__WIDTH_AND__HEIGHT__BIT_SHIFT)`. No caller signature change; the
  `normalize_i32F4__to_tile_u8` wrapper and all `get_tile_*_u8` getters inherit the fix.
- `normalize_i32F4__to_tile_u8` — replace the incomplete `-x < BIT(4)` term with idiom (2)
  (`x < 0 && (x & MASK(4)) != 0`). Combined with the fixed base, both counterexamples
  (−128 → 7; −24 → 7) resolve correctly.
- `get_tile_x_u8_from__vector_3i32F4` — no code change required; inherits the fix from
  `normalize_i32F4__to_tile_u8`. Apply the same to the unflagged Y/Z siblings for
  consistency (DRY — they are structurally identical).
- `normalize_xyz_i32F20_to__tile_xyz_i32` — add idiom (2) with `MASK(
  FRACTIONAL_PERCISION_20__BIT_SIZE)` on the raw F20 value before `i32F20_to__i32`, and rely
  on the corrected base for the tile shift. Verify both counterexamples (−524288 → −1;
  −8388609 → −2).
- `vector_3i32_to__tile_vector` — change the three body calls from
  `normalize_xyz_i32_to__tile_xyz_i32` to `normalize_xyz_i32F4_to__tile_xyz_i32` so the
  fractional bits are stripped first (matching `vector_3i32F4_to__tile_vector`). Also
  reconcile the name/parameter mismatch (rename or document that the parameter is F4) to
  close the Translation Gap.

**Related consistency fix (recommended, same file):** `normalize_xyz_i32F4_to__tile_xyz_i32`
has the *same* missing small-negative correction as the F20 wrapper but was not flagged.
Apply idiom (2) to it as well so all three `normalize_xyz_*_to__tile_xyz_i32` variants are
**Faithful** floor functions.

**Callers/tests/docs:** No caller signature changes. Update any documentation that
describes the tile-index mapping to state floor semantics. No phased approach is strictly
required, but sequence the edits base-first (`normalize_xyz_i32_to__tile_xyz_i32`,
`normalize_i32__to_tile_u8`) then wrappers, so intermediate states stay coherent.

## 4. Test Verification Checklist

**Existing coverage:** No test file exercises these functions.
`tests/core/source/world/test_suite_world_tile.c` contains no references to
`tile_vector`, `get_tile_*`, or the `normalize_*__to_tile_*` family, and there is no
dedicated `tile_vectors` test file. The fix currently has **zero** regression coverage.

**New tests required (create a dedicated `test_suite_world_tile_vectors.c`):**
- **Property Based Testing** — assert the floor invariant for randomized inputs:
  `normalize_i32__to_tile_u8(x) == floor(x/8) mod 8` and
  `normalize_xyz_i32_to__tile_xyz_i32(x) == floor(x/8)` across the full signed range,
  with emphasis on negative and boundary values.
- **Equivalence Check** — compare each fixed function against a slow reference floor
  (e.g. integer division with explicit sign handling) to prove behavior preservation.
- **Regression (concrete counterexamples from the review)** — pin the exact cases that
  were wrong: `normalize_i32__to_tile_u8(-8) == 7`, `(-16) == 6`;
  `normalize_i32F4__to_tile_u8(-128) == 7`, `(-24) == 7`;
  `normalize_xyz_i32F20_to__tile_xyz_i32(-524288) == -1`, `(-8388609) == -2`;
  `get_tile_x_u8_from__vector_3i32F4` for x = −128 → 7; `vector_3i32_to__tile_vector`
  for a fractional F4 input.
- **Fuzzing** — target the **Boundary Condition**: negative multiples of 8 and 16,
  `INT32_MIN`/`INT32_MAX`, and values with zero vs. non-zero fractional low bits.
- **Round Trip Check** — `tile_vector_3i32_to__vector_3i32` /
  `tile_vector_3i32_to__vector_3i32F4` inverse the normalized tile vector and confirm the
  reconstructed coordinate lies within the expected tile cell.

**Blast radius of tests:** High for new coverage (net-new test file), Low for existing
coverage (none to update). No phased approach needed; add the whole suite alongside the fix.

## 5. Blast Radius Summary

- **Files changed:** 1 source header (`core/include/world/tile_vectors.h`) + 1 new test
  file. All changed functions are `static inline`, so no ABI/linkage ripple.
- **Behavior-preserving for current callers?** Yes for the common case (non-negative and
  non-boundary negative inputs are unchanged). Only negative *boundary-aligned* inputs
  change, which is the intended correction.
- **De facto contracts invalidated:** Any consumer that captured the off-by-one boundary
  output (or serialized such a tile index) will observe a corrected value — a potential
  **State Desync** to verify at integration time.
- **Phased approach:** Not required, but edit base functions before wrappers.
- **Follow-up (out of scope):** `chunk_vectors.h::normalize_xyz_i32F4_to__chunk_xyz_i32`
  shares the same incomplete small-negative correction; file a separate review.
