# math -- Fixed-point numerics, vectors, angles, random, and timers

**Sources:** `core/source/vectors.c` + `core/include/vectors.h` + `core/source/degree.c` + `core/include/degree.h` + `core/source/random.c` + `core/include/random.h` + `core/include/numerics.h` + `core/include/timer.h` + `core/include/defines.h` + `core/include/defines_weak.h`

## Surface Concerns

The math support layer provides five subsystems used by every module in the engine: fixed-point numerics, 3D vectors, angle math, pseudo-random generation, and countdown timers. Top consumers include rendering, world, game_action, collisions, raycast, entity, inventory, UI, process, client, and multiplayer. The module is a leaf -- zero `platform.h` includes.

- **Fixed-point numerics** — i32F4 (4 fractional bits), i32F8 (8 bits), and i32F20/u32F20 (20 bits) types with conversion, lerp, multiply, add/subtract, clamp, and no-overflow helpers. Left-shift multiplies by 2^n (integer to fixed), right-shift divides by 2^n (fixed to integer), both sign-aware. `multiply__i32F4` is limited to operands in range 0..BIT(12).
- **3D vectors** — Vector types for i32F4, i32F20, i16F8, i32, and u8 with arithmetic, squared-distance computation, format conversion, and 8-way direction offset. Out-of-bounds sentinel is `BIT(31)` in each component. Squared distance is used almost exclusively (avoids sqrt).
- **Angle math** — 9-bit unsigned degrees (0-511, where 512 = 360°). `get_angle_between__vectors_3i32` is a closed-form polynomial arctan approximation (O(1), no lookup); it is accurate for short-range vectors. A 512-entry table of precomputed `Vector__3i32F20` direction offsets backs the angle-to-offset conversions. `add_angles`/`subtract_angles` are inline: subtract wraps at `ANGLE__360`, but add masks with `ANGLE__MASK` (= 31), so it wraps at 45° — an inconsistency, not 360°.
- **Pseudo-random** — `Repeatable_Psuedo_Random` (load-bearing typo) holds `seed__initial` + `seed__current_random`. The intrusive accessor advances the stored seed with pure arithmetic (no `rand()`); the non-intrusive accessor draws from the global `rand()` stream without advancing the object; the XY accessor is deterministic in `(x, y, seed__initial)` despite its "intrusively" name; the direction accessor returns a random 6-bit direction bitmask (`rand() & DIRECTION__ANY`). Embedded in `World`, `Entity`, `Game_Action_Manager`, and other managers.
- **Countdown timers** — u8, u16, and u32 precision timers with poll (returns true when elapsed), reset, loop (repeating interval), and multi-tick progress (u32-only; wraps excess into the next cycle). All inline; `Game` drives its tick timer via `loop_timer_u32`.

## Public API Surface

### Key Types

**i32F4 / i32F8 / i32F20 / u32F20** — fixed-point types defined in `defines.h` (weak fallbacks in `defines_weak.h`). i32F4, i32F8, and i32F20 all use `int32_t` (4/8/20 fractional bits); u32F20 uses `uint32_t`. `i16F8` (`int16_t`) is the only 16-bit variant. Conversion via `i32_to__i32F4(x)` (sign-defined left shift) and `i32F4_to__i32(x)` (sign-aware right shift); F8/F20 follow the same pattern.

**Vector__3i32F4 / Vector__3i32F20 / Vector__3i16F8 / Vector__3i32 / Vector__3u8** — 3D vector structs with x/y/z members, defined in `defines_weak.h`. Literals like `VECTOR__0_0_0` and `VECTOR__OUT_OF_BOUNDS` provided in `vectors.h`.

**Degree__u9** — 9-bit unsigned angle type (`uint16_t`, 0-511) defined in `defines.h`. Constants: `ANGLE__0`, `ANGLE__27_5` (= 32), `ANGLE__45` (= 64), `ANGLE__90` (= 128), `ANGLE__180` (= 256), `ANGLE__270` (= 384), `ANGLE__360` (= 512), `ANGLE__MASK` (= 31), `ANGLE__OUT_OF_BOUNDS` (= 1023).

**Repeatable_Psuedo_Random** — state struct with `seed__initial` and `seed__current_random`, defined in `defines.h` (not `random.h`). Embedded in World (World.repeatable_pseudo_random), Entity, Game_Action_Manager, and other managers.

### Key Functions

**Numerics:**
- `static inline i32F4 i32_to__i32F4(Signed_Index__i32);` / `static inline Signed_Index__i32 i32F4_to__i32(i32F4);` — conversion via sign-aware shifts.
- `static inline i32F4 multiply__i32F4(i32F4, i32F4);` — (x * y) >> 4, limited to operands 0..BIT(12).
- `static inline i32F4 lerp__i32F4(i32F4, i32F4, i32F4);` / `static inline i32F4 lerp__xy__i32F4(...);` — linear interpolation.
- `static inline bool add_u32__no_overflow(u32, u32, u32 *);` — returns true on overflow (result via out-param).
- `static inline u32 subtract_u32__no_overflow(u32, u32);` — returns the clamped difference (0 on underflow).
- `static inline i32 clamp__i32(i32, i32, i32);` — clamp helper.

**Vectors:**
- `static inline Vector__3i32F4 add_vectors__3i32F4(Vector__3i32F4, Vector__3i32F4);`
- `static inline Vector__3i32F4 subtract_vectors__3i32F4(Vector__3i32F4, Vector__3i32F4);`
- `static inline i32F4 get_distance_squared_of__vector_3i32F4(Vector__3i32F4);`
- `static inline bool get_distance_squared_of__vector_3i32__no_overflow(Vector__3i32, u32*);` — u32 out-param (mislabeled `u64` in the name); true on overflow.
- `static inline Vector__3i32 vector_3i32F4_to__vector_3i32(Vector__3i32F4);` — truncates fractional part.
- `void offset_vector_by__direction(Vector__3i32F4*, Direction__u8);` — 8-way offset (4 cardinal + 4 diagonal); other direction bitmasks are a no-op.

**Angles:**
- `Direction__u8 get_direction_from__angle(Degree__u9);` / `Degree__u9 get_angle_from__direction(Direction__u8);` — bidirectional conversion.
- `Vector__3i32F4 get_2i32F4_offset_from__angle(Degree__u9);` — direction offset from angle via lookup table (not very accurate beyond ~10 integer units).
- `Vector__3i32F20 get_2i32F20_offset_from__angle(Degree__u9);` — higher-precision F20 variant.
- `Degree__u9 get_angle_between__vectors_3i32(Vector__3i32, Vector__3i32);` — closed-form arctan approximation; accurate for short-range vectors.
- `static inline Degree__u9 add_angles(Degree__u9, Degree__u9);` — wraps via `ANGLE__MASK` (45°), unlike subtract.
- `static inline Degree__u9 subtract_angles(Degree__u9, Degree__u9);` — wraps at `ANGLE__360`.
- `bool is_degree_u9__out_of_bounds(Degree__u9);` — true when `>= ANGLE__OUT_OF_BOUNDS`.

**Random:**
- `void initialize_repeatable_psuedo_random(Repeatable_Psuedo_Random*, Psuedo_Random_Seed__u32);` — sets initial and current seed.
- `Psuedo_Random__i32 get_pseudo_random_i32__intrusively(Repeatable_Psuedo_Random*);` — advances stored seed.
- `Psuedo_Random__i32 get_pseudo_random_i32__non_intrusively(Repeatable_Psuedo_Random*);` — global `rand()` stream; does not advance the object.
- `Psuedo_Random__i32 get_pseudo_random_i32_with__xy__intrusively(Repeatable_Psuedo_Random*, Signed_Index__i32, Signed_Index__i32);` — deterministic in (x, y, seed__initial); never touches the seed despite the name.
- `Psuedo_Random__i32 get_pseudo_random_i32__non_intrusively_with__seed(Repeatable_Psuedo_Random*, i32 seed);` — deterministic from the given seed.
- `u8 get_psuedo_random__direction_u8__non_intrusively_with__seed(Repeatable_Psuedo_Random*, i32 seed);` — random direction bitmask (`rand() & DIRECTION__ANY`).

**Timers (all static inline in timer.h):**
- `void initialize_timer_u32(Timer__u32*, Quantity__u32);` / `void reset_timer_u32(Timer__u32*);`
- `bool poll_timer_u32(Timer__u32*);` — returns true when elapsed.
- `void loop_timer_u32(Timer__u32*);` — auto-reset on elapsed, repeating interval.
- `bool progress_timer__u32(Timer__u32*, Quantity__u32);` — advance by variable ticks (u32-only), returns true if full cycle elapsed.

## Key Files Table

| File | Role |
|------|------|
| `core/source/vectors.c` | `offset_vector_by__direction` (only non-inline vector helper) |
| `core/include/vectors.h` | Vector literals, arithmetic, distance, conversion, comparison (all inline) |
| `core/source/degree.c` | 512-entry direction-offset lookup table, angle-to-direction, closed-form angle-between-vectors |
| `core/include/degree.h` | Angle function declarations + inline add/subtract/out-of-bounds (constants live in `defines.h`) |
| `core/source/random.c` | Seed arithmetic + `srand`/`rand` wrappers, XY and direction variants |
| `core/include/random.h` | Function declarations (the `Repeatable_Psuedo_Random` type lives in `defines.h`) |
| `core/include/numerics.h` | Fixed-point conversion, lerp, multiply, clamping, overflow helpers |
| `core/include/timer.h` | Countdown timers for u8/u16/u32; multi-tick progress is u32-only |
