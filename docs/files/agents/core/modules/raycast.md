# Raycast — Fixed-point ray stepping for ground detection

**Sources:** `core/source/raycast/ray.c` + `core/include/raycast/ray.h`

## Surface Concerns

**L3 SIMULATION module.** The Raycast module provides a fixed-point ray primitive used primarily for ground detection in the collision system. It represents a ray as a 20-fractional-bit (`i32F20`) vector stepped along a direction until it crosses tile boundaries. Called from `poll_hitbox_aabb_for__tile_collision()` in the collisions module. Pure logic — zero `platform.h` includes.

- **Ray representation** — A ray is defined by its starting and current positions (i32F20 for sub-tile precision) and a direction angle (`Degree__u9`). The plane mode selects which two axes the ray moves in: XY, XZ, or YZ. The i32F20 type (20 fractional bits) provides enough precision for tile-scale stepping without floating-point.
- **Stepping mechanics** — Rays advance by pre-computed offsets from the degree lookup table (512 entries, defined in `core/source/degree.c` — see `math.md`). Two stepping variants: `step_p_ray_until__next_tile()` advances until crossing a tile boundary (8-pixel tiles), and `step_p_ray_until__whole_integer()` steps until crossing a whole-integer boundary. Both loop until the coarse position value changes.
- **Ray queries** — Inline helpers provide endpoint conversion (`get_ray_endpoint_as__vector_3i32F4()`), length checks (`is_p_ray_within__squared_length_i32()`), and displacement queries (`get_x/y/z_offset_i32F4_of__ray()`). Used by the tile collision resolver to compute ground Z levels and limit ray range to the hitbox's falling distance.
- **Fixed-capacity/no-allocation** — Rays are stack-allocated structs. No heap allocation, no pools, no capacity limits.
- **Typo in public API** — `is_ray__out_of_bouds()` is misspelled (`bouds` for `bounds`) in the public header; callers must use the misspelled name.

## Public API Surface

### Key Types

**`Ray__3i32F20`** — defined in `defines.h`. A struct (not a pointer):
- `ray_starting_vector__3i32F20` — fixed-point origin (`Vector__3i32F20`)
- `ray_current_vector__3i32F20` — current position along ray (`Vector__3i32F20`)
- `angle_of__ray` — direction as a `Degree__u9`
- `ray_plane_mode` — `Ray_Plane_Mode`: XY, XZ, or YZ

### Key Functions

- `Ray__3i32F20 get_ray(Vector__3i32F4 starting_vector__3i32F4, Degree__u9 angle, Ray_Plane_Mode ray_plane_mode);` — returns a new ray.
- `Ray__3i32F20 get_ray_as__extension(Ray__3i32F20 *p_ray, Degree__u9 angle);` — returns a ray starting at the ray's current position.
- `Ray__3i32F20 get_ray__out_of_bounds(void);` — static inline; returns the out-of-bounds sentinel ray.
- `void step_p_ray(Ray__3i32F20 *p_ray);`
- `void step_p_ray_until__next_whole_integer(Ray__3i32F20 *p_ray);`
- `void step_p_ray_until__next_tile(Ray__3i32F20 *p_ray);`
- `static inline bool is_ray__out_of_bouds(Ray__3i32F20 ray);` — takes the ray by value.
- `Vector__3i32F4 get_ray_endpoint_as__vector_3i32F4(Ray__3i32F20 *p_ray);` / `Vector__3i32 get_ray_endpoint_as__vector_3i32(Ray__3i32F20 *p_ray);`
- `Vector__3i32F20 get_vector__3i32F20_wrt__p_ray_and_its_origin(Ray__3i32F20 *p_ray);` — displacement from the ray's origin.
- `bool is_p_ray_within__squared_length_i32(Ray__3i32F20 *p_ray, i32 length);` / `bool is_p_ray_within__squared_length_i32F4(Ray__3i32F20 *p_ray, i32F4 length);`
- `i32F4 get_x_offset_i32F4_of__ray(Ray__3i32F20 *p_ray);` / `i32F4 get_y_offset_i32F4_of__ray(Ray__3i32F20 *p_ray);` / `i32F4 get_z_offset_i32F4_of__ray(Ray__3i32F20 *p_ray);`
- `i32F20 get_squared_length_i32F20_of__ray(Ray__3i32F20 *p_ray);` / `i32F4 get_squared_length_i32F4_of__ray(Ray__3i32F20 *p_ray);`

## Key Files Table

| File | Role |
|------|------|
| `core/source/raycast/ray.c` | Ray creation, stepping loops, degree table usage |
| `core/include/raycast/ray.h` | Ray API, out-of-bounds sentinel, query helpers (inline) |
