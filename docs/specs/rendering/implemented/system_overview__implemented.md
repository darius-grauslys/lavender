# System Overview: Implemented (Template) Headers

## Purpose

The `implemented/` directory contains **template headers** that declare
game-specific registration functions. These files are part of the engine
core source tree but are designed to be **copied** to each game project by
the `lav_new_project` script. The game developer then modifies the copies
to register their project's textures and animations. The originals in core
serve as defaults/templates.

## Architecture

### Template Distribution Model

    Engine Core
    +-- core/include/rendering/implemented/
    |   +-- aliased_texture_registrar.h   (template)
    |   +-- sprite_animation_registrar.h  (template)
    |
    lav_new_project (script)
    |   -> Copies templates to game project's implemented/ directory
    |
    Game Project
    +-- <project>/include/rendering/implemented/
        +-- aliased_texture_registrar.h   (game-specific copy)
        +-- sprite_animation_registrar.h  (game-specific copy)

### Include Path Strategy

The `implemented/` directory is **NOT** in the core include path. It is only
in the game project's include path. This ensures that when the engine
includes `rendering/implemented/aliased_texture_registrar.h`, it resolves
to the game project's copy rather than the core template.

### Registration Functions

| File | Function | Signature | Called During |
|------|----------|-----------|--------------|
| `aliased_texture_registrar.h` | `register_aliased_textures` | `(Aliased_Texture_Manager*, Game*) -> void` | Game initialization |
| `sprite_animation_registrar.h` | `register_sprite_animations` | `(Sprite_Manager*) -> void` | Game initialization |

## Registration Function Details

### register_aliased_textures

Registers all game-specific named textures into the `Aliased_Texture_Manager`.
The game developer implements this function to call
`allocate_texture_with__alias` or `load_texture_from__path_with__alias` for
each texture the game needs.

**Typical implementation pattern:**

    void register_aliased_textures(
            Aliased_Texture_Manager *p_aliased_texture_manager,
            Game *p_game) {
        Texture texture;

        // Allocate a blank texture with an alias
        allocate_texture_with__alias(
            p_PLATFORM_gfx_context,
            p_PLATFORM_gfx_window,
            p_aliased_texture_manager,
            "my_texture",
            TEXTURE_FLAGS(...),
            &texture);

        // Load a texture from file with an alias
        load_texture_from__path_with__alias(
            p_PLATFORM_gfx_context,
            p_PLATFORM_gfx_window,
            p_aliased_texture_manager,
            "my_sprite_sheet",
            TEXTURE_FLAGS(...),
            "assets/sprites.png",
            &texture);
    }

**Ownership:** The `Aliased_Texture_Manager` owns all registered textures.
The caller does not retain ownership of the `Texture` values.

**Error convention:** Both `allocate_texture_with__alias` and
`load_texture_from__path_with__alias` return `true` on **failure** and
`false` on success (inverted bool convention).

### register_sprite_animations

Registers all game-specific sprite animation definitions. The game developer
implements this function to call `register_sprite_animation_into__sprite_context`
for each animation the game defines.

**Typical implementation pattern:**

    void register_sprite_animations(
            Sprite_Manager *p_sprite_manager) {
        register_sprite_animation_into__sprite_context(
            p_sprite_context,
            Sprite_Animation_Kind__MyAnimation,
            (Sprite_Animation){
                .the_kind_of_animation__this_sprite_has =
                    Sprite_Animation_Kind__MyAnimation,
                .sprite_animation__initial_frame__u8 = 0,
                .sprite_animation__quantity_of__frames__u8 = 4,
                .sprite_animation__ticks_per__frame__u5 = 8,
                .sprite_animation__flags__u3 = 0
            });
    }

**Note:** Despite the parameter being named `p_sprite_manager`, the actual
registration target is the `Sprite_Context`. This signature may be updated
in a future refactor.

## Lifecycle Integration

### Initialization Sequence

The registration functions are called during game initialization, after the
core rendering subsystems have been initialized:

    1. initialize_gfx_context(&gfx_context)
       -> Initializes all subsystem managers

    2. PLATFORM_initialize_gfx_context(...)
       -> Platform-specific setup

    3. register_aliased_textures(
           &gfx_context.aliased_texture_manager, p_game)
       -> Game-specific texture registration

    4. register_sprite_animations(p_sprite_manager)
       -> Game-specific animation registration

### Dependencies

| Function | Requires Before Call |
|----------|---------------------|
| `register_aliased_textures` | `Aliased_Texture_Manager` initialized, `PLATFORM_Gfx_Context` available |
| `register_sprite_animations` | `Sprite_Context` initialized |

## Relationship to Rendering Subsystems

| Registration Function | Target Subsystem | API Used |
|-----------------------|------------------|----------|
| `register_aliased_textures` | `Aliased_Texture_Manager` | `allocate_texture_with__alias`, `load_texture_from__path_with__alias` |
| `register_sprite_animations` | `Sprite_Context` | `register_sprite_animation_into__sprite_context` |

The registered textures become available for runtime lookup via
`get_texture_by__alias` and `get_texture_by__uuid`. The registered
animations become available for application to sprites via
`set_sprite_animation`.

## Header Guards

| File | Guard |
|------|-------|
| `aliased_texture_registrar.h` | `ALIAS_TEXTURE_REGISTRAR_H` |
| `sprite_animation_registrar.h` | `SPRITE_ANIMATION_REGISTRAR_H` |
