m_entity_dispose_handler__default — core/source/entity/entity.c

Default dispose handler for an Entity: releases the entity's registered Sprite and Hitbox_AABB back to their respective managers.

Pre-conditions:
1. p_this_entity must be a non-null pointer to a valid Entity whose Serialization_Header.uuid is read via GET_UUID_P to locate the sprite.
2. p_game must be a non-null pointer to a valid Game providing both a gfx context and a hitbox context.
3. p_world must be a non-null pointer to a valid World that has an associated Graphics_Window (used to reach the sprite manager) and whose uuid identifies a registered hitbox manager within the game's hitbox context (the hitbox manager lookup mirrors the GET_UUID_P(p_world) convention used in game_action__hitbox__aabb.h).
4. All three parameters are dereferenced unconditionally; none may be NULL. (Per Lavender semantics this is a cleanup/dispose path that returns struct members to pools — it is not RAII-style resource setup.)

Post-conditions:
1. If the entity had a Sprite registered in the sprite manager (looked up by the entity's uuid), that Sprite has been released back to the sprite manager via release_sprite_from__sprite_manager.
2. If a Hitbox_AABB was associated with the entity in the world's hitbox AABB manager (looked up by the entity's uuid via the inline get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager), that Hitbox_AABB has been released back to the manager via release_hitbox_aabb_from__hitbox_aabb_manager.
3. The pointed-to Entity is not itself mutated; only manager-internal free pools are updated.
4. The function returns void.

Correctness Verdict: Correct

Semantic Alignment:
The implementation fulfills the dispose intent: both the entity's sprite and its hitbox AABB are released. The sprite path correctly looks up the sprite by the entity's uuid and guards the release with `if (p_sprite)`. The hitbox path correctly resolves the world's hitbox manager via GET_UUID_P(p_world) (matching the convention in game_action__hitbox__aabb.h) and the entity's hitbox by the entity's uuid (the inline helper itself uses GET_UUID_P(p_entity)), guarding the release with `if (p_hitbox_aabb)`. No sprite or hitbox record/member is omitted and no fields are reordered.

Implementation Correctness:
Type compatibility — GET_UUID_P(p_this_entity) and GET_UUID_P(p_world) yield an Identifier__u32 (the `uuid` field of Serialization_Header, defines.h:231), which exactly matches the Identifier__u32 parameters of get_p_sprite_by__uuid_from__sprite_manager and get_pV_hitbox_manager_from__hitbox_context respectively. The (Hitbox_AABB_Manager*) cast on the void* polymorphic return of get_pV_hitbox_manager_from__hitbox_context is legitimate and consistent with game_action__hitbox__aabb.h:27. release_sprite_from__sprite_manager's Gfx_Context* first argument is satisfied by get_p_gfx_context_from__game(p_game). No implicit conversions or truncation occur.
Undefined behavior — No pointer arithmetic, no type punning, no broken aliasing, no out-of-bounds access; all manager handles are obtained via established accessor chains. CAVEAT: the null guard on p_hitbox_aabb_manager is wrapped in #ifndef NDEBUG, so in release builds a missing hitbox manager leads to dereferencing NULL inside get_p_hitbox_aabb_by__entity_from__hitbox_aabb_manager. This matches the codebase's defensive-debug pattern (also used in the sibling m_entity_enable_handler__default and get_p_sprite_manager_from__graphics_window); it is acceptable when the pre-condition (world has a registered hitbox manager) holds, but is a latent release-build null-dereference risk to be aware of.
Validation — Validation is appropriately minimal and consistent with the codebase: sprite/hitbox AABB presence is checked at runtime (`if (p_sprite)` / `if (p_hitbox_aabb)`), while manager existence is a debug-only assertion. The caller is responsible for ensuring p_this_entity, p_game, and p_world are valid; per the Lavender model this handler performs cleanup (release to pools), not resource setup, so no RAII-style initialization semantics are expected.

Side Effects:
Mutates manager-internal free pools: the entity's Sprite is returned to the sprite manager (release_sprite_from__sprite_manager), which may free associated graphics/GPU resources, and — if present — the entity's Hitbox_AABB is returned to the hitbox AABB manager (release_hitbox_aabb_from__hitbox_aabb_manager), invalidating that hitbox record. The Entity pointed to by p_this_entity is not itself modified. In debug builds, a debug_error message is emitted only if the world's hitbox manager is absent (followed by an early return).
