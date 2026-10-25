PLATFORM_render_entity — core/include/platform.h

Renders an entity's platform sprite to the screen at a camera-relative position; culls the sprite (and hides the entity) when it falls outside the camera's visible region, and flips it horizontally when the entity faces west. On a fixed-position entity it pins the sprite to the screen center.

Pre-conditions:
1. `entity` must be a non-null pointer to a valid, allocated Entity.
2. `game` must be a non-null pointer to a valid Game (it is only used to obtain the active Camera).
3. For a real (rendering) implementation, the entity must carry a platform sprite wrapper with a populated `p_sprite`; the function is a no-op when the entity is flagged as not updating graphics.
4. The caller is responsible for ensuring `entity` and `game` are valid; the function performs no null checks (acceptable for a low-level PLATFORM render primitive).

Post-conditions:
1) Returns void; no return value.
2) If graphics updating is disabled on the entity: no state is mutated (early return), no side effects.
3) If position updating is disabled: the platform sprite is repositioned to the fixed location (127-8, 96-8) via `NDS_set_position_of__PLATFORM_sprite`.
4) Otherwise: the sprite is positioned relative to the camera; if it lies outside the cull margin (CAMERA_FULCRUM_WIDTH/2 + 16 horizontally, CAMERA_FULCRUM_HEIGHT/2 + 16 vertically) the entity is marked hidden and the sprite hidden, else the entity is marked visible and the sprite unhidden, then placed at `(x_global - x_origin + 127 - 8, -(y_global - y_origin - 96 + 8))`.
5) The sprite's flip is set based on whether the entity direction contains DIRECTION__WEST.

Correctness Verdict: Incorrect

Semantic Alignment:
The intended semantics — camera-relative sprite placement, off-screen culling, directional flip, and a fixed-position fallback — are coherent and match the structure of the NDS reference implementation. However, that reference implementation is not realizable against the current codebase (see Implementation Correctness), so the documented semantic intent cannot actually be fulfilled.

Implementation Correctness:
- The header declaration is well-formed and matches the test/template stub signatures (`void PLATFORM_render_entity(Entity *entity, Game *game)`).
- The canonical reference implementation in `nds/source/rendering/nds_entity.c` is structurally broken against the current core headers:
  * It reads `p_entity->sprite_wrapper.p_sprite` and `p_entity->sprite_wrapper.direction`, but the current `Entity` struct (`core/include/defines.h`, struct Entity_t, lines 1127-1134) contains only `_serialization_header`, `entity_data`, and `entity_functions` — there is NO `sprite_wrapper` field, so these accesses will not compile.
  * It calls helpers that are not declared or defined anywhere in the codebase: `is_entity_not__updating_graphics`, `is_entity_not__updating_position`, `set_entity_as__hidden`, `set_entity_as__visible`, `get_p_camera_from__game`, `get_x_i32_from__entity`, `get_y_i32_from__entity`.
  * It `#include`s `<rendering/render_entity.h>`, a file that does not exist anywhere in the repository, so the translation unit cannot resolve its includes.
  * This staleness is signalled by the `// TODO: remove` comment on the declaration (platform.h line 76) and on each implementation site.
- The arithmetic once pointers are valid is type-consistent (`int32_t` with `abs()`, `Quantity__u32`/`bool` arguments to the `NDS_set_*` inline helpers in `nds/include/rendering/nds_sprite.h`). No off-by-one or UB is introduced by the math itself; the defect is undefined symbols / structural mismatch.
- The test/template stubs (`tests/core/source/PLATFORM.c:188`, `tests/templates/source/PLATFORM.c:188`) are empty bodies `{}` — they compile and trivially satisfy the contract by doing nothing, but they do not fulfill the rendering semantic.
- No validation is needed beyond caller-supplied validity, consistent with the codebase's low-level PLATFORM conventions.

Side Effects:
- Real (NDS) implementation: mutates the platform sprite (position, hidden state, flip) and mutates the entity's hidden/visible flag via `set_entity_as__hidden`/`set_entity_as__visible`; none of this happens when graphics updating is disabled (early return).
- Test/template stubs: no side effects (empty body).
- Does not touch any state outside the entity and its sprite; return is void.
